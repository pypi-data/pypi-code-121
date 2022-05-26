from django.contrib.contenttypes.models import (
    ContentType,
)
from django.core.management import (
    BaseCommand,
)
from django.db import (
    connection,
)

from web_bb import (
    logger,
)


class Command(BaseCommand):

    def handle(self, *args, **options):
        """
        Создание и заполнение таблицы django_content_type_table для
        получения наименования таблицы по content_type_id
        """
        create_table_sql = (
            """
            create table if not exists django_content_type_table
            (
                id serial not null constraint django_content_type_table_pkey primary key,
                table_name varchar(255) not null,
                app_label varchar(100) not null,
                model varchar(100) not null
            );
            """
        )

        set_owner_sql = (
            """
            alter table if exists django_content_type_table
            owner to bars_web_bb;
            """
        )

        truncate_table = (
            """
            truncate django_content_type_table;
            """
        )

        insert_row_sql = (
            """
            insert into django_content_type_table (table_name, app_label, model)
            values ('{table_name}', '{app_label}', '{model}')
            """
        )

        wrong_content_type_ids = []

        with connection.cursor() as cursor:
            cursor.execute(
                create_table_sql
            )

            cursor.execute(
                set_owner_sql
            )

            cursor.execute(
                truncate_table
            )

            content_types = ContentType.objects.all()

            if not content_types.exists():
                print('content types does not exists')

            for c_t in content_types.iterator():
                model = c_t.model_class()

                if model:
                    table_name = model._meta.db_table

                    insert_sql = insert_row_sql.format(
                        table_name=table_name,
                        app_label=c_t.app_label,
                        model=c_t.model,
                    )

                    cursor.execute(
                         insert_sql
                    )
                else:
                    wrong_content_type_ids.append(
                        c_t.id
                    )

            print(wrong_content_type_ids)
