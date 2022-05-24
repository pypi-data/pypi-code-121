import socket
import time
from distutils.util import (
    strtobool,
)
from typing import (
    Optional,
)

import psycopg2
from docker.errors import (
    APIError,
    ImageNotFound,
    NotFound,
)
from docker.models.containers import (
    Container,
)

from botoolkit.bo_barsdock.enums import (
    ContainerStatusEnum,
)
from botoolkit.bo_postgres.services import (
    PostgresServiceManager,
)
from botoolkit.bo_postgres.strings import (
    PORT_ALREADY_USED_ERROR,
    WRONG_POSTGRES_CPU_MAX_COUNT_VALUE_ERROR,
)
from botoolkit.core.enums import (
    MemoryDimensionEnum,
)
from botoolkit.core.loggers import (
    logger,
)
from botoolkit.core.strings import (
    ARGUMENT_VALUE_WITHOUT_DIMENSION_ERROR,
)


class PostgresContainerNameArgumentsMixin:
    """
    Добавляет параметры
        - postgres_container_name
    """

    def patch_arguments_schema(self):
        super().patch_arguments_schema()

        self._arguments_schema.append(
            {
                'section': 'postgres',
                'option': 'container_name',
                'help': 'Имя контейнера с Postgres.',
            },
        )


class PostgresArgumentsMixin(PostgresContainerNameArgumentsMixin):
    """
    Добавляет параметры
        - postgres_image
        - postgres_container_name
        - postgres_port
        - postgres_db
        - postgres_user
        - postgres_password
        - postgres_pgdata
        - postgres_shared_buffers
        - postgres_temp_buffers
        - postgres_work_mem
        - postgres_maintenance_work_mem
        - postgres_track_activities
        - postgres_track_counts
        - postgres_autovacuum
        - postgres_wal_level
        - postgres_archive_mode
        - postgres_max_wal_senders
        - postgres_checkpoint_completion_target
        - postgres_random_page_cost
        - postgres_default_text_search_config
    """

    def patch_arguments_schema(self):
        super().patch_arguments_schema()

        self._arguments_schema.extend(
            (
                {
                    'section': 'postgres',
                    'option': 'image',
                    'help': 'Имя образа Postgres. Для примера, postgres:13.3.',
                },
                {
                    'section': 'postgres',
                    'option': 'port',
                    'help': 'Расшариваемый из контейнера с Postgres порт.',
                },
                {
                    'section': 'postgres',
                    'option': 'shm_size',
                    'help': 'Размер shm контейнера с Postgres.',
                },
                {
                    'section': 'postgres',
                    'option': 'cpu_max_count',
                    'help': 'Максимальное количество ядер процессора используемых контейнером Postgres.',
                },
                {
                    'section': 'postgres',
                    'option': 'db',
                    'help': 'Наименование базы данных в Postgres.',
                },
                {
                    'section': 'postgres',
                    'option': 'user',
                    'help': 'Имя пользователя для доступа к БД в Postgres.',
                },
                {
                    'section': 'postgres',
                    'option': 'password',
                    'help': 'Пароль пользователя для доступа к БД в Postgres.',
                },
                {
                    'section': 'postgres',
                    'option': 'pgdata',
                    'help': 'Абсолютный путь к директории с данными Postgres PGDATA в контейнере.',
                },
                {
                    'section': 'postgres',
                    'option': 'max_connections',
                    'help': 'Значение параметра max_connections Postgres.',
                },
                {
                    'section': 'postgres',
                    'option': 'shared_buffers',
                    'help': 'Значение параметра shared_buffers Postgres. Используйте MB или GB.',
                },
                {
                    'section': 'postgres',
                    'option': 'temp_buffers',
                    'help': 'Значение параметра temp_buffers config Postgres. Используйте MB или GB.',
                },
                {
                    'section': 'postgres',
                    'option': 'work_mem',
                    'help': (
                        'Postgres work_mem config parameter. Use MB and GB.'
                    ),
                },
                {
                    'section': 'postgres',
                    'option': 'maintenance_work_mem',
                    'help': 'Значение параметра maintenance_work config Postgres. Используйте MB или GB.',
                },
                {
                    'section': 'postgres',
                    'option': 'track_activities',
                    'help': 'Значение параметра track_activities Postgres.',
                },
                {
                    'section': 'postgres',
                    'option': 'track_counts',
                    'help': 'Значение параметра track_counts Postgres.',
                },
                {
                    'section': 'postgres',
                    'option': 'autovacuum',
                    'help': 'Значение параметра autovacuum Postgres.',
                },
                {
                    'section': 'postgres',
                    'option': 'wal_level',
                    'help': 'Значение параметра wal_level Postgres.',
                },
                {
                    'section': 'postgres',
                    'option': 'archive_mode',
                    'help': 'Значение параметра archive_mode Postgres.',
                },
                {
                    'section': 'postgres',
                    'option': 'max_wal_senders',
                    'help': 'Значение параметра max_wal_senders Postgres.',
                },
                {
                    'section': 'postgres',
                    'option': 'max_replication_slots',
                    'help': 'Значение параметра max_replication_slots Postgres.'
                },
                {
                    'section': 'postgres',
                    'option': 'checkpoint_completion_target',
                    'help': 'Значение параметра checkpoint_completion_target Postgres.',
                },
                {
                    'section': 'postgres',
                    'option': 'random_page_cost',
                    'help': 'Значение параметра random_page_cost Postgres.',
                },
                {
                    'section': 'postgres',
                    'option': 'default_text_search_config',
                    'help': 'Значение параметра default_text_search_config Postgres.',
                },
            )
        )

    def _validate_argument_with_dimension_value(
        self,
        argument_name: str,
    ):
        """
        Валидация параметров с единицами измерения
        """
        argument_value = getattr(
            self._parsed_args,
            argument_name,
        )

        if argument_value:
            with_dimension = (
                MemoryDimensionEnum.ends_with_dimension(
                    value=argument_value,
                )
            )

            if not with_dimension:
                raise RuntimeError(
                    ARGUMENT_VALUE_WITHOUT_DIMENSION_ERROR.format(
                        argument_name=argument_name,
                    )
                )

    def _validate_postgres_shared_buffers(self):
        """
        Валидация значения параметра postgres_shared_buffers
        """
        self._validate_argument_with_dimension_value(
            argument_name='postgres_shared_buffers',
        )

    def _validate_postgres_temp_buffers(self):
        """
        Валидация значения параметра postgres_temp_buffers
        """
        self._validate_argument_with_dimension_value(
            argument_name='postgres_temp_buffers',
        )

    def _validate_postgres_work_mem(self):
        """
        Валидация значения параметра postgres_work_mem
        """
        self._validate_argument_with_dimension_value(
            argument_name='postgres_work_mem',
        )

    def _validate_postgres_maintenance_work_mem(self):
        """
        Валидация значения параметра postgres_maintenance_work_mem
        """
        self._validate_argument_with_dimension_value(
            argument_name='postgres_maintenance_work_mem',
        )

    def _validate_postgres_cpu_max_count(self):
        """
        Валидация значения параметра postgres_cpu_max_count
        """
        if self._parsed_args.postgres_cpu_max_count:
            if self._parsed_args.postgres_cpu_max_count.isdigit():
                if int(self._parsed_args.postgres_cpu_max_count) <= 0:
                    raise RuntimeError(
                        WRONG_POSTGRES_CPU_MAX_COUNT_VALUE_ERROR
                    )
            else:
                raise RuntimeError(
                    WRONG_POSTGRES_CPU_MAX_COUNT_VALUE_ERROR
                )


