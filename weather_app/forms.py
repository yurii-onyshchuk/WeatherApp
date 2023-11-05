from django import forms


class WeatherForm(forms.Form):
    """Form to collect user input for weather request"""

    start_date = forms.DateField(label='Початкова дата', widget=forms.DateInput(attrs={'type': 'date', }))
    end_date = forms.DateField(label='Кінцева дата', widget=forms.DateInput(attrs={'type': 'date', }))
    city = forms.CharField(label='Місто', max_length=100)

