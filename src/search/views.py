from django.views.generic import FormView

from aids.forms import AidSearchForm
from search.forms import (AudianceSearchForm, PerimeterSearchForm,
                          ThemeSearchForm, CategorySearchForm)


class SearchMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['querystring'] = self.request.GET.urlencode()
        return context


class AudianceSearch(SearchMixin, FormView):
    template_name = 'search/step_audiance.html'
    form_class = AudianceSearchForm


class PerimeterSearch(SearchMixin, FormView):
    template_name = 'search/step_perimeter.html'
    form_class = PerimeterSearchForm

    def get_initial(self):
        GET = self.request.GET
        initial = {
            'targeted_audiances': GET.getlist('targeted_audiances', ''),
        }
        return initial


class ThemeSearch(SearchMixin, FormView):
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
        aids = filter_form.filter_queryset()
        context['total_aids'] = aids.count()
        return context
