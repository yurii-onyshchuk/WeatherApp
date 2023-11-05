import json
import requests

from django.conf import settings


class WeatherDataRetriever:
    def __init__(self, data: dict):
        self.data = data

    def get_weather_data_from_api(self):
        query_params = self.get_query_params()
        response = request_to_api(settings.WEATHER_API_URL + settings.WEATHER_API_METHOD['history'], query_params)
        return response

    def get_query_params(self):
        query_params = {'key': settings.WEATHER_API_KEY,
                        'q': self.data['city'],
                        'dt': self.data['start_date'],
                        'end_dt': self.data['end_date'],
                        'lang': settings.WEATHER_API_LANGUAGE_CODE, }
        return query_params


def request_to_api(url, params):
    response = requests.get(url, params)
    print(response.url)
    if response.status_code == 200:
        return json.loads(response.text)
    else:
        raise response.raise_for_status()
