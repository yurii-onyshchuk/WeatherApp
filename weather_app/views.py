from django.views.generic import FormView

from .forms import WeatherForm
from .services.weather_api_service import WeatherDataProcessor


class Home(FormView):
    """View class for the home page with a form to collect user input data for a weather query."""

    template_name = 'weather_app/index.html'
    form_class = WeatherForm
    extra_context = {'title': 'Дізнайся про погоду'}

    def form_valid(self, form):
        api_weather_data = WeatherDataProcessor(form.cleaned_data).get_weather_data_from_api()
        return self.render_to_response(self.get_context_data(form=form, api_weather_data=api_weather_data))
