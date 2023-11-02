from django.conf import settings
from django.views.generic import FormView

from .forms import WeatherForm
from .services.weather_api_service import get_weather_data_from_api, get_query_params


class Home(FormView):
    """View class for the home page with a form to collect user input data for a weather query."""

    template_name = 'weather_app/index.html'
    form_class = WeatherForm
    extra_context = {'title': 'Дізнайся про погоду'}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'query_params' in kwargs:
            context['title'] = 'Дані щодо погоди'
            context['show_results'] = True
            context['response_data'] = get_weather_data_from_api(settings.WEATHER_API_URL, kwargs['query_params'])
        return context

    def form_valid(self, form):
        query_params = get_query_params(form.cleaned_data)
        return self.render_to_response(self.get_context_data(form=form, query_params=query_params))
