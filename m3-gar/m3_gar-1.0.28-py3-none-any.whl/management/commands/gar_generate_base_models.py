from django.conf import (
    settings,
)
from django.core.management.commands.inspectdb import (
    Command as InspectDBCommand,
)


class Command(InspectDBCommand):
    help = 'Утилита для генерации базовых моделей на основе XSD'
    usage_str = 'Usage: ./manage.py --dst <path>'

    def add_arguments(self, parser):
        super().add_arguments(parser)

        parser.add_argument(
            '--dst',
            help='Результирующий .py файл',
        )

    def handle(self, **options):
        settings.DATABASES['xsd_folder'] = {
            'ENGINE': 'm3_gar.xsd_generator',
        }
        options['database'] = 'xsd_folder'

        with open(options['dst'], 'w') as f:
            for line in self.handle_inspection(options):
                f.write(f'{line}\n')

    def get_field_type(self, connection, table_name, row):
        field_type, field_params, field_notes = super().get_field_type(
            connection, table_name, row)
        field_params['verbose_name'] = row.description

        if field_type == 'CharField' and 'max_length' not in field_params:
            field_type = 'TextField'

        return field_type, field_params, field_notes

    def get_meta(self, table_name, constraints, column_to_field_name, is_view, is_partition):
        result = super().get_meta(
            table_name, constraints, column_to_field_name, is_view, is_partition)

        for index, row in enumerate(result):
            if "managed = False" in row:
                result[index] = row.replace(
                    "managed = False",
                    "abstract = True",
                )
                break

        for index, row in enumerate(result):
            if "db_table" in row:
                del result[index]
                break

        return result
