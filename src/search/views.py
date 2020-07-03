from django.views.generic import FormView
from django.http import QueryDict, Http404

from aids.forms import AidSearchForm
from aids.views import SearchView
from search.models import SearchPage
from search.forms import (AudianceSearchForm, PerimeterSearchForm,
                          ThemeSearchForm, CategorySearchForm)


class SearchMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['querystring'] = self.request.GET.urlencode()
        return context


class AudianceSearch(SearchMixin, FormView):
    """Step 1 of the multi-page search form."""

    template_name = 'search/step_audiance.html'
    form_class = AudianceSearchForm


class PerimeterSearch(SearchMixin, FormView):
    """Step 2 of the multi-page search form."""

    template_name = 'search/step_perimeter.html'
    form_class = PerimeterSearchForm

    def get_initial(self):
        GET = self.request.GET
        initial = {
            'targeted_audiances': GET.getlist('targeted_audiances', ''),
        }
        return initial


class ThemeSearch(SearchMixin, FormView):
    """Step 3 of the multi-page search form."""

    template_name = 'search/step_theme.html'
    form_class = ThemeSearchForm

    def get_initial(self):
        GET = self.request.GET
        initial = {
            'targeted_audiances': GET.getlist('targeted_audiances', ''),
            'perimeter': GET.get('perimeter', ''),
        }
        return initial


class CategorySearch(SearchMixin, FormView):
    """Step 4 of the multi-page search form."""

    template_name = 'search/step_category.html'
    form_class = CategorySearchForm

    def get_initial(self):
        GET = self.request.GET
        initial = {
            'targeted_audiances': GET.getlist('targeted_audiances', ''),
            'perimeter': GET.get('perimeter', ''),
            'themes': GET.getlist('themes', []),
        }
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        initial = self.get_initial()
        filter_form = AidSearchForm(initial)
        theme_aids = filter_form.filter_queryset()

        if initial['themes']:
            theme_aids = theme_aids.filter(
                categories__theme__slug__in=initial['themes'])

        context['total_aids'] = theme_aids.distinct().count()
        return context


class SearchPageDetail(SearchView):
    """A static search page with admin-customizable content."""

    template_name = 'search/search_page.html'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().get(request, *args, **kwargs)

    def get_object(self):
        qs = SearchPage.objects.filter(slug=self.kwargs.get('slug'))
        try:
            obj = qs.get()
        except qs.model.DoesNotExist:
            raise Http404('No "Search page" found matching the query')
        return obj

    def get_form_kwargs(self):
        """Set the data passed to the form.

        If no data was provided by the user, then we use the initial
        querystring provided by admins.

        If the form was submitted, the GET values are set, we use those
        instead.
        """
        initial_data = QueryDict(
            self.object.search_querystring, mutable=True)
        user_data = self.request.GET.copy()
        user_data.pop('page', None)
        user_data.pop('integration', None)
        data = user_data or initial_data
        kwargs = super().get_form_kwargs()
        kwargs['data'] = data
        return kwargs

    def get_form(self, form_class=None):
        form = super().get_form(form_class)

        if self.object.available_categories:
            categories_qs = self.object.available_categories
            form.fields['categories'].queryset = categories_qs

        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_page'] = self.get_object()
        return context
