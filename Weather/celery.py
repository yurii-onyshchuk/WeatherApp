import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Weather.settings')
app = Celery('Weather')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
