from django.core.management import BaseCommand, call_command


class Command(BaseCommand):
    help = 'Deploying in Docker container'

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('db', nargs='+', type=str)

    def handle(self, *args, **options):
        try:
            # call_command("makemigrations")
            call_command("migrate")
            call_command("loaddata", options['db'])
        except:
            pass
