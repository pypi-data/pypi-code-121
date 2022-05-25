from typing import (
    Optional,
)

from docker.models.containers import (
    Container,
)
from docker.models.images import (
    Image,
)

from botoolkit.core.services import (
    DockerServiceManager,
)


class PostgresServiceManager(DockerServiceManager):
    """
    Менеджер для управления сервисом Postgres
    """

    def run(
        self,
        image: Image,
        container_name: str,
        pg_data: str,
        db: str,
        user: str,
        password: str,
        max_connections: int,
        shared_buffers: str,
        temp_buffers: str,
        work_mem: str,
        maintenance_work_mem: str,
        track_activities: str,
        track_counts: str,
        autovacuum: str,
        wal_level: str,
        archive_mode: str,
        max_wal_senders: str,
        max_replication_slots: int,
        checkpoint_completion_target: str,
        random_page_cost: str,
        default_text_search_config: str,
        port: Optional[str] = None,
        build_dir_path: Optional[str] = None,
        shm_size: str = '2G',
        cpu_max_count: int = 3,
    ) -> Container:
        """
        Запуск контейнера с Postgres
        """
        ports = {}

        if port:
            ports['5432/tcp'] = port

        environment = {
            'PGDATA': pg_data,
            'POSTGRES_DB': db,
            'POSTGRES_USER': user,
            'POSTGRES_PASSWORD': password,
        }

        command = (
            f'postgres -c shared_buffers={shared_buffers} '
            f'-c max_connections={max_connections} '
            f'-c temp_buffers={temp_buffers} '
            f'-c work_mem={work_mem} '
            f'-c maintenance_work_mem={maintenance_work_mem} '
            f'-c track_activities={track_activities} '
            f'-c track_counts={track_counts} '
            f'-c autovacuum={autovacuum} '
            f'-c wal_level={wal_level} '
            f'-c archive_mode={archive_mode} '
            f'-c max_wal_senders={max_wal_senders} '
            f'-c max_replication_slots={max_replication_slots} '
            f'-c track_activities={track_activities} '
            f'-c track_counts={track_counts} '
            f'-c checkpoint_completion_target={checkpoint_completion_target} '
            f'-c random_page_cost={random_page_cost} '
            f'-c default_text_search_config={default_text_search_config}'
        )

        self._container = self._docker_client.containers.run(
            image=image,
            command=command,
            cpuset_cpus=f'0,{cpu_max_count}',
            detach=True,
            name=container_name,
            network=self._network,
            ports=ports,
            shm_size=shm_size,
            environment=environment,
        )

        return self._container
