import asyncio
import uuid
from argparse import (
    Namespace,
)
from collections import (
    OrderedDict,
)
from datetime import (
    datetime,
)
from distutils.util import (
    strtobool,
)
from pathlib import (
    Path,
)
from typing import (
    Dict,
    List,
    Optional,
    OrderedDict as OrderedDictType,
    Union,
)

import docker
import yaml
from docker.errors import (
    ContainerError,
)
from docker.models.containers import (
    Container,
)
from jenkins import (
    Jenkins,
)

from botoolkit.bo_conf.api import (
    BOConfigGenerator,
)
from botoolkit.bo_conf.mixins import (
    ConfiguratorArgumentsMixin,
    WebBBActivatedPluginsConfigArgumentsMixin,
    WebBBAppRegionAbbreviationConfigArgumentsMixin,
)
from botoolkit.bo_conf.settings import (
    GENERATOR_TOOL_NAME as BOCONF_GENERATOR_TOOL_NAME,
    TOOL_NAME as BOCONF_TOOL_NAME,
)
from botoolkit.bo_databaser.settings import (
    TOOL_NAME as BODATABASER_TOOL_NAME,
)
from botoolkit.bo_git.enums import (
    BranchEnum,
)
from botoolkit.bo_git.mixins import (
    WebBBAppBranchArgumentMixin,
    WebBBBranchesArgumentsMixin,
)
from botoolkit.bo_git.settings import (
    TOOL_NAME as BOGIT_TOOL_NAME,
)
from botoolkit.bo_jenkins.enums import (
    StandStateEnum,
)
from botoolkit.bo_jenkins.mixins import (
    JenkinsArgumentsMixin,
    JenkinsStandURLArgumentMixin,
)
from botoolkit.bo_jenkins.parsers import (
    JenkinsJobParser,
)
from botoolkit.bo_jenkins.settings import (
    TOOL_NAME as BOJENKINS_TOOL_NAME,
)
from botoolkit.bo_postgres.command_validators import (
    LocalDBAccessValidator,
    LocalDBMaxConnectionsValidator,
    LocalDBMaxParallelWorkersPerGatherValidator,
)
from botoolkit.bo_postgres.consts import (
    TEMPLATE_1,
)
from botoolkit.bo_postgres.enums import (
    DBImageTypeEnum,
    DBStatusEnum,
)
from botoolkit.bo_postgres.exporters import (
    WebBBDBImageConfigurationExporter,
)
from botoolkit.bo_postgres.generators import (
    WebBBDBImageConfigurationGenerator,
)
from botoolkit.bo_postgres.helpers import (
    DBQueryExecutor,
    generate_db_image_name,
)
from botoolkit.bo_postgres.mixins import (
    PostgresArgumentsMixin,
    PostgresServiceCommandMixin,
)
from botoolkit.bo_postgres.repositories import (
    WebBBDBImageBuildRepository,
)
from botoolkit.bo_postgres.services import (
    PostgresServiceManager,
)
from botoolkit.bo_postgres.settings import (
    BASE_DB_IMAGE_SCHEMA_TEMPLATE_PATH,
    TOOL_NAME as BOPOSTGRES_TOOL_NAME,
)
from botoolkit.bo_postgres.strings import (
    BASE_DB_IMAGE_SCHEMA_NOT_FOUND_ERROR,
)
from botoolkit.bo_registry.helpers import (
    RegistryAuxiliaryTool,
)
from botoolkit.bo_registry.mixins import (
    RegistryArgumentsMixin,
    RegistryClientArgumentMixin,
    RegistryURLArgumentsMixin,
)
from botoolkit.bo_registry.settings import (
    TOOL_NAME as BOREGISTRY_TOOL_NAME,
)
from botoolkit.bo_toolkit.mixins import (
    BOToolkitPrivateKeyArgumentMixin,
    DockerArgumentsMixin,
)
from botoolkit.bo_toolkit.settings import (
    TOOL_NAME as BOTOOLKIT_TOOL_NAME,
)
from botoolkit.bo_web_bb.consts import (
    RUN_WEB_BB_APP_CONTAINER_COMMANDS,
)
from botoolkit.bo_web_bb.enums import (
    ProjectEnum,
)
from botoolkit.bo_web_bb.mixins import (
    WebBBDockerMixin,
    WebBBServiceCommandMixin,
)
from botoolkit.bo_web_bb.services import (
    WebBBAppServiceManager,
)
from botoolkit.bo_web_bb.settings import (
    TOOL_NAME as BOWEBBB_TOOL_NAME,
    WEB_BB_APP_IMAGE_DIR_PATH,
)
from botoolkit.core.commands import (
    BOConfiguredToolCommand,
    BOConfiguredToolConfigureCommand,
    BOConfiguredToolLister,
)
from botoolkit.core.consts import (
    ALLOWED_ALL_EMPTY_CONFIG_PARAMETERS,
)
from botoolkit.core.loggers import (
    logger,
)
from botoolkit.core.mixins import (
    ClearArgumentMixin,
    DockerServiceMixin,
    RemoveArtefactsOnAbortMixin,
)
from botoolkit.settings import (
    CONFIGURATION_DIRECTORY_PATH,
)


