import uuid

from botoolkit.core.strings import (
    KEY_COLUMN_VALUES_ARE_NOT_INTEGER_ERROR,
)


class DatabaserGeneralArgumentsMixin:
    """
    Добавляет параметры
        --databaser_general_result_configuration_dir_path
    """

    def patch_arguments_schema(self):
        super().patch_arguments_schema()

        self._arguments_schema.extend(
            (
                {
                    'section': 'databaser_general',
                    'option': 'result_configuration_dir_path',
                    'help': (
                        'Абсолютный путь до директории, куда нужно генерировать конфигурационный файл для запуска '
                        'Databaser в режиме разработки'
                    ),
                },
            )
        )


class DatabaserDstDBArgumentsMixin:
    """
    Добавляет параметры
        --databaser_dst_db_host
        --databaser_dst_db_port
        --databaser_dst_db_name
        --databaser_dst_db_user
        --databaser_dst_db_password
    """

    def patch_arguments_schema(self):
        super().patch_arguments_schema()

        self._arguments_schema.extend(
            (
                {
                    'section': 'databaser',
                    'option': 'dst_db_host',
                    'help': 'IP-адрес машины или имя сервиса с целевой базой данных.',
                },
                {
                    'section': 'databaser',
                    'option': 'dst_db_port',
                    'help': 'Порт для доступа к целевой базе данных.',
                },
                {
                    'section': 'databaser',
                    'option': 'dst_db_name',
                    'help': 'Имя целевой базы данных.',
                },
                {
                    'section': 'databaser',
                    'option': 'dst_db_user',
                    'help': 'Пользователь в целевой базе данных.',
                },
                {
                    'section': 'databaser',
                    'option': 'dst_db_password',
                    'help': 'Пароль пользователя в целевой базе данных.',
                },
            )
        )


