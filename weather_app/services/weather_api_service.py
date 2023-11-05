import json
import datetime

import requests

from django.conf import settings


class WeatherDataProcessor:
    def __init__(self, data):
        self.data = data
        self.forecast_weather_data, self.historical_weather_data = {}, {}

    def get_weather_data_from_api(self) -> dict:
        if self.data['start_date'] > datetime.date.today():
            self.forecast_weather_data = ForecastWeatherRetriever(self.data).get_weather_data_from_api()
        elif self.data['end_date'] <= datetime.date.today():
            self.historical_weather_data = HistoryWeatherRetriever(self.data).get_weather_data_from_api()
        else:
            self.forecast_weather_data = ForecastWeatherRetriever(self.data).get_weather_data_from_api()
            self.historical_weather_data = HistoryWeatherRetriever(self.data).get_weather_data_from_api()
        return {'forecast_weather_data': self.forecast_weather_data,
                'historical_weather_data': self.historical_weather_data}


class AbstractWeatherRetriever:
    def __init__(self, data: dict):
        self.data = data

    def get_query_params(self) -> dict:
        query_params = {'key': settings.WEATHER_API_KEY,
                        'q': self.data['city'],
                        'lang': settings.WEATHER_API_LANGUAGE_CODE}
        return query_params


class HistoryWeatherRetriever(AbstractWeatherRetriever):
    weather_api_method = settings.WEATHER_API_METHOD['history']
    max_days_range = settings.WEATHER_API_LIMITS['max_days_range_for_history_request']

    def get_weather_data_from_api(self):
        subperiod_list = split_data_period(self.data['start_date'], self.data['end_date'], self.max_days_range)
        response_list = self.get_response_list(subperiod_list)
        result_response = response_list[0]
        if len(response_list) > 1:
            for i in range(1, len(response_list)):
                result_response['forecast']['forecastday'].extend(response_list[i]['forecast']['forecastday'])
        return result_response

    def get_response_list(self, subperiod_list):
        response_list = []
        for subperiod in subperiod_list:
            self.data['start_date'] = subperiod['start_date']
            self.data['end_date'] = subperiod['end_date']
            query_params = self.get_query_params()
            response = request_to_api(settings.WEATHER_API_URL + self.weather_api_method, query_params)
            response_list.append(response)
        return response_list

    def get_query_params(self) -> dict:
        query_params = super().get_query_params()
        query_params.update({'dt': self.data['start_date'],
                             'end_dt': self.data['end_date']})
        return query_params


class ForecastWeatherRetriever(AbstractWeatherRetriever):
    weather_api_method = settings.WEATHER_API_METHOD['forecast']

    def get_weather_data_from_api(self):
        query_params = self.get_query_params()
        response = request_to_api(settings.WEATHER_API_URL + self.weather_api_method, query_params)
        response = self.date_filter(response)
        return response

    def date_filter(self, response):
        forecastdays = response['forecast']['forecastday']
        filtered_forecast = []
        for day in forecastdays:
            date = datetime.datetime.strptime(day['date'], "%Y-%m-%d").date()
            if self.data['start_date'] <= date <= self.data['end_date']:
                filtered_forecast.append(day)
        response['forecast']['forecastday'] = filtered_forecast
        return response

    def get_query_params(self) -> dict:
        query_params = super().get_query_params()
        query_params.update({'days': settings.WEATHER_API_LIMITS['forecast_days_limit'], })
        return query_params


def split_data_period(start_date, end_date, interval_in_day: int) -> list[dict]:
    if end_date - start_date < datetime.timedelta(interval_in_day):
        return [{'start_date': start_date, 'end_date': end_date}, ]
    subperiod_list = []
    while start_date <= end_date:
        end_of_period = start_date + datetime.timedelta(interval_in_day)
        if end_of_period > end_date:
            end_of_period = end_date
        subperiod_list.append({'start_date': start_date, 'end_date': end_of_period})
        start_date = end_of_period + datetime.timedelta(days=1)
    return subperiod_list


def request_to_api(url, params):
    response = requests.get(url, params)
    print(response.url)
    if response.status_code == 200:
        return json.loads(response.text)
    else:
        raise response.raise_for_status()