class ConfigureBOPostgresCommand(
    PostgresArgumentsMixin,
    BOConfiguredToolConfigureCommand,
):
    """
    Команда конфигурирования инструмента bopostgres
    """

    def __init__(
        self,
        *args,
        **kwargs,
    ):
        super().__init__(
            *args,
            **kwargs,
        )

        self.description = (
            'Configure bopostgres for working with Postgres docker containers.'
        )

    def get_tool_name(self):
        return BOPOSTGRES_TOOL_NAME

    def get_allowed_empty_config_parameters(self):
        return ALLOWED_ALL_EMPTY_CONFIG_PARAMETERS

    def get_required_config_tool_names(self):
        required_config_tool_names = super().get_required_config_tool_names()

        required_config_tool_names.extend(
            (
                BOTOOLKIT_TOOL_NAME,
            )
        )

        return required_config_tool_names


class GenerateBaseDBImageSchemaCommand(
    PostgresArgumentsMixin,
    JenkinsArgumentsMixin,
    ConfiguratorArgumentsMixin,
    ClearArgumentMixin,
    BOConfiguredToolCommand,
):
    """
    Команда генерации конфига для создания базовых образов баз данных
    """

    def __init__(
        self,
        *args,
        **kwargs,
    ):
        super().__init__(
            *args,
            **kwargs,
        )

        self.description = (
            'Generate base_db_image_schema.yaml.'
        )

    def get_required_config_tool_names(self):
        required_config_tool_names = super().get_required_config_tool_names()

        required_config_tool_names.extend(
            (
                BOPOSTGRES_TOOL_NAME,
                BOJENKINS_TOOL_NAME,
                BOCONF_TOOL_NAME,
                BOTOOLKIT_TOOL_NAME,
            )
        )

        return required_config_tool_names

    def get_parser(
        self,
        prog_name,
    ):
        parser = super().get_parser(
            prog_name=prog_name,
        )

        parser.add_argument(
            '--with_test_databases',
            dest='with_test_databases',
            action='store',
            default=False,
            type=lambda x: bool(strtobool(x)),
            help=(
                'Need generate test databases schemas'
            ),
        )

        parser.add_argument(
            '--exclude_projects',
            dest='exclude_projects',
            action='store',
            default=None,
            type=lambda x: tuple(map(lambda project: ProjectEnum(project), x.split(','))),
            help='Excluded projects',
        )

        parser.add_argument(
            '--exclude_branches',
            dest='exclude_branches',
            action='store',
            default=(),
            type=lambda x: tuple(map(lambda branch: BranchEnum(branch), x.split(','))),
            help='Excluded branches'
        )

        parser.add_argument(
            '--base_images_branch',
            dest='base_images_branch',
            action='store',
            default=BranchEnum.DEFAULT,
            type=lambda x: BranchEnum(x),
            help='Branch using in generating base db images',
        )

        return parser

    def take_action(
        self,
        parsed_args: Namespace,
    ):
        """
       Создание схемы базовых образов баз данных из шаблона
       """
        super().take_action(
            parsed_args=parsed_args,
        )

        repository = WebBBDBImageBuildRepository()

        projects = ProjectEnum.get_projects()

        if parsed_args.exclude_projects:
            projects = tuple(set(projects).difference(parsed_args.exclude_projects))

        generator = WebBBDBImageConfigurationGenerator(
            repository=repository,
            parsed_args=parsed_args,
            projects=projects,
        )
        exporter = WebBBDBImageConfigurationExporter(
            repository=repository,
        )

        generator.generate()

        exporter.to_yaml(
            clear=self._parsed_args.clear,
        )

        logger.write(
            'base_db_image_schema.yaml was successfully created.\n'
        )