class PostgresServiceCommandMixin:
    """
    Миксин для создания команд с работой с сервисом Postgres
    """

    def __init__(
        self,
        *args,
        **kwargs,
    ):
        self._postgres_container: Optional[Container] = None
        self._postgres_manager: Optional[PostgresServiceManager] = None

        super().__init__(
            *args,
            **kwargs,
        )

    def get_parser(
        self,
        prog_name,
    ):
        parser = super().get_parser(
            prog_name=prog_name,
        )

        parser.add_argument(
            '--pull_postgres_image',
            dest='pull_postgres_image',
            action='store',
            default=True,
            type=lambda x: bool(strtobool(x)),
            help=(
                'Нужно вытянуть последнюю версию образа Postgres перед запуском контейнера. Если указан False, то '
                'поиск образа будет производиться на хостовой машине. Значение по умолчанию: True.'
            ),
        )

        return parser

    def _check_postgres_activity(self):
        """
        Проверка активности Postgres для дальнейшей с ним работы
        """
        is_active = False

        try:
            connection = psycopg2.connect(
                f"host='127.0.0.1' "
                f"port='{self._parsed_args.postgres_port}' "
                f"dbname='{self._parsed_args.postgres_db}' "
                f"user='{self._parsed_args.postgres_user}' "
                f"password='{self._parsed_args.postgres_password}' "
                f"connect_timeout=1"
            )

            connection.close()

            is_active = True
        except Exception:
            pass

        return is_active

    def _is_port_in_use(self, port):
        """
        Проверка использования порта
        """
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(('localhost', port)) == 0

    def _remove_artefacts(self):
        self._remove_container(
            container_id=self._parsed_args.postgres_container_name,
        )

    def _get_postgres_container_name(self):
        """
        Возвращает имя контейнера с Postgres
        """
        return (
            f'{self._container_prefix}{self._parsed_args.postgres_container_name}'
        )

    def _check_postgres_port(self):
        """
        Проверяет использование порта
        """
        if self._is_port_in_use(int(self._parsed_args.postgres_port)):
            raise RuntimeError(
                PORT_ALREADY_USED_ERROR.format(self._parsed_args.postgres_port)
            )

    def _start_postgres_container(self):
        """
        Выполняет поиск ранее созданного контейнера и запускает его, если порт свободен
        """
        try:
            container = self._docker_client.containers.get(
                container_id=self._get_postgres_container_name(),
            )

            if container.status == ContainerStatusEnum.EXITED.value:
                self._check_postgres_port()
                container.start()
                logger.write(f'postgres container with name "{container.name}" started..\n')
            elif container.status == ContainerStatusEnum.RUNNING.value:
                logger.write(f'postgres container with name "{container.name}" already running..\n')
        except (
            NotFound,
            APIError,
        ):
            self._run_postgres_container()

    def _run_postgres_container(
        self,
        *args,
        **kwargs,
    ):
        """
        Запуск контейнера с Postgres
        """
        self._check_postgres_port()

        self._postgres_manager = PostgresServiceManager(
            docker_client=self._docker_client,
            network=self._parsed_args.docker_network,
        )

        image_items = self._parsed_args.postgres_image.split(':')
        image_repository = ':'.join(image_items[:-1])
        image_tag = image_items[-1]

        if self._parsed_args.pull_postgres_image:
            image = self._postgres_manager.pull(
                image_repository=image_repository,
                image_tag=image_tag,
            )
        else:
            image = self._postgres_manager.get_image(
                image_repository=image_repository,
                image_tag=image_tag,
            )

        self._postgres_container = self._postgres_manager.run(
            image=image,
            container_name=self._get_postgres_container_name(),
            pg_data=self._parsed_args.postgres_pgdata,
            db=self._parsed_args.postgres_db,
            user=self._parsed_args.postgres_user,
            password=self._parsed_args.postgres_password,
            max_connections=self._parsed_args.postgres_max_connections,
            shm_size=self._parsed_args.docker_shm_size,
            cpu_max_count=self._parsed_args.docker_cpu_max_count,
            shared_buffers=self._parsed_args.postgres_shared_buffers,
            temp_buffers=self._parsed_args.postgres_temp_buffers,
            work_mem=self._parsed_args.postgres_work_mem,
            maintenance_work_mem=self._parsed_args.postgres_maintenance_work_mem,
            track_activities=self._parsed_args.postgres_track_activities,
            track_counts=self._parsed_args.postgres_track_counts,
            autovacuum=self._parsed_args.postgres_autovacuum,
            wal_level=self._parsed_args.postgres_wal_level,
            max_replication_slots=self._parsed_args.postgres_max_replication_slots,
            archive_mode=self._parsed_args.postgres_archive_mode,
            max_wal_senders=self._parsed_args.postgres_max_wal_senders,
            checkpoint_completion_target=(
                self._parsed_args.postgres_checkpoint_completion_target
            ),
            random_page_cost=self._parsed_args.postgres_random_page_cost,
            default_text_search_config=(
                self._parsed_args.postgres_default_text_search_config
            ),
            port=self._parsed_args.postgres_port,
        )

        while not self._check_postgres_activity():
            logger.write('waiting for Postgres to start. sleep 5 seconds..\n')
            time.sleep(5)

        logger.write(
            f'container with Postgres was created successfully with params: '
            f'@short_id="{self._postgres_container.short_id}" '
            f'@name="{self._postgres_container.name}" '
            f'@image="{self._postgres_container.image}" '
            f'@status="{self._postgres_container.status}"\n'
        )

    def _stop_postgres_container(
        self,
        timeout=180,
    ):
        """
        Остановка контейнера с Postgres с заданным временем ожидания
        """
        logger.write(
            f'stopping Postgres container {self._postgres_container.name}..\n'
        )

        self._postgres_container.stop(
            timeout=timeout,
        )

        stopping_result = self._postgres_container.wait(
            timeout=timeout,
        )

        logger.write(
            f'stopping Postgres container{self._postgres_container.name} was '
            f'finished with result "{stopping_result}"\n'
        )

    def _push_postgres_image(
        self,
        stream: bool = False,
        tag: str = 'latest',
    ) -> str:
        image_repository = (
            f'web-bb-db-{self._parsed_args.databaser_build_region_abbreviation}-'
            f'{self._parsed_args.databaser_build_task_id}'
        ).lower()

        full_image_repository = (
            f'{self._parsed_args.registry_url}/{image_repository}' if
            self._parsed_args.registry_url else
            image_repository
        ).lower()

        self._stop_postgres_container()

        logger.write(
            'committing Postgres container..\n'
        )
        self._postgres_container.commit(
            repository=full_image_repository,
            tag=tag,
        )

        self._postgres_manager.push(
            image_repository=image_repository,
            image_tag=tag,
            registry_url=self._parsed_args.registry_url,
            stream=stream,
        )

        if self._parsed_args.remove_result_db_image:
            try:
                self._docker_client.images.remove(
                    image=f'{full_image_repository}:{tag}',
                    force=True,
                )

                logger.write(
                    f'image with name {full_image_repository}:{tag} was '
                    f'dropped.\n'
                )
            except ImageNotFound as e:
                logger.write(f'{e}\n')

        return full_image_repository
