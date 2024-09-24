import csv

from django.apps import apps
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db.utils import IntegrityError


class Command(BaseCommand):
    help = 'Load CSV file to DataBase'
    LOOKUP_APP_NAME = 'reviews'

    def add_arguments(self, parser) -> None:
        parser.add_argument('csv_file', type=str, help='File with path')

    def get_model_by_name(self, name):
        if '_' in name:
            name = ''.join(name.split('_'))
        if 'user' in name:
            return get_user_model()
        for check_name in [name, name[:-1]]:
            # Try plural and single spelling
            try:
                model = apps.get_model(
                    app_label=self.LOOKUP_APP_NAME, model_name=check_name
                )
                return model
            except LookupError:
                pass
        raise CommandError(
            f'Model {name} does not exist. '
            'Check model name.'
        )

    def handle(self, *args, **options):
        file_path = options['csv_file']
        file_name = file_path.split('/')[-1]
        model_name = file_name.split('.')[0]
        model = self.get_model_by_name(model_name)
        with open(file_path, encoding='utf=8') as file:
            reader = csv.DictReader(file)
            count = 0
            for row in reader:
                try:
                    _, created = model.objects.get_or_create(**row)
                    if created:
                        count += 1
                    else:
                        self.stdout.write(self.style.WARNING(
                            f'Object with fields {row} already exist. '
                            'Object creation Skipped'
                        ))
                except IntegrityError:
                    raise CommandError(
                        f'Can not create object {row}. '
                        'Objects with partially matching values already exist '
                        'in DataBase.\nUNIQUE constraint violated.'
                    )
                except ValueError as err:
                    raise CommandError(
                        f'{err}\nPlease check fields names in CSV file. '
                        'Field name for Related Fields should end in `_id`.'
                    )
        self.stdout.write(self.style.SUCCESS(
            f'Successfully load {file_name}.\n'
            f'{count} objects added to {model.__name__} model.'
        ))
