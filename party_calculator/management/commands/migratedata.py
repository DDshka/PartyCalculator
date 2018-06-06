from django.core.management import BaseCommand
from party_calculator.tasks import create_user


class Command(BaseCommand):
    help = 'Migrates passed text file into database'

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('src', nargs='+', type=str)
        parser.add_argument('model', nargs='+', type=str)

    def handle(self, *args, **options):
        model = ''.join(options['model'])
        src = ''.join(options['src'])

        file = open(src, 'r')

        headers = self.clear_and_split(file.readline())

        i = 1
        # todo why don't just use enumerate(...)
        for line in file:
            splitted = self.clear_and_split(line)
            kwargs = dict(zip(headers, splitted))

            kwargs['username'] = kwargs['email']
            kwargs['password'] = '12345678'
            kwargs['legacy_id'] = i

            create_user.delay(module_name="authModule.models", model_name=model, **kwargs)
            i += 1

    def clear_and_split(self, text: str, sep=','):
        return text.replace('\n', '').split(sep=sep)
