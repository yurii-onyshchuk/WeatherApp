import copy
import datetime
import json
import requests

from django.conf import settings


class WeatherDataProcessor:
    """Class to process weather data retrieval from an external API.

    Manages fetching weather data based on user input and classifies it as historical or forecast data.
    """

    def __init__(self, data: dict):
        self.data = data
        self.forecast_weather_data, self.historical_weather_data = {}, {}

    def get_weather_data_from_API(self) -> dict:
        """Fetch weather data from an external API based on user input.

        Determines whether to fetch historical or forecast data, or both, based on user-defined date ranges.
        """
        if self.data['start_date'] > datetime.date.today():
            self.forecast_weather_data = ForecastWeatherRetriever(self.data).get_data_from_API()
        elif self.data['end_date'] <= datetime.date.today():
            self.historical_weather_data = HistoryWeatherRetriever(self.data).get_data_from_API()
        else:
            self.forecast_weather_data = ForecastWeatherRetriever(self.data).get_data_from_API()
            self.historical_weather_data = HistoryWeatherRetriever(self.data).get_data_from_API()
        return {'historical_weather_data': self.historical_weather_data,
                'forecast_weather_data': self.forecast_weather_data, }


class AbstractWeatherAPIRetriever:
    """Abstract class for fetching data from an external API.

    Contains common methods and properties for all weather data retrieval classes.
    """

    api_key = settings.WEATHER_API_KEY
    api_url = settings.WEATHER_API_URL
    api_method = None
    api_language_code = settings.WEATHER_API_LANGUAGE_CODE

    def __init__(self, data: dict):
        self.data = data

    def get_response(self) -> dict:
        """Send a request to the external API and return the response."""
        query_params = self.get_query_params()
        response = request_to_api(self.api_url + self.api_method, query_params)
        return response

    def get_query_params(self) -> dict:
        """Define query parameters for the API request."""
        query_params = {'key': self.api_key,
                        'q': self.data['city'],
                        'lang': self.api_language_code}
        return query_params


class HistoryWeatherRetriever(AbstractWeatherAPIRetriever):
    """Class for fetching historical weather data from an external API.

    Retrieves historical weather data within a given date range.
    """

    api_method = settings.WEATHER_API_METHOD['history']
    max_days_range = settings.WEATHER_API_LIMITS['max_days_range_for_history_request']

    def get_data_from_API(self):
        """Fetch historical weather data from the API, considering API's evening behavior.

        This method retrieves historical weather data within the specified date range,
        accounting for the API's behavior. In the evening, the API provides weather data
        for the next day in historical data. Therefore, if the end date is greater than today,
        it's adjusted to today's date.
        """
        data = copy.deepcopy(self.data)
        if data['end_date'] > datetime.date.today():
            data['end_date'] = datetime.date.today()
        subperiod_list = split_data_period(data['start_date'], data['end_date'], self.max_days_range)
        response_list = self.get_combined_response(subperiod_list)
        result_response = response_list[0]
        if len(response_list) > 1:
            for i in range(1, len(response_list)):
                result_response['forecast']['forecastday'].extend(response_list[i]['forecast']['forecastday'])
        return result_response

    def get_combined_response(self, subperiod_list: list[dict]):
        """Fetch historical weather data for multiple subperiods."""
        combined_response = []
        for subperiod in subperiod_list:
            self.data['start_date'] = subperiod['start_date']
            self.data['end_date'] = subperiod['end_date']
            response = self.get_response()
            combined_response.append(response)
        return combined_response

    def get_query_params(self) -> dict:
        """Define query parameters specific to historical weather data."""
        query_params = super().get_query_params()
        query_params.update({'dt': self.data['start_date'],
                             'end_dt': self.data['end_date']})
        return query_params


class ForecastWeatherRetriever(AbstractWeatherAPIRetriever):
    """Class for fetching forecast weather data from an external API.

    Retrieves forecast weather data within a given date range.
    """

    api_method = settings.WEATHER_API_METHOD['forecast']
    api_limit = settings.WEATHER_API_LIMITS['forecast_days_limit']

    def get_data_from_API(self) -> dict:
        """Fetch forecast weather data from the API based on user input.

        The API allows querying data for a specific number of days starting from today.
        To accommodate this limitation, the method fetches data for the entire available period
        and then filters it to provide the data relevant to the user's specified date range.
        This ensures that the user gets the data they requested."""
        response = self.get_response()
        return self.date_filter(response)

    def date_filter(self, response: dict) -> dict:
        """Filter forecast weather data based on the user-defined date range.

        This method takes the raw forecast weather data from the API and filters it
        to retain only the data that falls within the user-specified date range.
        """
        forecastdays = response['forecast']['forecastday']
        filtered_forecast = []
        for day in forecastdays:
            date = datetime.datetime.strptime(day['date'], "%Y-%m-%d").date()
            if self.data['start_date'] <= date <= self.data['end_date'] and datetime.date.today() < date:
                filtered_forecast.append(day)
        response['forecast']['forecastday'] = filtered_forecast
        return response

    def get_query_params(self) -> dict:
        """Define query parameters specific to forecast weather data."""
        query_params = super().get_query_params()
        query_params.update({'days': self.api_limit, })
        return query_params


class CitySearcher(AbstractWeatherAPIRetriever):
    """Class to search for city names and retrieve city-related data from an external API."""

    api_method = settings.WEATHER_API_METHOD['search']

    def get_data_from_API(self) -> dict:
        """Fetch city name suggestions based on user input.

        This method queries an external API to retrieve city name
        suggestions matching the user's input.
        """
        return self.get_response()


def split_data_period(start_date: datetime.date, end_date: datetime.date, interval_in_day: int) -> list[dict]:
    """Split a date range into subperiods based on a specified interval."""
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


def request_to_api(url: str, params: dict):
    """Send a request to an external API and return the response"""
    response = requests.get(url, params)
    if response.status_code == 200:
        return json.loads(response.text)
    else:
        raise response.raise_for_status()
