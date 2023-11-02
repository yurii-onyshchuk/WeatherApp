from django.db import models


class WeatherData(models.Model):
    """Model to represent weather data for a specific city and date."""

    city = models.CharField(verbose_name='Місто', max_length=100)
    date = models.DateField(verbose_name='Дата спостереження')
    temperature = models.DecimalField(verbose_name='Температура', max_digits=3, decimal_places=1)
