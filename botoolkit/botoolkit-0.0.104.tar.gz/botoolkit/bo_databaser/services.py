from docker.models.images import (
    Image,
)

from botoolkit.core.loggers import (
    logger,
)
from botoolkit.core.services import (
    DockerServiceManager,
)


class DatabaserServiceManager(DockerServiceManager):
    """
    Менеджер для управления сервисом Databaser
    """

    def run(
        self,
        image: Image,
        container_name: str,
        mem_limit: str,
        shm_size: str,
        log_level: str,
        test_mode: str,
        src_db_host: str,
        src_db_port: str,
        src_db_name: str,
        src_db_user: str,
        src_db_password: str,
        dst_db_host: str,
        dst_db_port: str,
        dst_db_name: str,
        dst_db_user: str,
        dst_db_password: str,
        key_table_name: str,
        key_column_names: str,
        key_column_values: str,
        key_table_hierarchy_column_name: str,
        excluded_tables: str,
        tables_limit_per_transaction: str,
        tables_with_generic_foreign_key: str,
        is_truncate_tables: str,
        tables_truncate_included: str,
        tables_truncate_excluded: str,
        full_transfer_tables: str,
    ):
        """
        Запуск контейнера с Databaser
        """
        environment = {
            'DATABASER_LOG_LEVEL': log_level,
            'DATABASER_SRC_DB_HOST': src_db_host,
            'DATABASER_SRC_DB_PORT': src_db_port,
            'DATABASER_SRC_DB_NAME': src_db_name,
            'DATABASER_SRC_DB_USER': src_db_user,
            'DATABASER_SRC_DB_PASSWORD': src_db_password,
            'DATABASER_DST_DB_HOST': dst_db_host,
            'DATABASER_DST_DB_PORT': dst_db_port,
            'DATABASER_DST_DB_NAME': dst_db_name,
            'DATABASER_DST_DB_USER': dst_db_user,
            'DATABASER_DST_DB_PASSWORD': dst_db_password,
            'DATABASER_KEY_TABLE_NAME': key_table_name,
            'DATABASER_KEY_COLUMN_NAMES': key_column_names,
            'DATABASER_KEY_COLUMN_VALUES': key_column_values,
            'DATABASER_KEY_TABLE_HIERARCHY_COLUMN_NAME': (
                key_table_hierarchy_column_name
            ),
            'DATABASER_TEST_MODE': test_mode,
            'DATABASER_IS_TRUNCATE_TABLES': is_truncate_tables,
            'DATABASER_TABLES_TRUNCATE_INCLUDED': tables_truncate_included,
            'DATABASER_TABLES_TRUNCATE_EXCLUDED': tables_truncate_excluded,
            'DATABASER_EXCLUDED_TABLES': excluded_tables,
            'DATABASER_TABLES_WITH_GENERIC_FOREIGN_KEY': (
                tables_with_generic_foreign_key
            ),
            'DATABASER_FULL_TRANSFER_TABLES': full_transfer_tables,
        }

        log_generator = self._docker_client.containers.run(
            image=image,
            detach=False,
            name=container_name,
            network=self._network,
            shm_size=shm_size,
            mem_limit=mem_limit,
            environment=environment,
            stream=True,
        )

        for line in log_generator:
            logger.write(line.decode('utf-8'))

        container = self._docker_client.containers.get(
            container_id=container_name,
        )

        return container
