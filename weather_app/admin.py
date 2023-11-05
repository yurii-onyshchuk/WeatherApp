from django.contrib import admin
from .models import WeatherData


@admin.register(WeatherData)
class WeatherDataAdmin(admin.ModelAdmin):
    """Admin class for the WeatherData model.

    Defines the display and behavior of WeatherData objects in the Django admin panel.
    """

    list_display = ('city', 'date', 'temperature',)
    list_display_links = ('city',)
    readonly_fields = ('city', 'date', 'temperature',)
    ordering = ('city', 'date',)
    list_filter = ('city',)
