import datetime

from django.test import TestCase
from django.urls import reverse


class WeatherDataProcessorTestCase(TestCase):
    today = datetime.date.today()

    def test_dates_before_today(self):
        start_date = self.today - datetime.timedelta(days=7)
        end_date = self.today - datetime.timedelta(days=1)
        self.execute_date_test(start_date, end_date, 'historical_weather_data')

    def test_start_date_before_today_end_date_today(self):
        start_date = self.today - datetime.timedelta(days=7)
        end_date = self.today
        self.execute_date_test(start_date, end_date, 'historical_weather_data')

    def test_start_date_today_end_date_after_today(self):
        start_date = self.today
        end_date = self.today + datetime.timedelta(days=7)
        self.execute_date_test(start_date, end_date, 'historical_weather_data', 'forecast_weather_data', )

    def test_dates_after_today(self):
        start_date = self.today + datetime.timedelta(days=1)
        end_date = self.today + datetime.timedelta(days=7)
        self.execute_date_test(start_date, end_date, 'forecast_weather_data')

    def test_start_date_before_today_end_date_after_today(self):
        start_date = self.today - datetime.timedelta(days=3)
        end_date = self.today + datetime.timedelta(days=3)
        self.execute_date_test(start_date, end_date, 'historical_weather_data', 'forecast_weather_data', )

    def test_equal_dates_before_today(self):
        start_date = self.today - datetime.timedelta(days=7)
        end_date = self.today - datetime.timedelta(days=7)
        self.execute_date_test(start_date, end_date, 'historical_weather_data')

    def test_equal_dates_today(self):
        start_date = end_date = self.today
        self.execute_date_test(start_date, end_date, 'historical_weather_data')

    def test_equal_dates_after_today(self):
        start_date = self.today + datetime.timedelta(days=7)
        end_date = self.today + datetime.timedelta(days=7)
        self.execute_date_test(start_date, end_date, 'forecast_weather_data')

    def execute_date_test(self, start_date, end_date, *expected_keys):
        data = {'start_date': start_date, 'end_date': end_date, 'city': 'Kyiv', }
        url = reverse('home')
        response = self.client.post(url, data)

        weather_data = []
        for key in expected_keys:
            weather_data += response.context['api_weather_data'][key]['forecast']['forecastday']

        expected_day_count = (end_date - start_date + datetime.timedelta(days=1)).days
        actual_day_count = len(weather_data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(expected_day_count, actual_day_count)
        self.assertEqual(datetime.datetime.strptime(weather_data[0]['date'], "%Y-%m-%d").date(), start_date)
        self.assertEqual(datetime.datetime.strptime(weather_data[-1]['date'], "%Y-%m-%d").date(), end_date)
