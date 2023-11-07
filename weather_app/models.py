import datetime
from django.db import models


class WeatherData(models.Model):
    """Model to represent weather data for a specific city and date."""

    city = models.CharField(verbose_name='Місто', max_length=100)
    date = models.DateField(verbose_name='Дата спостереження')
    temperature = models.DecimalField(verbose_name='Температура, °C', max_digits=3, decimal_places=1)

    def __str__(self):
        return f'{self.city} / {self.date}'

    class Meta:
        unique_together = ('city', 'date',)
        verbose_name = 'Погодні дані'
        verbose_name_plural = 'Погодні дані'

    @classmethod
    def get_data_according_to_form(cls, data: dict) -> models.QuerySet | None:
        """ Retrieve weather data from the database based on user input.

        If only ALL the required data is three-digit in the database, then they return.
        Otherwise, nothing is returned.
        """
        db_weather_data = cls.objects.filter(city=data['city'], date__range=(data['start_date'], data['end_date']))
        date_range = [data['start_date'] + datetime.timedelta(days=i)
                      for i in range((data['end_date'] - data['start_date']).days + 1)]
        if db_weather_data.count() == len(date_range):
            return db_weather_data

    @classmethod
    def save_api_weather_data(cls, data: dict) -> None:
        """Save weather data from an external API to the database.

        This method extracts relevant data from the API response
        and saves it as WeatherData records in the database.
        """
        weather_data_list = []
        for weather_data_type, value in data.items():
            if value:
                for day in data[weather_data_type]['forecast']['forecastday']:
                    city = data[weather_data_type]['location']['name']
                    date_str = day['date']
                    avg_temp = day['day']['avgtemp_c']
                    date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
                    weather_data = cls(city=city, date=date, temperature=avg_temp)
                    weather_data_list.append(weather_data)
        cls.objects.bulk_create(weather_data_list, ignore_conflicts=True)