class DatabaserArgumentsMixin:
    """
    Добавляет параметры
        --databaser_log_level
        --databaser_test_mode
        --databaser_src_db_host
        --databaser_src_db_port
        --databaser_src_db_name
        --databaser_src_db_user
        --databaser_src_db_password
        --databaser_key_table_name
        --databaser_key_column_names
        --databaser_key_column_values
        --databaser_key_table_hierarchy_column_name
        --databaser_excluded_tables
        --databaser_tables_limit_per_transaction
        --databaser_tables_with_generic_foreign_key
        --databaser_tables_truncate_excluded
        --databaser_is_truncate_tables
        --databaser_tables_truncate_included
        --databaser_tables_truncate_excluded
        --databaser_full_transfer_tables
    """

    def patch_arguments_schema(self):
        super().patch_arguments_schema()

        self._arguments_schema.extend(
            (
                {
                    'section': 'databaser',
                    'option': 'log_level',
                    'help': (
                        'Уровень логирования. Допустимые значения: NOTSET, DEBUG, INFO, WARNING, ERROR, CRITICAL. '
                        'Значение по умолчанию: INFO.'
                    ),
                },
                {
                    'section': 'databaser',
                    'option': 'test_mode',
                    'help': (
                        'Databaser работает в тестовом режиме. В тестовом режиме контейнер с целевой базой данных не '
                        'удаляется. По умолчанию: False.'
                    ),
                },
                {
                    'section': 'databaser',
                    'option': 'src_db_host',
                    'help': 'IP-адрес или наименование сервиса с базой донором.',
                },
                {
                    'section': 'databaser',
                    'option': 'src_db_port',
                    'help': 'Порт для доступа к базе донору.',
                },
                {
                    'section': 'databaser',
                    'option': 'src_db_name',
                    'help': 'Имя базы данных донора.',
                },
                {
                    'section': 'databaser',
                    'option': 'src_db_user',
                    'help': 'Пользователь базы данных донора.',
                },
                {
                    'section': 'databaser',
                    'option': 'src_db_password',
                    'help': 'Пароль пользователя базы данных донора.',
                },
                {
                    'section': 'databaser',
                    'option': 'key_table_name',
                    'help': 'Имя ключевой таблицы, которая будет в основе среза данных.',
                },
                {
                    'section': 'databaser',
                    'option': 'key_column_names',
                    'help': (
                        'Имя ключевого поля. Если наименований несколько, то они должны быть перечислены через запятую.'
                    ),
                },
                {
                    'section': 'databaser',
                    'option': 'key_column_values',
                    'help': 'Идентификаторы записей ключевой таблицы.',
                },
                {
                    'section': 'databaser',
                    'option': 'key_table_hierarchy_column_name',
                    'help': 'Имя колонки ключевой таблицы служащей для построения иерархию.',
                },
                {
                    'section': 'databaser',
                    'option': 'excluded_tables',
                    'help': (
                        'Перечисление таблиц через запятую, без пробелов, исключаемых для переноса данных в целевую БД.'
                    ),
                },
                {
                    'section': 'databaser',
                    'option': 'tables_limit_per_transaction',
                    'help': (
                        'Ограничение по количеству обрабатываемых таблиц в одной транзакции. Например, при очистке '
                        'таблиц.'
                    ),
                },
                {
                    'section': 'databaser',
                    'option': 'tables_with_generic_foreign_key',
                    'help': 'Таблицы с Generic Foreign Key.',
                },
                {
                    'section': 'databaser',
                    'option': 'is_truncate_tables',
                    'help': 'Необходимо зачищать таблицы перед переносом данных.',
                },
                {
                    'section': 'databaser',
                    'option': 'tables_truncate_included',
                    'help': 'Таблицы предназначенные для зачистки перед переносом данных.',
                },
                {
                    'section': 'databaser',
                    'option': 'tables_truncate_excluded',
                    'help': 'Таблицы исключаемые от зачистки перед переносом данных.',
                },
                {
                    'section': 'databaser',
                    'option': 'full_transfer_tables',
                    'help': 'Таблицы для полного переноса данных.',
                },
            )
        )

    def _validate_databaser_key_column_values(self):
        """
        Валидация значения параметра databaser_key_column_values
        """
        if self._parsed_args.databaser_key_column_values:
            ids = (
                self._parsed_args.databaser_key_column_values.strip().replace(' ', '').split(',')
            )

            if not all(map(lambda x: x.isdigit(), ids)):
                raise RuntimeError(KEY_COLUMN_VALUES_ARE_NOT_INTEGER_ERROR)

    def _validate_databaser_excluded_tables(self):
        """
        Валидация значения параметра databaser_excluded_tables. Всегда должно
        быть указано значение по умолчанию
        """
        if not self._parsed_args.databaser_excluded_tables:
            bodatabaser_config = getattr(self, '_bodatabaser_config', None)

            if bodatabaser_config:
                self._parsed_args.databaser_excluded_tables = bodatabaser_config.get(
                    section='databaser',
                    option='excluded_tables',
                ).value

    def _fill_databaser_key_column_names(
        self,
        value: str,
    ):
        """
        Заполнение значения параметра databaser_key_column_names в
        конфигурационный файл
        """
        value = (
            value or
            self._config.get(
                section='databaser',
                option='key_column_names',
            ).value
        )

        if value:
            column_names = set(
                filter(
                    None,
                    value.strip().replace(' ', '').split(',')
                )
            )
            value = ','.join(sorted(column_names))

        self._config.set(
            section='databaser',
            option='key_column_names',
            value=value,
        )

    def _fill_databaser_excluded_tables(
        self,
        value: str,
    ):
        """
        Заполнение значения параметра databaser_excluded_tables
        """
        value = (
            value or
            self._config.get(
                section='databaser',
                option='excluded_tables',
            ).value
        )

        if value:
            excluded_tables = set(
                filter(
                    None,
                    value.strip().replace(' ', '').split(',')
                )
            )

            databaser_excluded_tables = self._config.get(
                section='databaser',
                option='excluded_tables',
            ).value

            if databaser_excluded_tables:
                databaser_excluded_tables = set(
                    filter(
                        None,
                        databaser_excluded_tables.strip().replace(' ', '').split(',')
                    )
                )

                excluded_tables = excluded_tables.union(
                    databaser_excluded_tables
                )

            bodatabaser_config = getattr(self, '_bodatabaser_config', None)

            if bodatabaser_config:
                default_databaser_excluded_tables = bodatabaser_config.get(
                    section='databaser',
                    option='excluded_tables',
                ).value

                # В исключаемых таблицах должны всегда находиться таблицы
                # bodatabaser, т.к. они не нужны всегда
                if default_databaser_excluded_tables:
                    default_databaser_excluded_tables = set(
                        filter(
                            None,
                            default_databaser_excluded_tables.strip().replace(' ', '').split(',')
                        )
                    )

                    excluded_tables = excluded_tables.union(
                        default_databaser_excluded_tables
                    )

            value = ','.join(sorted(excluded_tables))

        self._config.set(
            section='databaser',
            option='excluded_tables',
            value=value,
        )

    def _fill_databaser_full_transfer_tables(
        self,
        value: str,
    ):
        """
        Заполнение значения параметра databaser_full_transfer_tables
        """
        value = (
            value or
            self._config.get(
                section='databaser',
                option='full_transfer_tables',
            ).value
        )

        if value:
            full_transfer_tables = set(
                filter(
                    None,
                    value.strip().replace(' ', '').split(',')
                )
            )

            databaser_full_transfer_tables = self._config.get(
                section='databaser',
                option='full_transfer_tables',
            ).value

            if databaser_full_transfer_tables:
                databaser_full_transfer_tables = set(
                    filter(
                        None,
                        databaser_full_transfer_tables.strip().replace(' ', '').split(',')
                    )
                )

                full_transfer_tables = full_transfer_tables.union(
                    databaser_full_transfer_tables
                )

            bodatabaser_config = getattr(self, '_bodatabaser_config', None)

            if bodatabaser_config:
                default_databaser_full_transfer_tables = bodatabaser_config.get(
                    section='databaser',
                    option='full_transfer_tables',
                ).value

                if default_databaser_full_transfer_tables:
                    default_databaser_full_transfer_tables = set(
                        filter(
                            None,
                            default_databaser_full_transfer_tables.strip().replace(' ', '').split(',')
                        )
                    )

                    full_transfer_tables = full_transfer_tables.union(
                        default_databaser_full_transfer_tables
                    )

            value = ','.join(sorted(full_transfer_tables))

        self._config.set(
            section='databaser',
            option='full_transfer_tables',
            value=value,
        )


