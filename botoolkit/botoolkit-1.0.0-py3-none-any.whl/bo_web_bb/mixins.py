from botoolkit.bo_postgres.consts import (
    POSTGRES_DEFAULT_PORT,
)
from botoolkit.bo_web_bb.services import (
    BaseWebBBAppServiceManager,
    WebBBAppServiceManager,
)
from botoolkit.bo_web_bb.settings import (
    BASE_WEB_BB_APP_IMAGE_DIR_PATH,
    WEB_BB_APP_IMAGE_DIR_PATH,
)


class WebBBDockerContainerNameArgumentsMixin:
    """
    Добавляет параметры в команду
        --web_bb_docker_container_name
    """

    def patch_arguments_schema(self):
        super().patch_arguments_schema()

        self._arguments_schema.append(
            {
                'section': 'web_bb_docker',
                'option': 'container_name',
                'help': 'Имя контейнера с приложением web_bb_app.',
            }
        )


class WebBBDockerMixin(WebBBDockerContainerNameArgumentsMixin):
    """
    Добавляет параметры в команду
        --web_bb_docker_base_image_name
        --web_bb_docker_image_name
        --web_bb_docker_container_name
    """

    def patch_arguments_schema(self):
        super().patch_arguments_schema()

        self._arguments_schema.extend(
            (
                {
                    'section': 'web_bb_docker',
                    'option': 'base_image_name',
                    'help': 'Имя базового образа приложения web_bb_app.',
                },
                {
                    'section': 'web_bb_docker',
                    'option': 'image_name',
                    'help': 'Имя образа приложения web_bb_app.',
                },
            )
        )


class WebBBServiceCommandMixin:
    """
    Миксин для создания команд для работы с сервисом web_bb
    """

    def _prepare_base_web_bb_app_image(self):
        """
        Подготовка базового образа приложения
        """
        base_web_bb_app_image_name = (
            f'{self._parsed_args.registry_url}/{self._parsed_args.web_bb_docker_base_image_name}:{self._parsed_args.web_bb_app_branch}'  # noqa
            if self._parsed_args.registry_url
            else f'{self._parsed_args.web_bb_docker_base_image_name}:{self._parsed_args.web_bb_app_branch}'
        )

        self._remove_image(
            name=base_web_bb_app_image_name,
        )

        image_repository, image_tag = self._parsed_args.web_bb_docker_base_image_name, self._parsed_args.web_bb_app_branch  # noqa
        manager = BaseWebBBAppServiceManager(
            docker_client=self._docker_client,
            network=self._parsed_args.docker_network,
        )

        if self._parsed_args.rebuild_base_web_bb:
            manager.build(
                web_bb_app_branch=self._parsed_args.web_bb_app_branch,
                build_dir_path=BASE_WEB_BB_APP_IMAGE_DIR_PATH,
                toolkit_general_rsa_private_key=(
                    self._parsed_args.toolkit_general_rsa_private_key
                ),
                image_repository=image_repository,
                image_tag=image_tag,
                registry_url=self._parsed_args.registry_url,
                force_push=True,
            )
        else:
            manager.pull(
                image_repository=image_repository,
                image_tag=image_tag,
                registry_url=self._parsed_args.registry_url,
            )

    def _run_web_bb_app(
        self,
        command: str,
    ):
        """
        Запуск контейнера с приложением web_bb
        """
        web_bb_app_manager = WebBBAppServiceManager(
            docker_client=self._docker_client,
            network=self._parsed_args.docker_network,
        )

        image_repository, image_tag = (
            self._parsed_args.web_bb_docker_image_name.split(':')
        )

        base_web_bb_app_image_name = (
            f'{self._parsed_args.registry_url}/{self._parsed_args.web_bb_docker_base_image_name}:{self._parsed_args.web_bb_app_branch}' if  # noqa
            self._parsed_args.registry_url else
            f'{self._parsed_args.web_bb_docker_base_image_name}:{self._parsed_args.web_bb_app_branch}'
        )

        web_bb_app_image_name = (
            f'{self._parsed_args.registry_url}/{self._parsed_args.web_bb_docker_image_name}' if  # noqa
            self._parsed_args.registry_url else
            self._parsed_args.web_bb_docker_image_name
        )

        self._remove_image(
            name=web_bb_app_image_name,
        )

        web_bb_app_image = web_bb_app_manager.build(
            image_repository=image_repository,
            image_tag=image_tag,
            registry_url=self._parsed_args.registry_url,
            toolkit_general_rsa_private_key=(
                self._parsed_args.toolkit_general_rsa_private_key
            ),
            web_bb_app_branch=self._parsed_args.web_bb_app_branch,
            base_web_bb_app_image_name=base_web_bb_app_image_name,
            build_dir_path=WEB_BB_APP_IMAGE_DIR_PATH,
        )

        web_bb_app_manager.run(
            image=web_bb_app_image,
            command=command,
            container_name=f'{self._container_prefix}{self._parsed_args.web_bb_docker_container_name}',  # noqa
            shm_size=self._parsed_args.docker_shm_size,
            cpu_max_count=self._parsed_args.docker_cpu_max_count,
            activated_plugins=self._parsed_args.plugins_activated_plugins,
            db_host=f'{self._container_prefix}{self._parsed_args.postgres_container_name}',  # noqa
            db_port=POSTGRES_DEFAULT_PORT,
            db_name=self._parsed_args.postgres_db,
            db_user=self._parsed_args.postgres_user,
            db_password=self._parsed_args.postgres_password,
            web_bb_core_branch=self._parsed_args.web_bb_core_branch,
            web_bb_accounting_branch=self._parsed_args.web_bb_accounting_branch,
            web_bb_salary_branch=self._parsed_args.web_bb_salary_branch,
            web_bb_vehicle_branch=self._parsed_args.web_bb_vehicle_branch,
            web_bb_food_branch=self._parsed_args.web_bb_food_branch,
        )
