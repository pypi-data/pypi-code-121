import os
from argparse import (
    BooleanOptionalAction,
)

from django.conf import (
    settings,
)
from django.core.management import (
    BaseCommand,
    CommandError,
)
from django.utils.translation import (
    activate,
)

from m3_gar.importer.commands import (
    auto_update_data,
    load_complete_data,
)
from m3_gar.importer.consts import (
    DEFAULT_BULK_LIMIT,
)
from m3_gar.importer.source.exceptions import (
    NoNewVersionError,
)
from m3_gar.importer.timer import (
    Timer,
)
from m3_gar.importer.version import (
    fetch_version_info,
)
from m3_gar.models import (
    Version,
)
from m3_gar.util import (
    get_table_names_from_models,
)


class Command(BaseCommand):
    help = 'Fill or update GAR database'

    def add_arguments(self, parser):
        super().add_arguments(parser)

        parser.add_argument(
            '--src',
            help=(
                "Directory or archive path or url to load into DB. "
                "Use 'auto' to load latest known version"
            ),
        )
        parser.add_argument(
            '--truncate',
            action=BooleanOptionalAction,
            default=None,
            help='Truncate tables before loading data',
        )
        parser.add_argument(
            '--no-transaction',
            action='store_true',
            default=False,
            help='Do not wrap import in transaction',
        )
        parser.add_argument(
            '--update',
            action='store_true',
            help="Update database from https://fias.nalog.ru",
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=DEFAULT_BULK_LIMIT,
            help="Limit rows for bulk operations",
        )
        parser.add_argument(
            '--tables',
            help="Comma-separated list of tables to import",
        )
        parser.add_argument(
            '--update-version-info',
            action=BooleanOptionalAction,
            default=True,
            help='Update list of available database versions from http://fias.nalog.ru',
        )
        parser.add_argument(
            '--tempdir',
            help="Path to the temporary files directory"
        )

    def handle(
        self, *args,
        src,
        truncate,
        no_transaction,
        update,
        limit,
        tables,
        update_version_info,
        tempdir,
        **options,
    ):
        Timer.init()

        # признак обновления из внешнего источника
        remote = False
        if src and src.lower() == 'auto':
            src = None
            remote = True

        tempdir = self.parse_tempdir_arg(tempdir)

        if (src or remote) and Version.objects.filter(processed=True).exists() and truncate is None:
            self.stderr.write(
                'One of the tables contains data. '
                'Truncate all GAR tables manually or use '
                '--truncate/--no-truncate option'
            )

            raise CommandError

        if update_version_info:
            fetch_version_info(update_all=True)

        # Force Russian language for internationalized projects
        if settings.USE_I18N:
            activate('ru')

        tables = self.parse_tables_arg(tables)

        if src or remote:
            load_complete_data(
                path=src,
                truncate=truncate,
                no_transaction=no_transaction,
                limit=limit,
                tables=tables,
                tempdir=tempdir,
            )

        if update:
            try:
                auto_update_data(
                    limit=limit,
                    tables=tables,
                    tempdir=tempdir,
                )
            except NoNewVersionError as e:
                self.stdout.write(str(e))

    def parse_tempdir_arg(self, tempdir):
        """
        Возвращает временную директорую
        """
        if tempdir:
            error = None

            if not os.path.exists(tempdir):
                error = f'Directory `{tempdir}` does not exists.'
            elif not os.path.isdir(tempdir):
                error = f'Path `{tempdir}` is not a directory.'
            elif not os.access(tempdir, os.W_OK):
                error = f'Directory `{tempdir}` is not writeable'

            if error:
                self.stderr.write(error)

                raise CommandError

        return tempdir

    def parse_tables_arg(self, tables):
        """
        Возвращает перечень таблиц для загрузки
        """
        tables = set(tables.split(',')) if tables else set()
        tables_from_db = get_table_names_from_models()

        if not tables.issubset(set(tables_from_db)):
            diff = ', '.join(tables.difference(tables_from_db))
            self.stderr.write(
                f'Tables `{diff}` are not of GAR schema models and can not be processed'
            )

            raise CommandError

        tables = tuple(x for x in tables_from_db if x in list(tables))

        return tables
