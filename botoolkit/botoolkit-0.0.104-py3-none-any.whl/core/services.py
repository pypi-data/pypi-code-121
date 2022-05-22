from typing import (
    Optional,
)

from docker import (
    DockerClient,
)
from docker.models.images import (
    Image,
)

from botoolkit.core.loggers import (
    logger,
)


class DockerServiceManager:
    """
    Базовый класс для создания менеджера сервисов завернутого в контейнер
    """

    def __init__(
        self,
        docker_client: DockerClient,
        network:str,
    ):
        self._docker_client = docker_client
        self._network = network

    @property
    def full_repository_name(self):
        """
        Возвращает полное имя репозитория с адресом Registry
        """
        name = (
            f'{self._registry_url}/{self._image_repository}' if
            self._registry_url else
            self._image_repository
        )

        return name

    @property
    def image_name(self):
        return f'{self.full_repository_name}:{self._image_tag}'

    def get_image(
        self,
        image_repository: Optional[str] = None,
        image_tag: Optional[str] = None,
        registry_url: Optional[str] = None,
    ) -> Image:
        """
        Метод поиска образа на хостовой машине
        """
        image_name = (
            f'{registry_url}/{image_repository}:{image_tag}' if
            registry_url else
            f'{image_repository}:{image_tag}'
        )

        image = self._docker_client.images.get(image_name)

        return image

    def pull(
        self,
        image_repository: str,
        image_tag: str,
        registry_url: Optional[str] = None,
    ) -> Image:
        """
        Метод скачивания последней версии образа сервиса из репозитория
        """
        image_name = (
            f'{registry_url}/{image_repository}:{image_tag}' if
            registry_url else
            f'{image_repository}:{image_tag}'
        )

        logger.write(
            f'pulling image {image_name}..\n'
        )

        image = self._docker_client.images.pull(image_name)

        return image

    def build(self):
        """
        Метод сборки образа сервиса
        """

    def push(
        self,
        image_repository: str,
        image_tag: str,
        registry_url: Optional[str] = None,
        stream: bool = False,
    ) -> str:
        """
        Метод загрузки локальной версии образа сервиса в репозиторий
        """
        image_name = ''

        if registry_url:
            image_repository = f'{registry_url}/{image_repository}'

            image_name = (
                f'{image_repository}:{image_tag}'
            )

            logger.write(
                f'pushing "{image_name}" image..\n'
            )

            if stream:
                for line in self._docker_client.images.push(
                    repository=image_repository,
                    tag=image_tag,
                    stream=True,
                    decode=True,
                ):
                    logger.write(
                        f'{line}\n'
                    )
            else:
                self._docker_client.images.push(
                    repository=image_repository,
                    tag=image_tag,
                )

            logger.write(
                f'image "{image_name}" was pushed.\n'
            )

        return image_name

    def run(self):
        """
        Метод для запуска контейнера с сервисом
        """
