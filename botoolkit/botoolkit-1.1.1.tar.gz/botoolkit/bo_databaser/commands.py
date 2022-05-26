from argparse import (
    Namespace,
)
from distutils.util import (
    strtobool,
)
from pathlib import (
    Path,
)

from botoolkit.bo_conf.api import (
    BOConfigGenerator,
)
from botoolkit.bo_conf.mixins import (
    WebBBActivatedPluginsConfigArgumentsMixin,
)
from botoolkit.bo_conf.settings import (
    GENERATOR_TOOL_NAME as BOCONF_GENERATOR_TOOL_NAME,
    TOOL_NAME as BOCONF_TOOL_NAME,
)
from botoolkit.bo_databaser.mixins import (
    DatabaserArgumentsMixin,
    DatabaserBuildArgumentsMixin,
    DatabaserBuildContainerNameArgumentsMixin,
    DatabaserGeneralArgumentsMixin,
    DatabaserWithDstDBArgumentsMixin,
)
from botoolkit.bo_databaser.services import (
    DatabaserServiceManager,
)
from botoolkit.bo_databaser.settings import (
    BUILD_TOOL_NAME as BODATABASER_BUILD_TOOL_NAME,
    TOOL_NAME as BODATABASER_TOOL_NAME,
)
from botoolkit.bo_git.mixins import (
    WebBBBranchesArgumentsMixin,
    WebBBProjectsArgumentsMixin,
)
from botoolkit.bo_git.settings import (
    TOOL_NAME as BOGIT_TOOL_NAME,
)
from botoolkit.bo_jenkins.mixins import (
    JenkinsStandURLArgumentMixin,
)
from botoolkit.bo_jenkins.settings import (
    TOOL_NAME as BOJENKINS_TOOL_NAME,
)
from botoolkit.bo_postgres.consts import (
    POSTGRES_DEFAULT_PORT,
)
from botoolkit.bo_postgres.enums import (
    DBImageTypeEnum,
)
from botoolkit.bo_postgres.helpers import (
    generate_db_image_name,
)
from botoolkit.bo_postgres.mixins import (
    PostgresArgumentsMixin,
    PostgresContainerNameArgumentsMixin,
    PostgresServiceCommandMixin,
)
from botoolkit.bo_postgres.settings import (
    TOOL_NAME as BOPOSTGRES_TOOL_NAME,
)
from botoolkit.bo_registry.mixins import (
    RegistryURLArgumentsMixin,
)
from botoolkit.bo_registry.settings import (
    TOOL_NAME as BOREGISTRY_TOOL_NAME,
)
from botoolkit.bo_toolkit.mixins import (
    BOToolkitGeneralArgumentsMixin,
    BOToolkitPrivateKeyArgumentMixin,
    DockerArgumentsMixin,
)
from botoolkit.bo_toolkit.settings import (
    TOOL_NAME as BOTOOLKIT_TOOL_NAME,
)
from botoolkit.bo_web_bb.consts import (
    DATABASER_RUN_WEB_BB_APP_CONTAINER_COMMANDS,
)
from botoolkit.bo_web_bb.mixins import (
    WebBBDockerContainerNameArgumentsMixin,
    WebBBDockerMixin,
    WebBBServiceCommandMixin,
)
from botoolkit.bo_web_bb.settings import (
    TOOL_NAME as BOWEBBB_TOOL_NAME,
)
from botoolkit.core.commands import (
    BOConfiguredToolCommand,
    BOConfiguredToolConfigureCommand,
)
from botoolkit.core.consts import (
    ALLOWED_ALL_EMPTY_CONFIG_PARAMETERS,
)
from botoolkit.core.enums import (
    ConfigurationFormatEnum,
)
from botoolkit.core.exporters import (
    ConfExporter,
    EnvExporter,
)
from botoolkit.core.loggers import (
    logger,
)
from botoolkit.core.mixins import (
    DockerServiceMixin,
    RemoveArtefactsOnAbortMixin,
)
from botoolkit.core.strings import (
    WRONG_CONFIGURATION_FILE_FORMAT_ERROR,
)
from botoolkit.settings import (
    CONFIGURATION_DIRECTORY_PATH,
)


