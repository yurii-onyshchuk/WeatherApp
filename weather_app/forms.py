import datetime
from django import forms
from django.conf import settings
from weather_app.services.weather_api_service import CitySearcher


class WeatherForm(forms.Form):
    """Form to collect user input for weather request"""

    start_date = forms.DateField(label='Початкова дата', widget=forms.DateInput(attrs={'type': 'date', }))
    end_date = forms.DateField(label='Кінцева дата', widget=forms.DateInput(attrs={'type': 'date', }))
    city = forms.CharField(label='Місто', max_length=100, widget=forms.TextInput(attrs={'autocomplete': 'off', }))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['start_date'].widget.attrs.update({'min': self.min_date, 'max': self.max_date})
        self.fields['end_date'].widget.attrs.update({'min': self.min_date, 'max': self.max_date})

    def clean_start_date(self):
        """Clean and validate the start date input.

        Ensures that the start date is within the allowed historical weather data range.
        """
        start_date = self.cleaned_data['start_date']
        if start_date < self.min_date:
            self.add_error("start_date",
                           "Введено некоректну дату. Ми не можемо надати відомості про погоду більше 1 року тому")
        else:
            return start_date

    def clean_end_date(self):
        """Clean and validate the end date input.

        Ensures that the end date is within the allowed forecast weather data range.
        """
        end_date = self.cleaned_data['end_date']
        if end_date > self.max_date:
            self.add_error("end_date",
                           "Введено некоректну дату. Ми не можемо надати відомості про погоду більше як на 14 днів")
        else:
            return end_date

    def clean_city(self):
        """Clean and validate the user-input city field.

        This method checks if the entered city exists by querying an external API
        to ensure it's a valid city name.
        If the city is not found in the API data, an error is added to the field.
        """
        city = self.cleaned_data['city']
        if not CitySearcher(self.cleaned_data).get_data_from_API():
            self.add_error("city", "Введено некоректне місто. Зробіть вибір із запропонованих варіантів.")
        else:
            return city

    def clean(self):
        """Clean and validate the form as a whole.

        Checks if the start date is earlier than the end date.
        """
        cleaned_data = super().clean()
        start_date = cleaned_data['start_date']
        end_date = cleaned_data['end_date']

        if start_date and end_date and start_date > end_date:
            self.add_error("start_date", "Початкова дата повинна бути меншою за кінцеву дату")
            self.add_error("end_date", "Кінцева дата повинна бути більшою за початкову дату")
        return cleaned_data

    @property
    def min_date(self):
        """Get the minimum allowed date for user input."""
        return datetime.date.today() - datetime.timedelta(days=settings.WEATHER_API_LIMITS['history_days_limit'])

    @property
    def max_date(self):
        """Get the maximum allowed date for user input."""
        return datetime.date.today() + datetime.timedelta(days=settings.WEATHER_API_LIMITS['forecast_days_limit'] - 1)
