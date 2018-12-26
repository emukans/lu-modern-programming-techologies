from django.core.management.base import BaseCommand, CommandError
import json


class Command(BaseCommand):
    help = 'Import match logs'

    def add_arguments(self, parser):
        parser.add_argument('import_path', type=str)

    def handle(self, *args, **options):
        try:
            f = open(options['import_path'], 'r')
            match_data = json.load(f)

            self.stdout.write(self.style.SUCCESS('Successfully read file'))
        except FileNotFoundError:
            raise CommandError('File {file} not found'.format(file=options['import_path']))