class RunPostgresServiceCommand(
    DockerArgumentsMixin,
    PostgresArgumentsMixin,
    DockerServiceMixin,
    PostgresServiceCommandMixin,
    BOConfiguredToolCommand,
):
    """
    Запуск контейнера с Postgres
    """

    def __init__(
        self,
        *args,
        **kwargs,
    ):
        super().__init__(
            *args,
            **kwargs,
        )

        self.description = (
            'Run docker container with Postgres by sending parameters.'
        )

    def get_required_config_tool_names(self):
        required_config_tool_names = super().get_required_config_tool_names()

        required_config_tool_names.extend(
            (
                BOPOSTGRES_TOOL_NAME,
                BOTOOLKIT_TOOL_NAME,
            )
        )

        return required_config_tool_names

    def get_container_prefix(self):
        return 'bopostgres-'

    def take_action(
        self,
        parsed_args: Namespace,
    ):
        super().take_action(
            parsed_args=parsed_args,
        )
        self._remove_artefacts()

        self._run_postgres_container()


class RunWebBBPostgresServiceCommand(
    JenkinsStandURLArgumentMixin,
    DockerArgumentsMixin,
    PostgresArgumentsMixin,
    RegistryURLArgumentsMixin,
    WebBBDockerMixin,
    WebBBActivatedPluginsConfigArgumentsMixin,
    WebBBAppRegionAbbreviationConfigArgumentsMixin,
    BOToolkitPrivateKeyArgumentMixin,
    WebBBBranchesArgumentsMixin,
    WebBBServiceCommandMixin,
    PostgresServiceCommandMixin,
    DockerServiceMixin,
    RemoveArtefactsOnAbortMixin,
    BOConfiguredToolCommand,
):
    """
    Команда для запуска сборки среза БД Databaser-ом
    """

    def __init__(
        self,
        *args,
        **kwargs,
    ):
        super().__init__(
            *args,
            **kwargs,
        )

        self.description = (
            'Running Databaser.'
        )

    def get_required_config_tool_names(self):
        required_config_tool_names = super().get_required_config_tool_names()

        required_config_tool_names.extend(
            (
                BOCONF_TOOL_NAME,
                BOCONF_GENERATOR_TOOL_NAME,
                BODATABASER_TOOL_NAME,
                BOPOSTGRES_TOOL_NAME,
                BOREGISTRY_TOOL_NAME,
                BOWEBBB_TOOL_NAME,
                BOGIT_TOOL_NAME,
                BOJENKINS_TOOL_NAME,
                BOTOOLKIT_TOOL_NAME,
            )
        )

        return required_config_tool_names

    def get_container_prefix(self):
        return f'{BOPOSTGRES_TOOL_NAME}-'

    def get_parser(
        self,
        prog_name,
    ):
        parser = super().get_parser(
            prog_name=prog_name,
        )

        parser.add_argument(
            '--rebuild_base_web_bb',
            dest='rebuild_base_web_bb',
            action='store',
            default=False,
            type=lambda x: bool(strtobool(x)),
            help=(
                'Need to rebuild the base web_bb image. Default: False.'
            ),
        )

        return parser

    def _fill_parameters_from_stand_configuration(self):
        """
        Заполнение параметров из конфигурационного файла тестового стенда,
        если указан stand_url
        """
        if self._parsed_args.stand_url:
            configurations_path = Path(
                self._boconf_config.get(
                    section='boconf',
                    option='configurations_path',
                ).value
            )
            configurations_git_repository_url: str = self._boconf_config.get(
                section='boconf',
                option='configurations_git_repository_url',
            ).value

            bo_config_generator = BOConfigGenerator(
                stand_url=self._parsed_args.stand_url,
                projects_combination=self._projects_combination,
                configurations_path=configurations_path,
                configurations_git_repository_url=(
                    configurations_git_repository_url
                ),
                settings_config=self._boconf_generator_config,
            )

            web_bb_config = bo_config_generator.generate()

            self._parsed_args.plugins_activated_plugins = (
                web_bb_config['plugins']['activated_plugins'].value
            )

            self._parsed_args.runtime_app_region_abbreviation = (
                web_bb_config['runtime']['app_region_abbreviation'].value
            )

    def _fill_postgres_image_by_activated_projects(self):
        """
        Заполнение значения образа базы данных согласно подключенных проектов
        """
        image_name = generate_db_image_name(
            projects_combination=self._projects_combination,
            type_=DBImageTypeEnum.BASE,
            region=self._parsed_args.runtime_app_region_abbreviation,
        )

        if image_name and self._parsed_args.registry_url:
            db_image_name = f'{self._parsed_args.registry_url}/{image_name}'

            self._parsed_args.postgres_image = db_image_name

    def _remove_artefacts(
        self,
        is_success: bool = False,
    ):
        """
        Удаление контейнеров с базой и приложением
        """
        self._remove_container(
            container_id=self._parsed_args.web_bb_docker_container_name,
        )

        if not is_success:
            self._remove_container(
                container_id=self._parsed_args.postgres_container_name,
            )

    def take_action(
        self,
        parsed_args: Namespace,
    ):
        super().take_action(
            parsed_args=parsed_args,
        )

        self._fill_parameters_from_stand_configuration()

        self._fill_postgres_image_by_activated_projects()

        self._register_signals()

        self._prepare_base_web_bb_app_image()

        self._remove_artefacts()

        self._run_postgres_container()

        command = f'bash -c \'{" && ".join(RUN_WEB_BB_APP_CONTAINER_COMMANDS)}\''
        self._run_web_bb_app(
            command=command,
        )

        self._remove_artefacts(
            is_success=True,
        )

        logger.write(
            'container with Postgres was created.\n'
        )


