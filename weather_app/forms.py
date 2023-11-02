from django import forms


class WeatherForm(forms.Form):
    """Form to collect user input for weather request"""

    city = forms.CharField(label='Місто', max_length=100)
    start_date = forms.DateField(label='Початкова дата')
    end_date = forms.DateField(label='Кінцева дата')
