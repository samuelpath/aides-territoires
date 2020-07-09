from django.http import QueryDict, Http404
from django.views.generic import TemplateView

from search.models import SearchPage
from aids.views import SearchView, AdvancedSearchView, AidDetailView
from alerts.views import AlertCreate


class MinisiteMixin:

    # Can be `host` or `url`
    page_access_method = 'host'

    def get(self, request, *args, **kwargs):
        self.search_page = self.get_search_page()
        return super().get(request, *args, **kwargs)

    def get_search_page(self):
        """Get the custom page from url.

        This view can be accessed via two urls:
         - aides-territoires.beta.gouv.fr/recherche/<page_name>/
         - <page_name>.aides-territoires.beta.gouv.f

        This view will be accessed from a `xxx.aides-territoires.beta.gouv.fr`.
        So we need to extract the `xxx` part.
        """

        if self.page_access_method == 'host':
            page = self.get_search_page_by_host()
        else:
            page = self.get_search_page_by_url()

        return page

    def get_search_page_by_host(self):
        """Extract the page name from the host."""

        # TODO This was quickly developed before my vacations
        # Will be cleaned up next weeks
        HEADER = 'X-Minisite-Name'
        if HEADER in self.request.headers:
            page_slug = self.request.headers[HEADER]
        else:
            host = self.request.get_host()
            page_slug = host.split('.')[0]

        qs = SearchPage.objects.filter(slug=page_slug)
        try:
            obj = qs.get()
        except qs.model.DoesNotExist:
            raise Http404('No "Search page" found matching the query')
        return obj

    def get_search_page_by_url(self):
        """Extract the page name from the url."""

        page_slug = self.kwargs.get('slug')
        qs = SearchPage.objects.filter(slug=page_slug)
        try:
            obj = qs.get()
        except qs.model.DoesNotExist:
            raise Http404('No "Search page" found matching the query')
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_page'] = self.search_page
        return context


class SiteHome(MinisiteMixin, SearchView):
    """A static search page with admin-customizable content."""

    def get_template_names(self):
        if self.page_access_method == 'host':
            template_name = 'minisites/search_page.html'
        else:
            template_name = 'search/search_page.html'
        return [template_name]

    def get_form_kwargs(self):
        """Set the data passed to the form.

        If no data was provided by the user, then we use the initial
        querystring provided by admins.

        If the form was submitted, the GET values are set, we use those
        instead.
        """
        initial_data = QueryDict(
            self.search_page.search_querystring, mutable=True)
        user_data = self.request.GET.copy()
        user_data.pop('page', None)
        user_data.pop('integration', None)
        data = user_data or initial_data
        kwargs = super().get_form_kwargs()
        kwargs['data'] = data
        return kwargs

    def get_form(self, form_class=None):
        form = super().get_form(form_class)

        if self.search_page.available_categories:
            categories_qs = self.search_page \
                .available_categories \
                .select_related('theme')
            form.fields['categories'].queryset = categories_qs

        return form


class SiteSearch(MinisiteMixin, AdvancedSearchView):
    """The full search form."""

    template_name = 'minisites/advanced_search.html'


class SiteAid(MinisiteMixin, AidDetailView):
    """The detail page of a single aid."""

    template_name = 'minisites/aid_detail.html'


class SiteAlert(MinisiteMixin, AlertCreate):
    pass


class SiteLegalMentions(MinisiteMixin, TemplateView):
    template_name = 'minisites/legal_mentions.html'