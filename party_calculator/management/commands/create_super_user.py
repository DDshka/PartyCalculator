from django.core.management import BaseCommand


class Command(BaseCommand):
    help = 'Used to create a superuser.'
    requires_migrations_checks = True

    def handle(self, *args, **options):
        print("ZDAROVA")