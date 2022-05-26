import sys

from django.apps import (
    apps,
)
from django.core.management import (
    BaseCommand,
)
from django.db import (
    connection,
)

from m3_db_utils.helpers import (
    is_abstract_model,
    is_proxy_model,
)

from web_bb.core.base.partitions import (
    DateRangePartitionedModelMixin,
)


class Command(BaseCommand):
    help = (
        """
        Команда предназначена для зачистки всех секций партицированных таблиц и создания дефолтных секций 
        """
    )

    def handle(self, *args, **options):
        cursor = connection.cursor()

        models = filter(
            lambda m: issubclass(m, DateRangePartitionedModelMixin) and not is_abstract_model(m) and not is_proxy_model(m),
            apps.get_models(),
        )

        for model in models:
            sys.stdout.write(f'Обработка модели "{model.__name__}"..\n')

            partition_ranges = model.get_existing_partition_ranges()

            for partition_name, _, _ in partition_ranges:
                cursor.execute(
                    f'DROP TABLE {partition_name} CASCADE;'
                )

                sys.stdout.write(f'Секция "{partition_name}" была удалена.\n')

            model.create_default_partition()

            sys.stdout.write(f'Обработка модели "{model.__name__}" завершена.\n')

        cursor.close()


