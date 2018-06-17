Run docker-compose up -d
From activated virtualenv run "python manage.py migrate"

For now, if you want to use different ports for Postgres\Redis you have to change these ports in settings.py and docker-compose file

To make celery work, run following:
	- celery -A PartyCalculator worker -l DEBUG
	- celery -A PartyCalculator beat -l DEBUG --scheduler django_celery_beat.schedulers:DatabaseScheduler
	
	OPTIONAL:
	- celery flower -A PartyCalculator --broker=redis://localhost:6300/0 --info
		- port must be the same as in docker-compose/settings (currently 6300)
