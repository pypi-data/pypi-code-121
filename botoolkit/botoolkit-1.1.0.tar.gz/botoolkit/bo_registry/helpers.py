from abc import (
    ABC,
    abstractmethod,
)

import requests
from fabric import (
    Connection,
)
from nexuscli.nexus_client import (
    NexusClient,
)
from nexuscli.nexus_config import (
    NexusConfig,
)

from botoolkit.core.loggers import (
    logger,
)


class RegistryAuxiliaryTool:
    """
    Вспомогательный класс для работы с удаленным Registry
    """
    def __init__(
        self,
        registry_host_ip,
        registry_host_username,
        registry_container_name,
    ):
        self._registry_host_ip = registry_host_ip
        self._registry_host_username = registry_host_username
        self._registry_container_name = registry_container_name

    def _run_registry_host_command(self, command):
        """
        Запуск команды на удаленном хосте
        """
        with Connection(
            host=f'{self._registry_host_username}@{self._registry_host_ip}',
        ) as connection:
            result = connection.run(command, hide=True)

            msg = (
                'Ran {0.command!r} on {0.connection.host}..'
            )
            print(msg.format(result))

    def run_garbage_collector(self):
        """
        Запуск сборщика мусора Registry. Сборщик мусора удаляет только слои,
        но не удаляет репозитории, если они пустые
        """
        run_garbage_collector_command = (
            f'docker exec -i {self._registry_container_name} bin/registry '
            f'garbage-collect /etc/docker/registry/config.yml'
        )

        self._run_registry_host_command(run_garbage_collector_command)

    def run_remove_empty_repository(self, repository_name):
        """
        Удаление директории пустого репозитория, чтобы репозиторий больше не
        приходил в запросе /_catalog/
        """
        run_remove_empty_repository_command = (
            f'docker exec -i {self._registry_container_name} sh -c "'
            f'rm -rf /var/lib/registry/docker/registry/v2/repositories/{repository_name}"'  # noqa
        )

        self._run_registry_host_command(run_remove_empty_repository_command)


class BaseRegistryAPIClient(ABC):
    """
    Базовый класс для создания клиентов для взаимодействия с Registry
    """

    def __init__(self, registry_domain, username, password, *args, verify=True, **kwargs):
        self._registry_domain = registry_domain
        self._username = username
        self._password = password
        self._verify = verify

    @abstractmethod
    def get_repositories(self):
        """
        Метод получения списка репозиториев
        """

    @abstractmethod
    def delete_repository(self, repository_name, *args, **kwargs):
        """
        Метод удаления репозитория
        """

    def delete_repositories(
        self,
        repository_names,
        *args,
        **kwargs,
    ):
        repositories = self.get_repositories()

        for repository_name in repository_names:
            if repository_name not in repositories:
                raise ValueError(
                    'Please check repository_name parameter, repository not '
                    'found!'
                )

            self.delete_repository(
                repository_name=repository_name,
            )

            logger.write(f'repository "{repository_name}" was deleted from registry.\n')


class RegistryAPIClient(BaseRegistryAPIClient):
    """
    Клиент для работы с Registry по-средством API
    """

    def __init__(self, *args, registry_auxiliary_tool=None, **kwargs):
        super().__init__(*args, **kwargs)

        self._registry_url = f'https://{self._username}:{self._password}@{self._registry_domain}'
        self._headers = {
            'Accept': 'application/vnd.docker.distribution.manifest.v2+json',
        }
        self._registry_auxiliary_tool = registry_auxiliary_tool

    def get_repositories(self):
        """
        Получение списка репозиториев
        """
        result = []

        while True:
            catalog_url = f'{self._registry_url}/v2/_catalog/?n=100&last={result[len(result) - 1] if result else 0}'
            response = requests.get(catalog_url, verify=self._verify)

            if response.ok:
                repositories = response.json()['repositories']

                if repositories:
                    result.extend(repositories)
                else:
                    break
            else:
                break

        return result

    def get_repository_digest(self, repository_name, tag):
        """
        Получение хеша образа для дальнейшего удаления пустого репозитория
        """
        manifest_url = (
            f'{self._registry_url}/v2/{repository_name}/manifests/{tag}'
        )
        response = requests.head(
            manifest_url,
            verify=self._verify,
            headers=self._headers,
        )

        if response.ok:
            result = response.headers.get('Docker-Content-Digest'),
        else:
            result = None

        return result

    def get_repository_tags(self, repository_name):
        """
        Получение списка тегов репозитория
        """
        tags_url = f'{self._registry_url}/v2/{repository_name}/tags/list'
        response = requests.get(
            tags_url,
            verify=self._verify,
        )

        if response.ok:
            result = response.json().get('tags') or []
        else:
            result = []

        return result

    def delete_repository(self, *args, repository_name, **kwargs):
        """
        Удаление репозитория
        """
        tags = self.get_repository_tags(repository_name)

        for tag in tags:
            digest = self.get_repository_digest(
                repository_name=repository_name,
                tag=tag,
            )

            if digest:
                delete_repository_url = (
                    f'{self._registry_url}/v2/{repository_name}/manifests/{str(digest)}'
                )

                requests.delete(
                    delete_repository_url,
                    verify=self._verify,
                    headers=self._headers,
                )

        if self._registry_auxiliary_tool:
            self._registry_auxiliary_tool.run_garbage_collector()

            self._registry_auxiliary_tool.run_remove_empty_repository(
                repository_name=repository_name,
            )


class NexusAPIClient(BaseRegistryAPIClient):
    """
    Клиент взаимодействия с Registry в Nexus
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._registry_url = f'http://{self._registry_domain}'

        self._nexus_config = NexusConfig(
            username=self._username,
            password=self._password,
            url=self._registry_url,
            x509_verify=self._verify,
        )
        self._nexus_client = NexusClient(
            config=self._nexus_config,
        )

    def _get_docker_repository(self):
        """
        Получение docker репозитория
        """
        repositories = self._nexus_client.repositories.list

        docker_repository_params = list(filter(lambda r: r['format'] == 'docker' and 'docker-registry' in r['name'], repositories))[0]

        return self._nexus_client.repositories.get_by_name(docker_repository_params['name'])

    def get_repositories(self):
        """
        Метод получения списка репозиториев
        """
        docker_repository = self._get_docker_repository()

        artefacts = list(docker_repository.list('/'))

        return artefacts

    def delete_repository(self, *args, repository_name, **kwargs):
        """
        Удаление артефактов по указанному пути
        """
        docker_repository = self._get_docker_repository()

        docker_repository.delete(
            repository_path=repository_name,
        )

