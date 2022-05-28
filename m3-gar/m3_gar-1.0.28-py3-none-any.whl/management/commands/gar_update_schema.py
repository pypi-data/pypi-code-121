from django.conf import (
    settings,
)
from django.core.management import (
    BaseCommand,
    call_command,
)

from m3_gar.exceptions import (
    PublisherError,
)
from m3_gar.publish_tools import (
    ArchiveGARSchemaManager,
    DownloadGARSchemaManager,
    ReleasePreparer,
    Releaser,
    RepoManager,
)


class Command(BaseCommand):
    help = (
        'Основная команда для скачивания новых схем по указанному url, '
        'либо разархивирования архива БД ГАР, содержащего в себе схемы, '
        'генерации моделей по схемам, создания миграций, и выпуска пакета '
        'в случае наличия изменений'
    )
    usage_str = (
        'Usage: python manage.py gar_update_schema --url=<gar_xsd_schemas_url> '
        'OR python manage.py gar_update_schema --path=<path_to_archive_with_schemas>'
    )

    def add_arguments(self, parser):
        super().add_arguments(parser)

        parser.add_argument(
            '--url',
            action='store',
            dest='url',
            help='URL до zip-файла с xsd-схемами для построения БД',
        )
        parser.add_argument(
            '--path',
            action='store',
            dest='path',
            help='Путь до zip-файла с xsd-схемами для построения БД',
        )
        parser.add_argument(
            '--testmode',
            action='store_true',
            default=False,
            help=(
                'Тестовый режим - пуш будет сделан в отдельную ветку, '
                'пакет релизнется на тестовом PyPi. '
                'Для включения нужно добавить флаг --testmode'
            ),
        )

    def handle(
        self,
        *args,
        url,
        path,
        testmode,
        **options,
    ):
        try:
            if url and path or not (url or path):
                raise PublisherError('Необходимо указать или url, или path!')

            self.stdout.write('Запуск обновления пакета по схемам ГАР')

            repo_manager = RepoManager(testmode)
            repo = repo_manager.repo

            self.stdout.write('1/7 Получение схем...')
            if url:
                gar_schema_manager = DownloadGARSchemaManager(url, repo)

            elif path:
                gar_schema_manager = ArchiveGARSchemaManager(path, repo)

            gar_schema_manager.process_schemas()
            if not gar_schema_manager.has_schema_changes():
                # по схемам не было изменений, прекращаем работу
                raise PublisherError('Изменения в формате ГАР не найдены')

            self.stdout.write('2/7 Генерация моделей...')
            call_command(
                'gar_generate_base_models',
                dst=settings.GAR_BASE_DIR / 'base_models.py',
            )

            self.stdout.write('3/7 Проверка моделей...')
            call_command('gar_check_models')

            self.stdout.write('4/7 Создание и применение миграций...')
            call_command('makemigrations', 'm3_gar')
            call_command('migrate', 'm3_gar')

            self.stdout.write('5/7 Добавление новых файлов в репозиторий...')
            repo_manager.index_add()

            self.stdout.write('6/7 Обновление версии и лога изменений...')
            preparer = ReleasePreparer()
            preparer.prepare()
            new_version = preparer.new_version_str

            self.stdout.write('7/7 Обновление репозитория...')
            repo_manager.save_changes(new_version)

            self.stdout.write('Обновление репозитория новыми схемами ГАР выполнено успешно')

        except PublisherError as e:
            self.stderr.write(str(e))
