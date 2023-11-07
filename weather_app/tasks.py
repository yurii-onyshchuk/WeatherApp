from Weather.celery import app
from weather_app.models import WeatherData


@app.task
def save_api_weather_data(api_weather_data: dict) -> None:
    """A Celery task for save weather data to DB.

    This Celery task is responsible for saving weather data received from
    an external API to the database using the `WeatherData.save_api_weather_data` method.
    """
    WeatherData.save_api_weather_data(api_weather_data)
