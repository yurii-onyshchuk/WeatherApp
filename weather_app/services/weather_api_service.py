import json
import datetime

import requests

from django.conf import settings


class WeatherDataProcessor:
    def __init__(self, data):
        self.data = data

    def get_weather_data_from_api(self):
        if self.data['start_date'] > datetime.date.today():
            forecast_weather_data = ForecastWeatherRetriever(self.data).get_weather_data_from_api()
            return forecast_weather_data

        elif self.data['end_date'] <= datetime.date.today():
            historical_weather_data = HistoryWeatherRetriever(self.data).get_weather_data_from_api()
            return historical_weather_data


class AbstractWeatherRetriever:
    def __init__(self, data: dict):
        self.data = data

    def get_query_params(self) -> dict:
        query_params = {'key': settings.WEATHER_API_KEY,
                        'q': self.data['city'],
                        'lang': settings.WEATHER_API_LANGUAGE_CODE}
        return query_params


class HistoryWeatherRetriever(AbstractWeatherRetriever):
    def get_weather_data_from_api(self):
        query_params = self.get_query_params()
        response = request_to_api(settings.WEATHER_API_URL + settings.WEATHER_API_METHOD['history'], query_params)
        return response

    def get_query_params(self) -> dict:
        query_params = super().get_query_params()
        query_params.update({'dt': self.data['start_date'],
                             'end_dt': self.data['end_date']})
        return query_params


class ForecastWeatherRetriever(AbstractWeatherRetriever):
    def get_weather_data_from_api(self):
        query_params = self.get_query_params()
        response = request_to_api(settings.WEATHER_API_URL + settings.WEATHER_API_METHOD['forecast'], query_params)
        return response

    def get_query_params(self) -> dict:
        query_params = super().get_query_params()
        query_params.update({'days': settings.WEATHER_API_LIMITS['forecast_days_limit'], })
        return query_params


def request_to_api(url, params):
    response = requests.get(url, params)
    print(response.url)
    if response.status_code == 200:
        return json.loads(response.text)
    else:
        raise response.raise_for_status()
