from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.db.models import Q, Sum, Prefetch
from django.http import HttpResponse, HttpResponseRedirect
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.views.generic import (CreateView, DetailView, ListView, UpdateView,
                                  RedirectView, DeleteView, FormView)
from django.views.generic.edit import FormMixin
from django.views.generic.detail import SingleObjectMixin
from django.urls import reverse
from django.core.paginator import Paginator
from django.utils.functional import cached_property

from braces.views import MessageMixin

from stats.utils import log_event
from accounts.mixins import ContributorRequiredMixin
from programs.models import Program
from alerts.forms import AlertForm
from stats.models import Event
from categories.models import Category
from aids.tasks import log_admins
from aids.forms import (AidEditForm, AidAmendForm, AidSearchForm,
                        AdvancedAidFilterForm)
from aids.models import Aid, AidWorkflow


class SearchMixin:
    def get_form_kwargs(self):
        """Take input data from the GET values."""

        kwargs = super().get_form_kwargs()
        kwargs.update({
            'data': self.request.GET,
        })

        return kwargs


class AidPaginator(Paginator):
    """Custom paginator for aids.

    The default django paginator uses COUNT(*) for counting results, which
    takes up a lot of memory and results in terrible performances.
    """

    @cached_property
    def count(self):
        return self.object_list.values('id').order_by('id').count()


class SearchView(SearchMixin, FormMixin, ListView):
    """Search and display aids."""

    template_name = 'aids/search.html'
    context_object_name = 'aids'
    form_class = AidSearchForm
    paginate_by = 18
    paginator_class = AidPaginator

    def get(self, request, *args, **kwargs):
        self.form = self.get_form()
        self.form.full_clean()
        self.store_current_search()
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        """Return the list of results to display."""

        qs = Aid.objects \
            .published() \
            .open() \
            .select_related('perimeter', 'author') \
            .prefetch_related('financers', 'instructors')

        filter_form = self.form
        results = filter_form.filter_queryset(qs)
        ordered_results = filter_form.order_queryset(results).distinct()
        return ordered_results

    def get_programs(self):
        """Get the aid programs that matched the search perimeter.

        We consider that there is a match in one of the two cases:

         - the searched perimeter exactly matches some program's perimeter;
         - the searched perimeter is contained in some program's perimeter.
        """

        searched_perimeter = self.form.cleaned_data.get('perimeter', None)
        if not searched_perimeter:
            return []

        q_exact_match = Q(perimeter=searched_perimeter)
        q_container_match = Q(
            perimeter__in=searched_perimeter.contained_in.all())
        programs = Program.objects \
            .filter(q_exact_match | q_container_match)
        return programs

    def store_current_search(self):
        """Store the current search query in a cookie.

        This is needed to provide the correct "go back to your search" link in
        other pages' breadcrumbs.
        """
        search_query = self.request.GET.urlencode()
        self.request.session[settings.SEARCH_COOKIE_NAME] = search_query

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['perimeter'] = self.form.cleaned_data.get('perimeter', None)
        context['categories'] = self.form.cleaned_data.get('categories', None)
        context['themes'] = self.form.cleaned_data.get('themes', None)
        context['current_search'] = self.request.session.get(
            settings.SEARCH_COOKIE_NAME, '')

        default_order = 'relevance'
        order_value = self.request.GET.get('order_by', default_order)
        order_labels = dict(AidSearchForm.ORDER_BY)
        order_label = order_labels.get(
            order_value, order_labels[default_order])
        context['order_label'] = order_label
        context['alert_form'] = AlertForm(label_suffix='')

        return context


class AdvancedSearchView(SearchMixin, FormView):
    """Only displays the search form, more suitable for mobile views."""

    form_class = AdvancedAidFilterForm
    template_name = 'aids/advanced_search.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_search'] = self.request.session.get(
            settings.SEARCH_COOKIE_NAME, '')
        return context


class ResultsView(SearchView):
    """Only display search results.

    This view is designed to be called via ajax, and only renders html
    fragment of search engine results.
    """
    template_name = 'aids/_results.html'

    def get_context_data(self, **kwargs):
        kwargs['search_actions'] = True
        return super().get_context_data(**kwargs)


