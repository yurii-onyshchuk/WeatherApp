# Generated by Django 4.2.7 on 2023-11-06 00:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('weather_app', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='weatherdata',
            options={'verbose_name': 'Погодні дані', 'verbose_name_plural': 'Погодні дані'},
        ),
        migrations.AlterField(
            model_name='weatherdata',
            name='temperature',
            field=models.DecimalField(decimal_places=1, max_digits=3, verbose_name='Температура, °C'),
        ),
        migrations.AlterUniqueTogether(
            name='weatherdata',
            unique_together={('city', 'date')},
        ),
    ]