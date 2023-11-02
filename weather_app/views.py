from django.views.generic import FormView

from .forms import WeatherForm


class Home(FormView):
    """View class for the home page with a form to collect user input data for a weather query."""

    template_name = 'weather_app/index.html'
    form_class = WeatherForm
    extra_context = {'title': 'Дізнайся про погоду'}
