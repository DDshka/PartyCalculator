web: gunicorn PartyCalculator.wsgi --log-file -
python manage.py collectstatic --noinput


celery -A PartyCalculator worker -l INFO
celery -A PartyCalculator beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
