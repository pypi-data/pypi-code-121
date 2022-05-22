import signal
import sys

import docker
from docker import (
    DockerClient,
)
from docker.errors import (
    APIError,
    ImageNotFound,
)

from botoolkit.core.loggers import (
    logger,
)


class ClearArgumentMixin:
    """
    Добавляет параметр --clear в команду
    """
    def get_parser(self, prog_name):
        parser = super().get_parser(
            prog_name=prog_name,
        )

        parser.add_argument(
            '--clear',
            dest='clear',
            action='store_true',
            default=False,
            help='Зачистить старый конфигурационный файл и заполнить его значениями по умолчанию.',
        )

        return parser


class DockerServiceMixin:
    """
    Применяется для команд, работающих с Docker-сервисами
    """

    def __init__(
        self,
        *args,
        **kwargs,
    ):
        try:
            self._docker_client: DockerClient = docker.from_env(
                timeout=5400,
            )
        except Exception as e:
            logger.write('Docker not found on the local machine. Part of functionality will be unavailable!\n')

        # Префикс для запускаемых контейнеров с сервисами в рамках команды
        self._container_prefix = self.get_container_prefix()

        super().__init__(
            *args,
            **kwargs,
        )

    def get_container_prefix(self) -> str:
        """
        Возвращает префикс запускаемых контейнеров
        """
        return ''

    def _remove_container(
        self,
        container_id: str,
        with_prefix: bool = True,
    ):
        """
        Удаление контейнера
        """
        if with_prefix:
            container_id = f'{self._container_prefix}{container_id}'

        try:
            container = self._docker_client.containers.get(
                container_id=container_id,
            )
        except APIError:
            logger.write(
                f'container with id {container_id} for removing '
                f'not found\n'
            )
        else:
            container.remove(
                v=True,
                force=True,
            )

            logger.write(
                f'container with id "{container_id}" was removed.\n'
            )

    def _remove_image(
        self,
        name: str,
    ):
        try:
            self._docker_client.images.remove(
                image=name,
                force=True,
            )
        except ImageNotFound:
            logger.write(
                f'image with name {name} for removing not found\n'
            )

    def _remove_artefacts(self):
        """
        Метод удаления артефактов работы с Docker-сервисами
        """


class RemoveArtefactsOnAbortMixin:
    def _register_signals(self):
        """
        Регистрация обработчиков на случай KILL и пр.
        """

        def signal_handler(n, s):
            """
            Обработчик сигнала
            """
            self._remove_artefacts()
            sys.exit(f'Received signal {n:d}')

        signals = (
            signal.SIGHUP,
            signal.SIGTERM,
            signal.SIGINT,
        )

        for s in signals:
            signal.signal(s, signal_handler)