class CreateBaseDBImageCommand(
    RegistryClientArgumentMixin,
    DockerArgumentsMixin,
    PostgresArgumentsMixin,
    WebBBDockerMixin,
    WebBBAppBranchArgumentMixin,
    BOToolkitPrivateKeyArgumentMixin,
    WebBBServiceCommandMixin,
    PostgresServiceCommandMixin,
    DockerServiceMixin,
    RegistryArgumentsMixin,
    RemoveArtefactsOnAbortMixin,
    BOConfiguredToolCommand,
):
    """
    Команда для создания базовых образов баз данных согласно параметров из
    base_db_image_schema.yaml
    """

    def __init__(
        self,
        *args,
        **kwargs,
    ):
        super().__init__(
            *args,
            **kwargs,
        )

        self.description = (
            'Building base databases images by parameters from '
            'base_db_image_schema.yaml.'
        )

        self._base_db_image_schema: Optional[List[Dict[str, str]]] = None
        self._built_db_image_names = []
        self._build_containers = []
        self._build_images = []
        self._base_web_bb_images = set()

    def get_required_config_tool_names(self):
        required_config_tool_names = super().get_required_config_tool_names()

        required_config_tool_names.extend(
            (
                BOPOSTGRES_TOOL_NAME,
                BOREGISTRY_TOOL_NAME,
                BOWEBBB_TOOL_NAME,
                BOGIT_TOOL_NAME,
                BOTOOLKIT_TOOL_NAME,
            )
        )

        return required_config_tool_names

    def get_container_prefix(self):
        return f'{BOPOSTGRES_TOOL_NAME}-'

    def _parse_base_db_image_schema(self):
        """
        Парсинг YAML-файла со схемой создания базовых образов баз данных
        """
        local_base_db_image_schema_path = (
            CONFIGURATION_DIRECTORY_PATH / BASE_DB_IMAGE_SCHEMA_TEMPLATE_PATH.name
        )

        if not local_base_db_image_schema_path.exists():
            raise RuntimeError(BASE_DB_IMAGE_SCHEMA_NOT_FOUND_ERROR)

        with open(str(local_base_db_image_schema_path), 'r') as f:
            self._base_db_image_schema = yaml.load(
                stream=f.read(),
                Loader=yaml.FullLoader,
            )

    def _remove_build_container(
        self,
        container_name: str,
    ):
        """
        Удаление контейнера сборки
        """
        self._remove_container(
            container_id=container_name,
            with_prefix=False,
        )

        try:
            self._build_containers.remove(container_name)
        except ValueError:
            pass

    def _remove_current_build_artefacts(
        self,
        postgres_container_name,
        web_bb_docker_container_name,
        web_bb_docker_image_name,
    ):
        """
        Удаление артефактов каждого запуска сборки базового образа БД
        """
        self._remove_build_container(
            container_name=postgres_container_name,
        )

        self._remove_build_container(
            container_name=web_bb_docker_container_name,
        )

        web_bb_app_image_name = (
            f'{self._parsed_args.registry_url}/{web_bb_docker_image_name}'
            if self._parsed_args.registry_url
            else web_bb_docker_image_name
        )

        self._remove_image(
            name=web_bb_app_image_name,
        )
        try:
            self._build_images.remove(web_bb_docker_image_name)
        except ValueError:
            pass

    def _remove_build_artefacts(self):
        """
        Удаление артефактов всех сборок
        """
        for container_name in self._build_containers:
            self._remove_container(
                container_id=container_name,
                with_prefix=False,
            )

        for image_repository in self._build_images:
            image_name = (
                f'{self._parsed_args.registry_url}/{image_repository}'
                if self._parsed_args.registry_url
                else image_repository
            )

            self._remove_image(
                name=image_name,
            )

    def _remove_artefacts(self):
        """
        Удаление контейнеров с базой и приложением
        """
        self._remove_build_artefacts()

        for base_web_bb_app_image_name in self._base_web_bb_images:
            self._remove_image(
                name=base_web_bb_app_image_name,
            )

        self._clear_built_db_images()

    def _enable_pg_trgm(
        self,
        db_name,
        db_user,
        db_password,
        postgres_container,
    ):
        """
        Подключение плагина pg_trgm
        """
        logger.write('enable pg_trgm..\n')

        command = f'psql -d {db_name} -U {db_user} -W {db_password} -c "CREATE EXTENSION IF NOT EXISTS pg_trgm;"'

        postgres_container.exec_run(
            cmd=command,
        )

        command = f'psql -d {TEMPLATE_1} -U {db_user} -W {db_password} -c "CREATE EXTENSION IF NOT EXISTS pg_trgm;"'

        postgres_container.exec_run(
            cmd=command,
        )

    def _install_wal2json(
        self,
        postgres_container: Container,
    ):
        """
        Установка wal2json в контейнер с Postgres для работы replisync
        """
        logger.write('install wal2json..\n')

        postgres_major_version = self._parsed_args.postgres_image.split(':')[1].split('.')[0]

        command = (
            f'apt-get update && apt-get install -f -y --no-install-recommends '
            f'postgresql-{postgres_major_version}-wal2json postgresql-{postgres_major_version}-wal2json-dbgsym'
        )

        postgres_container.exec_run(
            cmd=f'bash -lc "{command}"',
        )

    def _run_postgres_container(
        self,
        build_params,
        postgres_manager,
        postgres_container_name,
        *args,
        **kwargs,
    ):
        image_repository, image_tag = (
            build_params['base_image_name'].split(':')
        )

        if 'postgres' in build_params['base_image_name']:
            image = postgres_manager.pull(
                image_repository=image_repository,
                image_tag=image_tag,
            )
        else:
            image = postgres_manager.get_image(
                image_repository=image_repository,
                image_tag=image_tag,
                registry_url=self._parsed_args.registry_url,
            )

        logger.write(
            f'running Postgres container with name '
            f'"{postgres_container_name}"..\n'
        )

        postgres_container = postgres_manager.run(
            image=image,
            container_name=postgres_container_name,
            pg_data=self._parsed_args.postgres_pgdata,
            db=self._parsed_args.postgres_db,
            user=self._parsed_args.postgres_user,
            password=self._parsed_args.postgres_password,
            shm_size=self._parsed_args.docker_shm_size,
            cpu_max_count=self._parsed_args.docker_cpu_max_count,
            max_connections=self._parsed_args.postgres_max_connections,
            shared_buffers=self._parsed_args.postgres_shared_buffers,
            temp_buffers=self._parsed_args.postgres_temp_buffers,
            work_mem=self._parsed_args.postgres_work_mem,
            maintenance_work_mem=(
                self._parsed_args.postgres_maintenance_work_mem
            ),
            track_activities=self._parsed_args.postgres_track_activities,
            track_counts=self._parsed_args.postgres_track_counts,
            autovacuum=self._parsed_args.postgres_autovacuum,
            wal_level=self._parsed_args.postgres_wal_level,
            archive_mode=self._parsed_args.postgres_archive_mode,
            max_wal_senders=self._parsed_args.postgres_max_wal_senders,
            max_replication_slots=self._parsed_args.postgres_max_replication_slots,
            checkpoint_completion_target=(
                self._parsed_args.postgres_checkpoint_completion_target
            ),
            random_page_cost=self._parsed_args.postgres_random_page_cost,
            default_text_search_config=(
                self._parsed_args.postgres_default_text_search_config
            ),
        )

        return postgres_container

    def _build_web_bb_app_image(
        self,
        build_params,
        web_bb_app_manager,
        web_bb_app_image_name,
        base_web_bb_app_image_name,
        image_repository,
        image_tag,
    ):
        self._remove_image(
            name=web_bb_app_image_name,
        )

        web_bb_app_image = web_bb_app_manager.build(
            image_repository=image_repository,
            image_tag=image_tag,
            registry_url=self._parsed_args.registry_url,
            toolkit_general_rsa_private_key=self._parsed_args.toolkit_general_rsa_private_key,
            web_bb_app_branch=build_params['web_bb_app_branch'],
            base_web_bb_app_image_name=base_web_bb_app_image_name,
            build_dir_path=WEB_BB_APP_IMAGE_DIR_PATH,
        )

        return web_bb_app_image

    def _run_web_bb_app_container(
        self,
        build_params,
        web_bb_app_manager,
        web_bb_app_image,
        web_bb_app_container_name,
        postgres_container_name,
    ):
        """
        Запуск контейнера с приложением
        """
        web_bb_app_manager.run(
            image=web_bb_app_image,
            container_name=web_bb_app_container_name,
            command=build_params['command'],
            shm_size=self._parsed_args.docker_shm_size,
            cpu_max_count=self._parsed_args.docker_cpu_max_count,
            activated_plugins=build_params['activated_plugins'],
            db_host=postgres_container_name,
            db_port=self._parsed_args.postgres_port,
            db_name=self._parsed_args.postgres_db,
            db_user=self._parsed_args.postgres_user,
            db_password=self._parsed_args.postgres_password,
            web_bb_core_branch=build_params['web_bb_core_branch'],
            web_bb_accounting_branch=build_params['web_bb_accounting_branch'],
            web_bb_salary_branch=build_params['web_bb_salary_branch'],
            web_bb_vehicle_branch=build_params['web_bb_vehicle_branch'],
            web_bb_food_branch=build_params['web_bb_food_branch'],
        )

    def _create_base_db_image(
        self,
        build_params: Dict[str, str],
    ):
        """
        Создание базового образа базы данных согласно переданных параметров
        """
        # В качестве дополнительного префикса используется часть hex-а от UUID, т.к. регионы могут именовать с нижним
        # подчеркиванием, что вызывает ошибку при обращении к контейнеру, как к сервису
        uuid_hex = uuid.uuid4().hex[:5]

        postgres_container_name = (
            f'{uuid_hex}-{self._container_prefix}{self._parsed_args.postgres_container_name}'
        )
        web_bb_app_container_name = (
            f'{uuid_hex}-{self._container_prefix}{self._parsed_args.web_bb_docker_container_name}'
        )

        web_bb_image_repository, image_tag = (
            self._parsed_args.web_bb_docker_image_name.split(':')
        )

        web_bb_image_repository = f'{uuid_hex}-{web_bb_image_repository}'

        self._build_images.append(f'{web_bb_image_repository}:{image_tag}')

        self._remove_current_build_artefacts(
            postgres_container_name=postgres_container_name,
            web_bb_docker_container_name=web_bb_app_container_name,
            web_bb_docker_image_name=f'{web_bb_image_repository}:{image_tag}',
        )

        self._build_containers.extend((
            postgres_container_name,
            web_bb_app_container_name,
        ))

        result_db_image_repository = (
            f'{self._parsed_args.registry_url}/{build_params["image_repository"]}'
            if self._parsed_args.registry_url
            else build_params['image_repository']
        )

        logger.write(
            f'start building base db image with name '
            f'{result_db_image_repository}:{build_params["image_tag"]}..\n'
        )

        postgres_manager = PostgresServiceManager(
            docker_client=self._docker_client,
            network=self._parsed_args.docker_network,
        )

        postgres_container = self._run_postgres_container(
            build_params=build_params,
            postgres_manager=postgres_manager,
            postgres_container_name=postgres_container_name,
        )

        web_bb_app_manager = WebBBAppServiceManager(
            docker_client=self._docker_client,
            network=self._parsed_args.docker_network,
        )

        base_web_bb_app_image_name = (
            f'{self._parsed_args.registry_url}/{self._parsed_args.web_bb_docker_base_image_name}:{build_params["web_bb_app_branch"]}'
            if self._parsed_args.registry_url
            else f'{self._parsed_args.web_bb_docker_base_image_name}:{build_params["web_bb_app_branch"]}'
        )

        self._base_web_bb_images.add(base_web_bb_app_image_name)

        web_bb_app_image_name = (
            f'{self._parsed_args.registry_url}/{web_bb_image_repository}:{image_tag}'
            if self._parsed_args.registry_url
            else f'{web_bb_image_repository}:{image_tag}'
        )

        web_bb_app_image = self._build_web_bb_app_image(
            build_params,
            web_bb_app_manager,
            web_bb_app_image_name,
            base_web_bb_app_image_name,
            web_bb_image_repository,
            image_tag,
        )

        self._enable_pg_trgm(
            db_name=self._parsed_args.postgres_db,
            db_user=self._parsed_args.postgres_user,
            db_password=self._parsed_args.postgres_password,
            postgres_container=postgres_container,
        )

        self._install_wal2json(
            postgres_container=postgres_container,
        )

        build_params['activated_plugins'] = (
            build_params['activated_plugins'].replace(' ', '').strip()
        )

        self._run_web_bb_app_container(
            build_params,
            web_bb_app_manager,
            web_bb_app_image,
            web_bb_app_container_name,
            postgres_container_name,
        )

        logger.write(
            f'stopping Postgres container with id "{postgres_container_name}"'
            f'..\n'
        )
        postgres_container.stop(
            timeout=180,
        )

        stopping_result = postgres_container.wait(
            timeout=180,
        )

        logger.write(
            f'stopping Postgres container with id "{postgres_container_name}"'
            f' was finished with result "{stopping_result}"\n'
        )

        logger.write(
            f'committing Postgres container with image name '
            f'"{result_db_image_repository}:{build_params["image_tag"]}"..\n'
        )

        postgres_container.commit(
            repository=result_db_image_repository,
            tag=build_params['image_tag'],
        )

        self._remove_registry_repository(
            repository_name=build_params['image_repository'],
            tag=build_params['image_tag'],
        )

        db_image_name = postgres_manager.push(
            image_repository=build_params['image_repository'],
            image_tag=build_params['image_tag'],
            registry_url=self._parsed_args.registry_url,
        )

        self._built_db_image_names.append(db_image_name)

        logger.write(
            f'building base db image with name '
            f'{result_db_image_repository}:{build_params["image_tag"]} finished.\n'
        )

        self._remove_current_build_artefacts(
            postgres_container_name=postgres_container_name,
            web_bb_docker_container_name=web_bb_app_container_name,
            web_bb_docker_image_name=f'{web_bb_image_repository}:{image_tag}',
        )

    def _clear_built_db_images(self):
        """
        Удаление собранных базовых образов БД
        """
        for image_name in filter(None, self._built_db_image_names):
            logger.write(f'removing image "{image_name}"..\n')

            self._docker_client.images.remove(
                image=image_name,
                force=True,
            )

    def _prepare_registry_tools(self):
        """
        Подготовка инструментария для работы с Registry
        """
        self._registry_auxiliary_tool = RegistryAuxiliaryTool(
            registry_host_ip=self._parsed_args.registry_host_ip,
            registry_host_username=self._parsed_args.registry_host_username,
            registry_container_name=self._parsed_args.registry_container_name,
        )

        self._registry_api_client = self._parsed_args.registry_client(
            registry_domain=self._parsed_args.registry_url,
            username=self._parsed_args.registry_user,
            password=self._parsed_args.registry_password,
            verify=False,
            registry_auxiliary_tool=self._registry_auxiliary_tool,
        )

        self._repositories = self._registry_api_client.get_repositories()

    def _remove_registry_repository(
        self,
        repository_name: str,
        tag: str,
    ):
        """
        Удаление репозитория из Registry
        """
        repository_name_matches = list(rn for rn in self._repositories if f'{repository_name}/manifests/{tag}' in rn)

        for repository_name_match in repository_name_matches:
            self._registry_api_client.delete_repository(
                repository_name=repository_name_match,
            )

    def _build_base_db_image(
        self,
        build_params,
    ):
        try:
            self._create_base_db_image(
                build_params=build_params,
            )
        except ContainerError:
            self._remove_artefacts()

            raise

    async def _async_build_base_db_images(
        self,
        grouped_schemas,
    ):
        """
        Запуск сборки базовых образов сгруппированных по базовому образу
        """
        for schemas_group in grouped_schemas.values():
            coroutines = [
                asyncio.to_thread(
                    self._create_base_db_image, build_params
                )
                for build_params in schemas_group
            ]

            if coroutines:
                await asyncio.gather(*coroutines)

    def _build_base_db_images(
        self,
        grouped_schemas: OrderedDictType[str, List[Dict[str, Union[str, None]]]],
    ):
        """
        Запуск асинхронной сборки базовых образов
        """
        asyncio.run(
            self._async_build_base_db_images(grouped_schemas),
            debug=True,
        )

    def take_action(
        self,
        parsed_args: Namespace,
    ):
        super().take_action(
            parsed_args=parsed_args,
        )

        start = datetime.now()
        logger.write(f'start building base db images - {start}\n')

        self._parse_base_db_image_schema()

        self._docker_client = docker.from_env()

        self._prepare_registry_tools()

        grouped_schemas: OrderedDictType[str, List[Dict[str, Union[str, None]]]] = OrderedDict()
        for build_params in self._base_db_image_schema:
            if build_params['base_image_name'] not in grouped_schemas:
                grouped_schemas[build_params['base_image_name']] = []

            grouped_schemas[build_params['base_image_name']].append(build_params)

        self._build_base_db_images(
            grouped_schemas=grouped_schemas,
        )

        self._remove_artefacts()

        finish = datetime.now()
        logger.write(
            f'finished building base db images. \nDates \nstart - {start}, \nfinish - {finish}, \nspend time - '
            f'{finish - start}\n'
        )


