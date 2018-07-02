web: gunicorn PartyCalculator.wsgi --log-file -
python manage.py collectstatic --noinput

celery-worker: celery -A PartyCalculator worker -l info
celery-beat: celery -A PartyCalculator beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