class ResultsReceiveView(LoginRequiredMixin, SearchView):
    """Send the search results by email."""

    http_method_names = ['post']
    EMAIL_SUBJECT = 'Vos résultats de recherche'

    def get_form_data(self):
        querydict = self.request.POST.copy()
        for key in ('csrfmiddlewaretoken', 'integration'):
            try:
                querydict.pop(key)
            except KeyError:
                pass
        return querydict

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['data'] = self.get_form_data()
        return kwargs

    def post(self, request, *args, **kwargs):
        """Send those search results by email to the user.

        We do it synchronously, but this view is meant to be called from an
        ajax query, so it should not be a problem.
        """
        self.form = self.get_form()
        self.form.full_clean()
        results = self.get_queryset()
        nb_results = results.count()
        first_results = results[:10]
        site = get_current_site(self.request)
        querystring = self.get_form_data().urlencode()
        scheme = 'https'
        search_url = reverse('search_view')
        full_url = '{scheme}://{domain}{search_url}?{querystring}'.format(
            scheme=scheme,
            domain=site.domain,
            search_url=search_url,
            querystring=querystring)
        results_body = render_to_string('emails/search_results.txt', {
            'user_name': self.request.user.full_name,
            'aids': first_results,
            'nb_results': nb_results,
            'full_url': full_url,
            'scheme': scheme,
            'domain': site.domain,
        })
        send_mail(
            self.EMAIL_SUBJECT,
            results_body,
            settings.DEFAULT_FROM_EMAIL,
            [self.request.user.email],
            fail_silently=False)
        return HttpResponse('')


class AidDetailView(DetailView):
    """Display an aid detail."""

    template_name = 'aids/detail.html'

    def get_queryset(self):
        """Get the queryset.

        Since we want to enable aid preview, we have special cases depending
        on the current user:

         - anonymous or normal users can only see published aids.
         - contributors can see their own aids.
         - superusers can see all aids.
        """
        category_qs = Category.objects \
            .select_related('theme') \
            .order_by('theme__name', 'name')

        base_qs = Aid.objects \
            .select_related('perimeter', 'author') \
            .prefetch_related('financers', 'instructors') \
            .prefetch_related(Prefetch('categories', queryset=category_qs))

        user = self.request.user
        if user.is_authenticated and user.is_superuser:
            qs = base_qs
        elif user.is_authenticated:
            q_published = Q(status='published')
            q_is_author = Q(author=user)
            qs = base_qs.filter(q_published | q_is_author)
        else:
            qs = base_qs.published()

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        current_search = self.request.session.get(
            settings.SEARCH_COOKIE_NAME, None)
        if current_search:
            context['current_search'] = current_search

        context['aid_slug'] = self.object.slug

        financers = self.object.financers.all()
        # We don't want to display instructors if they are the same as the
        # financers
        instructors = list(set(self.object.instructors.all()) - set(financers))
        context.update({
            'financers': financers,
            'instructors': instructors,
        })

        return context

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        log_event('aid', 'viewed', meta=self.object.slug, value=1)
        return response


class AidEditMixin:
    """Common code to aid editing views."""

    def get_queryset(self):
        qs = Aid.objects \
            .filter(author=self.request.user) \
            .order_by('name')
        self.queryset = qs
        return super().get_queryset()


class AidDraftListView(ContributorRequiredMixin, AidEditMixin, ListView):
    """Display the list of aids published by the user."""

    template_name = 'aids/draft_list.html'
    context_object_name = 'aids'
    paginate_by = 50
    sortable_columns = [
        'name',
        'date_created',
        'date_updated',
        'submission_deadline',
        'status',
    ]
    default_ordering = 'date_created'

    def get_queryset(self):
        qs = super().get_queryset()
        return qs

    def get_ordering(self):
        order = self.request.GET.get('order', '')
        order_field = order.lstrip('-')
        if order_field not in self.sortable_columns:
            order = self.default_ordering
        return order

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ordering'] = self.get_ordering()
        aid_slugs = context['aids'].values_list('slug', flat=True)

        events = Event.objects \
            .filter(category='aid', event='viewed') \
            .filter(meta__in=aid_slugs) \
            .values_list('meta') \
            .annotate(nb_views=Sum('value')) \
            .order_by('meta')
        context['hits'] = dict(events)

        return context