class DatabaserWithDstDBArgumentsMixin(
    DatabaserArgumentsMixin,
    DatabaserDstDBArgumentsMixin,
):
    """
    Добавляет параметры
        --databaser_log_level
        --databaser_test_mode
        --databaser_src_db_host
        --databaser_src_db_port
        --databaser_src_db_name
        --databaser_src_db_user
        --databaser_src_db_password
        --databaser_dst_db_host
        --databaser_dst_db_port
        --databaser_dst_db_name
        --databaser_dst_db_user
        --databaser_dst_db_password
        --databaser_key_table_name
        --databaser_key_column_names
        --databaser_key_column_values
        --databaser_key_table_hierarchy_column_name
        --databaser_excluded_tables
        --databaser_tables_limit_per_transaction
        --databaser_tables_with_generic_foreign_key
        --databaser_tables_truncate_excluded
        --databaser_is_truncate_tables
        --databaser_tables_truncate_included
        --databaser_tables_truncate_excluded
    """


class DatabaserBuildContainerNameArgumentsMixin:
    """
    Добавляет параметры
        --databaser_container_name
    """

    def patch_arguments_schema(self):
        super().patch_arguments_schema()

        self._arguments_schema.extend(
            (
                {
                    'section': 'databaser_build',
                    'option': 'container_name',
                    'help': 'Имя контейнера, в котором будет запускаться Databaser.',
                },
            )
        )


class DatabaserBuildArgumentsMixin(DatabaserBuildContainerNameArgumentsMixin):
    """
    Добавляет параметры
        --databaser_build_image
        --databaser_build_container_name
        --databaser_build_mem_limit
        --databaser_build_shm_size
        --databaser_build_region_abbreviation
        --databaser_build_task_id
    """

    def patch_arguments_schema(self):
        super().patch_arguments_schema()

        self._arguments_schema.extend(
            (
                {
                    'section': 'databaser_build',
                    'option': 'image',
                    'help': 'Имя образа Datatabaser.',
                },
                {
                    'section': 'databaser_build',
                    'option': 'mem_limit',
                    'help': 'Ограничение по используемой памяти контейнером Databaser.',
                },
                {
                    'section': 'databaser_build',
                    'option': 'shm_size',
                    'help': 'Размер shm в контейнере Databaser.',
                },
                {
                    'section': 'databaser_build',
                    'option': 'region_abbreviation',
                    'help': 'Аббревиатура региона.',
                },
                {
                    'section': 'databaser_build',
                    'option': 'task_id',
                    'help': 'Номер задачи в Jira, для которой будет осуществляться сборка среза данных.',
                },
            )
        )

    def _fill_databaser_build_task_id(
        self,
        value: str,
    ):
        """
        Проставление значения параметра databaser_build_task_id
        """
        if value:
            value = value.lower()
        else:
            value = f'task-{uuid.uuid4().hex[:8]}'

        self._config.set(
            section='databaser_build',
            option='task_id',
            value=value.lower(),
        )
