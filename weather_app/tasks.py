from Weather.celery import app
from weather_app.models import WeatherData


@app.task
def save_api_weather_data(api_weather_data):
    """A Celery task for save weather data to DB."""
    WeatherData.save_api_weather_data(api_weather_data)
