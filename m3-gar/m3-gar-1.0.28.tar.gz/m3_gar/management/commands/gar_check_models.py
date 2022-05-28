import inspect

from django.apps import (
    apps,
)
from django.core.management import (
    BaseCommand,
    CommandError,
)
from django.db import (
    models,
)

import m3_gar.base_models


class Command(BaseCommand):
    help = 'Утилита проверяет, что по всем базовым моделям созданы дочерние'

    def handle(self, **options):
        child_models = apps.get_models()

        success = True

        for name, obj in inspect.getmembers(m3_gar.base_models):
            if inspect.isclass(obj) and issubclass(obj, models.Model):
                for model in child_models:
                    if issubclass(model, obj):
                        break
                else:
                    self.stdout.write(f'Не найдена модель для {name}')
                    success = False

        if not success:
            self.stdout.write('Найдены не унаследованные базовые модели')

            raise CommandError
