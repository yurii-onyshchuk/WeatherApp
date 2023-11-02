import json
import requests

from django.conf import settings


def get_weather_data_from_api(url, params):
    response = requests.get(url, params)
    if response.status_code == 200:
        return json.loads(response.text)
    else:
        raise response.raise_for_status()


def get_query_params(data: dict):
    query_params = {'key': settings.WEATHER_API_KEY, 'q': data['city']}
    return query_params
