# Generated by Django 4.2.7 on 2023-11-02 20:45

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='WeatherData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('city', models.CharField(max_length=100, verbose_name='Місто')),
                ('date', models.DateField(verbose_name='Дата спостереження')),
                ('temperature', models.DecimalField(decimal_places=1, max_digits=3, verbose_name='Температура')),
            ],
        ),
    ]