import os

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PartyCalculator.settings')

app = Celery('PartyCalculator')
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

app.conf.beat_schedule = {}