class CheckDBAccessCommand(
    BOConfiguredToolLister,
):
    """
    Команда для проверки доступности подключения к базам данных активных
    тестовых стендов
    """

    def __init__(
        self,
        *args,
        **kwargs,
    ):
        super().__init__(
            *args,
            **kwargs,
        )

        self.description = (
            'Checking access for testing stands DBs from local machine.'
        )

    def get_required_config_tool_names(self):
        required_config_tool_names = super().get_required_config_tool_names()

        required_config_tool_names.extend(
            (
                BOPOSTGRES_TOOL_NAME,
                BOJENKINS_TOOL_NAME,
                BOCONF_TOOL_NAME,
                BOTOOLKIT_TOOL_NAME,
            )
        )

        return required_config_tool_names

    def take_action(
        self,
        parsed_args: Namespace,
    ):
        super().take_action(
            parsed_args=parsed_args,
        )

        configurations_path = Path(
            self._boconf_config.get(
                section='boconf',
                option='configurations_path',
            ).value
        )
        configurations_git_repository_url: str = self._boconf_config.get(
            section='boconf',
            option='configurations_git_repository_url',
        ).value

        jenkins_server = Jenkins(
            url=self._bojenkins_config['jenkins']['url'].value,
            username=self._bojenkins_config['jenkins']['username'].value,
            password=self._bojenkins_config['jenkins']['password'].value,
        )

        jenkins_job_parser = JenkinsJobParser(
            jenkins_server=jenkins_server,
        )

        jenkins_job_parser.parse()

        columns = (
            'Stand url',
            'Configuration file UUID',
            'DB host ip',
            'DB name',
            'Status',
            'max_connections',
            'max_parallel_workers_per_gather',
        )

        rows = []

        jobs_data = jenkins_job_parser.get_jobs_data_as_tuple(
            state=StandStateEnum.AVAILABLE,
        )

        for _, _, url, configuration_file_uuid, _ in jobs_data:
            bo_config_generator = BOConfigGenerator(
                stand_url=url,
                projects_combination=ProjectEnum.get_projects(),
                configurations_path=configurations_path,
                configurations_git_repository_url=(
                    configurations_git_repository_url
                ),
            )

            stand_config = bo_config_generator.generate()

            database_host = stand_config.get(
                section='database',
                option='database_host',
            ).value
            database_name = stand_config.get(
                section='database',
                option='database_name',
            ).value

            db_executor = DBQueryExecutor(
                database=database_name,
                user=stand_config.get(
                    section='database',
                    option='database_user',
                ).value,
                password=stand_config.get(
                    section='database',
                    option='database_password',
                ).value,
                host=database_host,
                port=stand_config.get(
                    section='database',
                    option='database_port',
                ).value,
            )

            have_access = False
            max_connections = None
            max_parallel_workers_per_gather = None
            is_open = db_executor.open()

            if is_open:
                db_access_validator = LocalDBAccessValidator(
                    db_executor=db_executor,
                )
                have_access = db_access_validator.validate()

                max_connections_validator = LocalDBMaxConnectionsValidator(
                    db_executor=db_executor,
                )
                max_connections = max_connections_validator.validate()

                max_parallel_workers_per_gather_validator = (
                    LocalDBMaxParallelWorkersPerGatherValidator(
                        db_executor=db_executor,
                    )
                )
                max_parallel_workers_per_gather = (
                    max_parallel_workers_per_gather_validator.validate()
                )

            rows.append(
                (
                    url,
                    configuration_file_uuid,
                    database_host,
                    database_name,
                    (
                        DBStatusEnum.REACHABLE.value if
                        have_access else
                        DBStatusEnum.UNREACHABLE.value
                    ),
                    max_connections,
                    max_parallel_workers_per_gather,
                )
            )

            db_executor.close()

        return columns, rows
