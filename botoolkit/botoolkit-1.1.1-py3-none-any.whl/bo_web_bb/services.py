from pathlib import (
    Path,
)
from typing import (
    List,
    Optional,
    Union,
)

from docker.models.images import (
    Image,
)

from botoolkit.core.helpers import (
    print_build_image_exception_log,
)
from botoolkit.core.loggers import (
    logger,
)
from botoolkit.core.services import (
    DockerServiceManager,
)


class BaseWebBBAppServiceManager(DockerServiceManager):
    """
    Менеджер для управления сервисом базового приложения web_bb
    """

    def build(
        self,
        image_repository: str,
        image_tag: str,
        toolkit_general_rsa_private_key: str,
        web_bb_app_branch: str,
        build_dir_path: Path,
        registry_url: Optional[str] = None,
        force_push: bool = False,
    ):
        """
        Сборка базового образа приложения web_bb
        """
        image_name = (
            f'{registry_url}/{image_repository}:{image_tag}' if
            registry_url else
            f'{image_repository}:{image_tag}'
        )

        build_args = {
            'TOOLKIT_GENERAL_RSA_PRIVATE_KEY': (
                toolkit_general_rsa_private_key
            ),
            'WEB_BB_APP_BRANCH': web_bb_app_branch,
        }

        logger.write(
            f'building image {image_name}..\n'
        )

        with print_build_image_exception_log():
            self._docker_client.images.build(
                path=str(build_dir_path),
                tag=image_name,
                quiet=True,
                nocache=True,
                pull=True,
                buildargs=build_args,
                rm=True,
                forcerm=True,
            )

        logger.write(
            f'image {image_name} was built.\n'
        )

        if force_push and registry_url:
            logger.write(
                f'pushing image {image_name}..\n'
            )

            self.push(
                image_repository=image_repository,
                image_tag=image_tag,
                registry_url=registry_url,
            )


class WebBBAppServiceManager(DockerServiceManager):
    """
    Менеджер для управления сервисом приложения web_bb
    """

    def build(
        self,
        image_repository: str,
        image_tag: str,
        registry_url: str,
        toolkit_general_rsa_private_key: str,
        web_bb_app_branch: str,
        base_web_bb_app_image_name: str,
        build_dir_path: Path,
        force_push: bool = False,
    ) -> Image:
        """
        Сборка базового образа приложения web_bb
        """
        image_name = (
            f'{registry_url}/{image_repository}:{image_tag}' if
            registry_url else
            f'{image_repository}:{image_tag}'
        )

        base_image_repository, base_image_tag = base_web_bb_app_image_name.split(':')
        self._docker_client.images.pull(
            repository=base_image_repository,
            tag=base_image_tag,
        )

        build_args = {
            'BASE_WEB_BB_APP_IMAGE_NAME': base_web_bb_app_image_name,
            'TOOLKIT_GENERAL_RSA_PRIVATE_KEY': (
                toolkit_general_rsa_private_key
            ),
            'WEB_BB_APP_BRANCH': web_bb_app_branch,
        }

        logger.write(
            f'building image {image_name}..\n'
        )

        with print_build_image_exception_log():
            image, log = self._docker_client.images.build(
                path=str(build_dir_path),
                tag=image_name,
                quiet=True,
                nocache=True,
                pull=True,
                buildargs=build_args,
                rm=True,
                forcerm=True,
            )

        logger.write(
            f'image with name "{image_name}" was built.\n'
        )

        if force_push and registry_url:
            self.push(
                image_repository=image_repository,
                image_tag=image_tag,
                registry_url=registry_url,
            )

        return image

    def run(
        self,
        image: Image,
        container_name: str,
        command: Union[str, List[str]],
        shm_size: str,
        cpu_max_count: int,
        activated_plugins: str,
        db_host: str,
        db_port: str,
        db_name: str,
        db_user: str,
        db_password: str,
        web_bb_core_branch: str,
        web_bb_accounting_branch: Optional[str] = None,
        web_bb_salary_branch: Optional[str] = None,
        web_bb_vehicle_branch: Optional[str] = None,
        web_bb_food_branch: Optional[str] = None,
    ):
        """
        Запуск контейнера с приложением web_bb
        """
        logger.write(f'running container {container_name}..\n')

        environment = {
            'WEB_BB_ACTIVATED_PLUGINS': activated_plugins,
            'DB_HOST': db_host,
            'DB_PORT': db_port,
            'DB_NAME': db_name,
            'DB_USER': db_user,
            'DB_PASSWORD': db_password,
            'WEB_BB_CORE_BRANCH': web_bb_core_branch,
            'WEB_BB_ACCOUNTING_BRANCH': web_bb_accounting_branch or '',
            'WEB_BB_SALARY_BRANCH': web_bb_salary_branch or '',
            'WEB_BB_VEHICLE_BRANCH': web_bb_vehicle_branch or '',
            'WEB_BB_FOOD_BRANCH': web_bb_food_branch or '',
        }

        log_generator = self._docker_client.containers.run(
            image=image,
            command=command,
            cpuset_cpus=f'0,{cpu_max_count}',
            detach=False,
            name=container_name,
            network=self._network,
            shm_size=shm_size,
            environment=environment,
            stream=True,
        )

        for line in log_generator:
            line = line.decode('utf-8')

            if '\n' in line:
                lines = line.split('\n')
            else:
                lines = (line,)

            for l in filter(lambda x: x, lines):
                if l:
                    logger.write(f'{l}\n')

        container = self._docker_client.containers.get(
            container_id=container_name,
        )

        return container