class ConfigureBODatabaserCommand(
    DatabaserArgumentsMixin,
    DatabaserGeneralArgumentsMixin,
    DatabaserBuildArgumentsMixin,
    BOConfiguredToolConfigureCommand,
):
    """
    Конфигурирование инструмента bodatabaser
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

        self.description = 'Configure bodatabaser.'

    def get_tool_name(self):
        return BODATABASER_TOOL_NAME

    def get_allowed_empty_config_parameters(self):
        return ALLOWED_ALL_EMPTY_CONFIG_PARAMETERS

    def get_required_config_tool_names(self):
        required_config_tool_names = super().get_required_config_tool_names()

        required_config_tool_names.append(BOTOOLKIT_TOOL_NAME)

        return required_config_tool_names


class ConfigureBuildDatabaserCommand(
    JenkinsStandURLArgumentMixin,
    BOToolkitGeneralArgumentsMixin,
    DatabaserWithDstDBArgumentsMixin,
    DatabaserBuildArgumentsMixin,
    DockerArgumentsMixin,
    WebBBBranchesArgumentsMixin,
    PostgresArgumentsMixin,
    RegistryURLArgumentsMixin,
    WebBBProjectsArgumentsMixin,
    BOConfiguredToolConfigureCommand,
):
    """
    Создание конфигурационного файла для сборки среза БД Databaser-ом
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

        self._is_force_configure = False

        self.description = 'Create a configuration file for build.'

    def get_tool_name(self):
        return BODATABASER_BUILD_TOOL_NAME

    def get_allowed_empty_config_parameters(self):
        allowed_empty_config_parameters = (
            super().get_allowed_empty_config_parameters()
        )

        allowed_empty_config_parameters.update(
            {
                'databaser': [
                    'tables_truncate_included',
                    'tables_truncate_excluded',
                    'dst_db_host',
                    'dst_db_port',
                    'dst_db_name',
                    'dst_db_user',
                    'dst_db_password',
                ],
                'web_bb': [
                    'accounting_branch',
                    'salary_branch',
                    'vehicle_branch',
                    'food_branch',
                ],
                'registry': [
                    'url',
                ]
            }
        )

        return allowed_empty_config_parameters

    def get_required_config_tool_names(self):
        required_config_tool_names = super().get_required_config_tool_names()

        required_config_tool_names.extend(
            (
                BODATABASER_TOOL_NAME,
                BOWEBBB_TOOL_NAME,
                BOCONF_TOOL_NAME,
                BOCONF_GENERATOR_TOOL_NAME,
                BOPOSTGRES_TOOL_NAME,
                BOREGISTRY_TOOL_NAME,
                BOGIT_TOOL_NAME,
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
            '--format',
            action='store',
            type=str,
            default=ConfigurationFormatEnum.CONF,
        )

        parser.add_argument(
            '--result_configuration_dir_path',
            action='store',
            type=str,
            default=self._bodatabaser_config['databaser_general']['result_configuration_dir_path'].value,  # noqa
        )

        return parser

    def _validate_format(
        self,
        format_: str,
    ):
        """
        Валидация формата результирующего конфигурационного файла
        """
        if format_ not in ConfigurationFormatEnum.values.keys():
            raise RuntimeError(
                WRONG_CONFIGURATION_FILE_FORMAT_ERROR
            )

    def _validate_arguments(self):
        super()._validate_arguments()

        self._validate_format(
            format_=self._parsed_args.format,
        )

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
            configurations_git_repository_url = self._boconf_config.get(
                section='boconf',
                option='configurations_git_repository_url',
            )

            bo_config_generator = BOConfigGenerator(
                stand_url=self._parsed_args.stand_url,
                projects_combination=self._projects_combination,
                configurations_path=configurations_path,
                configurations_git_repository_url=(
                    configurations_git_repository_url.value
                ),
                settings_config=self._boconf_generator_config,
            )

            web_bb_config = bo_config_generator.generate()

            self._config['databaser_build']['region_abbreviation'].value = (
                web_bb_config['runtime']['app_region_abbreviation'].value
            )

            self._config['web_bb']['activated_plugins'].value = (
                web_bb_config['plugins']['activated_plugins'].value
            )

            self._config['databaser']['src_db_host'].value = (
                web_bb_config['database']['database_host'].value
            )
            self._config['databaser']['src_db_port'].value = (
                web_bb_config['database']['database_port'].value
            )
            self._config['databaser']['src_db_name'].value = (
                web_bb_config['database']['database_name'].value
            )
            self._config['databaser']['src_db_user'].value = (
                web_bb_config['database']['database_user'].value
            )
            self._config['databaser']['src_db_password'].value = (
                web_bb_config['database']['database_password'].value
            )

    def _fill_postgres_image_by_activated_projects(self):
        """
        Заполнение значения образа базы данных согласно подключенных проектов
        """
        image_name = generate_db_image_name(
            projects_combination=self._projects_combination,
            type_=DBImageTypeEnum.BASE,
            region=self._config['databaser_build']['region_abbreviation'].value,
        )

        if image_name and self._parsed_args.registry_url:
            db_image_name = f'{self._parsed_args.registry_url}/{image_name}'

            self._config['postgres']['image'] = db_image_name

    def _fill_destination_database_parameters(self):
        """
        Заполнение параметров целевой базы данных
        """
        if not self._config['databaser']['dst_db_host'].value:
            self._config['databaser']['dst_db_host'].value = (
                self._parsed_args.postgres_container_name
            )

        if not self._config['databaser']['dst_db_port'].value:
            self._config['databaser']['dst_db_port'].value = POSTGRES_DEFAULT_PORT

        if not self._config['databaser']['dst_db_name'].value:
            self._config['databaser']['dst_db_name'].value = self._parsed_args.postgres_db

        if not self._config['databaser']['dst_db_user'].value:
            self._config['databaser']['dst_db_user'].value = self._parsed_args.postgres_user

        if not self._config['databaser']['dst_db_password'].value:
            self._config['databaser']['dst_db_password'].value = (
                self._parsed_args.postgres_password
            )

    def _fill_config_from_arguments(self):
        super()._fill_config_from_arguments()

        self._fill_parameters_from_stand_configuration()

        self._fill_postgres_image_by_activated_projects()

        self._fill_destination_database_parameters()

    def _write_config(self):
        if self._parsed_args.format == ConfigurationFormatEnum.CONF:
            exporter_class = ConfExporter
        elif self._parsed_args.format == ConfigurationFormatEnum.ENV:
            exporter_class = EnvExporter

        exporter = exporter_class(
            tool_name=self.tool_name,
            config=self._config,
            configuration_dir_path=Path(
                self._parsed_args.result_configuration_dir_path or
                CONFIGURATION_DIRECTORY_PATH
            ),
        )

        configuration_file_path = exporter.export()

        logger.write(
            f'Configuration file created successfully. Configuration file '
            f'path - {configuration_file_path}\n'
        )


class RunDatabaserCommand(
    DatabaserArgumentsMixin,
    DatabaserBuildArgumentsMixin,
    JenkinsStandURLArgumentMixin,
    DockerArgumentsMixin,
    PostgresArgumentsMixin,
    RegistryURLArgumentsMixin,
    WebBBDockerMixin,
    WebBBActivatedPluginsConfigArgumentsMixin,
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
        return f'{BODATABASER_TOOL_NAME}-'

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

        parser.add_argument(
            '--result_image_tag',
            dest='result_image_tag',
            action='store',
            default='latest',
            type=str,
            help='Result image tag',
        )

        parser.add_argument(
            '--remove_result_db_image',
            dest='remove_result_db_image',
            action='store',
            default=False,
            type=lambda x: bool(strtobool(x)),
            help=(
                'Remove result destination db image after pushing image to '
                'Registry. Default: False.'
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
            configurations_git_repository_url = self._boconf_config.get(
                section='boconf',
                option='configurations_git_repository_url',
            )

            bo_config_generator = BOConfigGenerator(
                stand_url=self._parsed_args.stand_url,
                projects_combination=self._projects_combination,
                configurations_path=configurations_path,
                configurations_git_repository_url=(
                    configurations_git_repository_url.value
                ),
                settings_config=self._boconf_generator_config,
            )

            web_bb_config = bo_config_generator.generate()

            self._parsed_args.databaser_build_region_abbreviation = (
                web_bb_config['runtime']['app_region_abbreviation'].value
            )

            self._parsed_args.plugins_activated_plugins = (
                web_bb_config['plugins']['activated_plugins'].value
            )

            self._parsed_args.runtime_time_zone = (
                web_bb_config['runtime']['time_zone'].value
            )

            self._parsed_args.databaser_src_db_host = (
                web_bb_config['database']['database_host'].value
            )
            self._parsed_args.databaser_src_db_port = (
                web_bb_config['database']['database_port'].value
            )
            self._parsed_args.databaser_src_db_name = (
                web_bb_config['database']['database_name'].value
            )
            self._parsed_args.databaser_src_db_user = (
                web_bb_config['database']['database_user'].value
            )
            self._parsed_args.databaser_src_db_password = (
                web_bb_config['database']['database_password'].value
            )

    def _fill_postgres_image_by_activated_projects(self):
        """
        Заполнение значения образа базы данных согласно подключенных проектов
        """
        image_name = generate_db_image_name(
            projects_combination=self._projects_combination,
            type_=DBImageTypeEnum.BASE,
            region=self._parsed_args.databaser_build_region_abbreviation,
            tag=self._parsed_args.web_bb_app_branch,
        )

        if image_name and self._parsed_args.registry_url:
            db_image_name = f'{self._parsed_args.registry_url}/{image_name}'

            self._parsed_args.postgres_image = db_image_name

    def _fill_databaser_excluded_tables(self):
        """
        Заполнение значения параметра databaser_excluded_tables
        """
        value = self._parsed_args.databaser_excluded_tables

        if value:
            excluded_tables = set(
                filter(
                    None,
                    value.strip().replace(' ', '').split(',')
                )
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
                            default_databaser_excluded_tables.strip().replace(' ', '').split(',')  # noqa
                        )
                    )

                    excluded_tables = excluded_tables.union(
                        default_databaser_excluded_tables
                    )

            value = ','.join(sorted(excluded_tables))

        self._parsed_args.databaser_excluded_tables = value

    def _remove_artefacts(self):
        """
        Удаление контейнеров с базой и приложением
        """
        self._remove_container(
            container_id=self._parsed_args.web_bb_docker_container_name,
        )

        self._remove_container(
            container_id=self._parsed_args.databaser_build_container_name,
        )

        self._remove_container(
            container_id=self._parsed_args.postgres_container_name,
        )

        self._remove_image(
            name=self._parsed_args.postgres_image,
        )

        base_web_bb_app_image_name = (
            f'{self._parsed_args.registry_url}/{self._parsed_args.web_bb_docker_base_image_name}' if  # noqa
            self._parsed_args.registry_url else
            self._parsed_args.web_bb_docker_base_image_name
        )
        self._remove_image(
            name=base_web_bb_app_image_name,
        )

        web_bb_app_image_name = (
            f'{self._parsed_args.registry_url}/{self._parsed_args.web_bb_docker_image_name}' if  # noqa
            self._parsed_args.registry_url else
            self._parsed_args.web_bb_docker_image_name
        )
        self._remove_image(
            name=web_bb_app_image_name,
        )

    def _run_databaser(self):
        """
        Запуск Databaser
        """
        logger.write(
            f'pulling Databaser image '
            f'{self._parsed_args.databaser_build_image}..\n'
        )

        databaser_image = self._docker_client.images.pull(
            repository=self._parsed_args.databaser_build_image,
        )

        databaser_manager = DatabaserServiceManager(
            docker_client=self._docker_client,
            network=self._parsed_args.docker_network,
        )

        logger.write(
            'start working Databaser..\n'
        )

        databaser_manager.run(
            image=databaser_image,
            container_name=f'{self._container_prefix}{self._parsed_args.databaser_build_container_name}',  # noqa
            mem_limit=self._parsed_args.databaser_build_mem_limit,
            shm_size=self._parsed_args.databaser_build_shm_size,
            log_level=self._parsed_args.databaser_log_level,
            test_mode=self._parsed_args.databaser_test_mode,
            src_db_host=self._parsed_args.databaser_src_db_host,
            src_db_port=self._parsed_args.databaser_src_db_port,
            src_db_name=self._parsed_args.databaser_src_db_name,
            src_db_user=self._parsed_args.databaser_src_db_user,
            src_db_password=self._parsed_args.databaser_src_db_password,
            dst_db_host=f'{self._container_prefix}{self._parsed_args.postgres_container_name}',  # noqa
            dst_db_port=POSTGRES_DEFAULT_PORT,
            dst_db_name=self._parsed_args.postgres_db,
            dst_db_user=self._parsed_args.postgres_user,
            dst_db_password=self._parsed_args.postgres_password,
            key_table_name=self._parsed_args.databaser_key_table_name,
            key_column_names=self._parsed_args.databaser_key_column_names,
            key_column_values=self._parsed_args.databaser_key_column_values,
            key_table_hierarchy_column_name=(
                self._parsed_args.databaser_key_table_hierarchy_column_name
            ),
            excluded_tables=self._parsed_args.databaser_excluded_tables,
            tables_limit_per_transaction=(
                self._parsed_args.databaser_tables_limit_per_transaction
            ),
            tables_with_generic_foreign_key=(
                self._parsed_args.databaser_tables_with_generic_foreign_key
            ),
            is_truncate_tables=self._parsed_args.databaser_is_truncate_tables,
            tables_truncate_included=(
                self._parsed_args.databaser_tables_truncate_included
            ),
            tables_truncate_excluded=(
                self._parsed_args.databaser_tables_truncate_excluded
            ),
            full_transfer_tables=self._parsed_args.databaser_full_transfer_tables,
        )

        logger.write(
            'databaser working finished.\n'
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

        self._fill_databaser_excluded_tables()

        self._register_signals()

        self._prepare_base_web_bb_app_image()

        self._remove_artefacts()

        self._run_postgres_container()

        command = f'bash -c \'{" && ".join(DATABASER_RUN_WEB_BB_APP_CONTAINER_COMMANDS)}\''  # noqa
        self._run_web_bb_app(
            command=command,
        )

        self._run_databaser()

        full_image_repository = self._push_postgres_image(
            stream=False,
            tag=self._parsed_args.result_image_tag,
        )

        logger.write(
            f'<<<PARAMETERS>>>\n'
            f'stand_url = {self._parsed_args.stand_url}\n'
            f'databaser_log_level = {self._parsed_args.databaser_log_level}\n'
            f'databaser_test_mode = {self._parsed_args.databaser_test_mode}\n'
            f'databaser_key_table_name = {self._parsed_args.databaser_key_table_name}\n'
            f'databaser_key_column_names = {self._parsed_args.databaser_key_column_names}\n'
            f'databaser_key_column_values = {self._parsed_args.databaser_key_column_values}\n'
            f'databaser_key_table_hierarchy_column_name = {self._parsed_args.databaser_key_table_hierarchy_column_name}\n'
            f'databaser_excluded_tables = {self._parsed_args.databaser_excluded_tables}\n'
            f'databaser_tables_limit_per_transaction = {self._parsed_args.databaser_tables_limit_per_transaction}\n'
            f'databaser_tables_with_generic_foreign_key = {self._parsed_args.databaser_tables_with_generic_foreign_key}\n'
            f'databaser_is_truncate_tables = {self._parsed_args.databaser_is_truncate_tables}\n'
            f'databaser_tables_truncate_included = {self._parsed_args.databaser_tables_truncate_included}\n'
            f'databaser_tables_truncate_excluded = {self._parsed_args.databaser_tables_truncate_excluded}\n'
            f'databaser_full_transfer_tables = {self._parsed_args.databaser_full_transfer_tables}\n'
            f'<<</PARAMETERS>>>\n\n'
            f'<<<INSTRUCTION>>>\n\n'
            f'<<<AUTOMATIC.ENVIRONMENT.SETUP>>>\n'
            f'run >>$ botoolkit work on --jira_issue_id={self._parsed_args.databaser_build_task_id.upper()}\n'
            f'the command above will generate a configuration file and will launch a container with a database\n'
            f'more information about botoolkit - http://docs.budg.bars.group/botoolkit/\n'
            f'<<</AUTOMATIC.ENVIRONMENT.SETUP>>>\n\n'
            f'<<<MANUAL.ENVIRONMENT.SETUP>>>\n'
            f'<<<PROJECT.CONF>>>\n'
            f'ACTIVATED_PLUGINS = {self._parsed_args.plugins_activated_plugins}\n'  # noqa
            f'TIME_ZONE = {self._parsed_args.runtime_time_zone}\n'
            f'<<</PROJECT.CONF>>>\n\n'
            f'<<<PULL.IMAGE&RUN.DB.CONTAINER>>>\n'
            f'run >>$ docker run -d -p <container_exposed_port>:5432 {full_image_repository}:{self._parsed_args.result_image_tag}\n'  # noqa
            f'OR when using barsdock\n'
            f'run >>$ docker run -d -p <container_exposed_port>:5432 --network barsdnet --name database {full_image_repository}:{self._parsed_args.result_image_tag}\n'  # noqa
            f'<<</PULL.IMAGE&RUN.DB.CONTAINER>>>\n'
            f'<<</MANUAL.ENVIRONMENT.SETUP>>>\n\n'
            f'<<</INSTRUCTION>>>\n'
        )

        self._remove_artefacts()


class StopDatabaserCommand(
    DatabaserBuildContainerNameArgumentsMixin,
    PostgresContainerNameArgumentsMixin,
    WebBBDockerContainerNameArgumentsMixin,
    DockerServiceMixin,
    BOConfiguredToolCommand,
):
    """
    Команда для остановки запущенного Databaser и сопутствующих сервисов
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
            'Stopping Databaser.'
        )

    def get_container_prefix(self):
        return f'{BODATABASER_TOOL_NAME}-'

    def get_required_config_tool_names(self):
        required_config_tool_names = super().get_required_config_tool_names()

        required_config_tool_names.extend(
            (
                BODATABASER_TOOL_NAME,
                BOPOSTGRES_TOOL_NAME,
                BOWEBBB_TOOL_NAME,
                BOTOOLKIT_TOOL_NAME,
            )
        )

        return required_config_tool_names

    def _remove_artefacts(self):
        """
        Удаление контейнеров с базой и приложением
        """
        self._remove_container(
            container_id=self._parsed_args.web_bb_docker_container_name,
        )

        self._remove_container(
            container_id=self._parsed_args.databaser_build_container_name,
        )

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

        self._remove_artefacts()