class AidCreateView(ContributorRequiredMixin, CreateView):
    """Allows publishers to submit their own aids."""

    template_name = 'aids/create.html'
    form_class = AidEditForm

    def form_valid(self, form):
        self.object = aid = form.save(commit=False)

        requested_status = self.request.POST.get('status', None)
        if requested_status == 'review':
            aid.status = 'reviewable'

        aid.author = self.request.user
        aid.save()
        form.save_m2m()

        msg = _('Your aid was sucessfully created. You can keep editing it or '
                '<a href="%(url)s" target="_blank">preview it</a>.') % {
                    'url': aid.get_absolute_url()
                }

        messages.success(self.request, msg)
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        edit_url = reverse('aid_edit_view', args=[self.object.slug])
        return edit_url


class AidEditView(ContributorRequiredMixin, MessageMixin, AidEditMixin,
                  UpdateView):
    """Edit an existing aid."""

    template_name = 'aids/edit.html'
    context_object_name = 'aid'
    form_class = AidEditForm

    def form_valid(self, form):

        save_as_new = '_save_as_new' in self.request.POST
        if save_as_new:
            obj = form.save(commit=False)
            obj.id = None
            obj.slug = None
            obj.date_created = timezone.now()
            obj.date_published = None
            obj.status = AidWorkflow.states.draft
            obj.is_imported = False
            obj.import_uniqueid = None
            obj.save()
            form.save_m2m()
            msg = _('The new aid was sucessfully created. You can keep '
                    'editing it.')

            response = HttpResponseRedirect(self.get_success_url())
        else:
            response = super().form_valid(form)
            msg = _('The aid was sucessfully updated. You can keep '
                    'editing it.')

        self.messages.success(msg)
        return response

    def get_success_url(self):
        edit_url = reverse('aid_edit_view', args=[self.object.slug])
        return '{}?preview'.format(edit_url)


class AidStatusUpdate(ContributorRequiredMixin, AidEditMixin,
                      SingleObjectMixin, RedirectView):
    """Update an aid status."""

    http_method_names = ['post']

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.update_aid_status()
        return super().post(request, *args, **kwargs)

    def update_aid_status(self):
        """Move the aid to the next step in the workflow.

        None of these transitions require any special permission, hence we
        don't run any additional checks.
        """
        aid = self.object

        # Check that submitted form data is still consistent
        current_status = self.request.POST.get('current_status', None)
        if aid.status != current_status:
            return

        STATES = AidWorkflow.states
        if aid.status == STATES.draft:
            aid.submit()
        elif aid.status in (STATES.reviewable, STATES.published):
            aid.unpublish()
            log_admins.delay(
                'Aide dépubliée',
                'Une aide vient d\'être dépubliée.\n\n{}'.format(aid),
                aid.get_absolute_url())

        msg = _('We updated your aid status.')
        messages.success(self.request, msg)

    def get_redirect_url(self, *args, **kwargs):
        return reverse('aid_edit_view', args=[self.object.slug])


class AidDeleteView(ContributorRequiredMixin, AidEditMixin, DeleteView):
    """Soft deletes an existing aid."""

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        confirmed = self.request.POST.get('confirm', False)
        if confirmed:
            self.object.soft_delete()
            msg = _('Your aid was deleted.')
            messages.success(self.request, msg)

        success_url = reverse('aid_draft_list_view')
        redirect = HttpResponseRedirect(success_url)
        return redirect


class AidAmendView(MessageMixin, UpdateView):
    """Offers a way to users to amend existing aids."""

    template_name = 'aids/amend.html'
    form_class = AidAmendForm
    context_object_name = 'aid'

    def get_queryset(self):
        return Aid.objects.published().open()

    def get_initial(self):
        initial = super().get_initial()
        if self.request.user.is_authenticated:
            initial.update({
                'amendment_author_name': self.request.user.full_name,
                'amendment_author_email': self.request.user.email,
                'amendment_author_org': self.request.user.organization,
            })
        return initial

    def form_valid(self, form):
        amended_aid_pk = form.instance.pk
        amended_aid_slug = form.instance.slug

        aid = form.save(commit=False)
        aid.pk = None
        aid.date_created = timezone.now()
        aid.date_updated = None
        aid.is_amendment = True
        aid.amended_aid_id = amended_aid_pk
        aid.is_imported = False
        aid.import_uniqueid = None

        if self.request.user.is_authenticated:
            aid.author = self.request.user
        else:
            aid.author = None

        aid.save()
        form.save_m2m()

        msg = _('Your amendment will be reviewed by an admin soon. '
                'Thank you for contributing.')
        self.messages.success(msg)
        url = reverse('aid_detail_view', args=[amended_aid_slug])
        return HttpResponseRedirect(url)
