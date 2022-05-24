from django.core.management import (
    BaseCommand,
)
from django.db import (
    connections,
    transaction,
)
from django.utils.functional import (
    partition,
)

from m3_gar import (
    config,
)
from m3_gar.importer.constraints import (
    ConstraintsEditor,
)
from m3_gar.importer.models_sort import (
    sort_models,
)
from m3_gar.models.util import (
    RegionCodeModelMixin,
)
from m3_gar.util import (
    get_models,
)


class Command(BaseCommand):
    help = 'Manage DB constraints and indexes'

    def add_arguments(self, parser):
        super().add_arguments(parser)

        parser.add_argument(
            'state',
            choices=['enable', 'disable'],
            help='Enable/disable database consistency/durability',
        )

        parser.add_argument(
            '--truncate',
            type=str,
            default=None,
            nargs='?',
            const='',
            help='Truncate all data (works only with "disable" state)',
        )
        parser.add_argument(
            '--fk',
            action='store_true',
            default=False,
            help='Perform operations for foreign key constraints',
        )
        parser.add_argument(
            '--unique',
            action='store_true',
            default=False,
            help='Perform operations for unique constraints',
        )
        parser.add_argument(
            '--index',
            action='store_true',
            default=False,
            help='Perform operations for database indexes',
        )
        parser.add_argument(
            '--logged',
            action='store_true',
            default=False,
            help='Change tables logging status',
        )
        parser.add_argument(
            '--commit',
            action='store_true',
            default=False,
            help='Commit produced SQL to the database',
        )

    def handle(
        self, *args,
        state,
        truncate,
        fk,
        unique,
        index,
        logged,
        commit,
        **kwargs,
    ):
        self.models = sort_models(get_models())
        self.sql_collected = []
        self.enable = state == 'enable'

        if not self.enable and truncate is not None:
            regions = truncate and truncate.split(',') or []
            regions = list(map(int, regions))

            self.truncate(regions)

        if any((fk, unique, index)):
            self.set_constraints(fk, unique, index)

        if logged:
            self.set_logged()

        for sql in self.sql_collected:
            self.stdout.write(sql)

        if commit:
            with transaction.atomic(using=config.DATABASE_ALIAS):
                conn = connections[config.DATABASE_ALIAS]
                with conn.cursor() as cursor:
                    for sql in self.sql_collected:
                        cursor.execute(sql)

    def truncate(self, regions):
        truncate_all = not regions
        truncate_dicts = 0 in regions

        regions_str = ','.join(str(region) for region in regions if region != 0)

        dicts, regional = partition(
            lambda m: issubclass(m, RegionCodeModelMixin),
            self.models,
        )

        if truncate_all:
            truncate_models = self.models
            delete_models = []
        else:
            if truncate_dicts:
                truncate_models = dicts
            else:
                truncate_models = []

            delete_models = regional

        for model in truncate_models:
            sql = f'TRUNCATE TABLE {model._meta.db_table} RESTART IDENTITY CASCADE;'
            self.sql_collected.append(sql)

        for model in delete_models:
            sql = f'DELETE FROM {model._meta.db_table} WHERE region_code IN ({regions_str});'
            self.sql_collected.append(sql)

    def set_constraints(self, fk, unique, index):
        constraints_editor = ConstraintsEditor(
            enable=self.enable,
            fk=fk,
            unique=unique,
            index=index,
        )

        for model in self.models:
            for sql in constraints_editor.change_model_constraints(model):
                self.sql_collected.extend(sql)

    def set_logged(self):
        logged = (
            'LOGGED'
            if self.enable
            else 'UNLOGGED'
        )

        for model in self.models:
            sql = f'ALTER TABLE {model._meta.db_table} SET {logged};'
            self.sql_collected.append(sql)
