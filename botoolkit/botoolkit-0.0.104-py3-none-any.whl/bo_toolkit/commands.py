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
    BOBARSDockConfigGenerator,
)
from botoolkit.bo_conf.mixins import (
    ConfiguratorArgumentsMixin,
    SkippedOptionsConfigArgumentMixin,
)
from botoolkit.bo_conf.settings import (
    GENERATOR_TOOL_NAME as BOCONF_GENERATOR_TOOL_NAME,
    TOOL_NAME as BOCONF_TOOL_NAME,
)
from botoolkit.bo_databaser.mixins import (
    DatabaserArgumentsMixin,
    DatabaserGeneralArgumentsMixin,
)
from botoolkit.bo_barsdock.mixins import (
    BOBARSDockGeneralArgumentsMixin,
)
from botoolkit.bo_git.mixins import (
    WebBBBranchesArgumentsMixin,
    WebBBProjectsArgumentsMixin,
)
from botoolkit.bo_git.settings import (
    TOOL_NAME as BOGIT_TOOL_NAME,
)
from botoolkit.bo_guide.mixins import (
    GuideArgumentsMixin,
)
from botoolkit.bo_jenkins.mixins import (
    JenkinsDatabaserArgumentsMixin,
)
from botoolkit.bo_jira.api import (
    JiraAPIClient,
)
from botoolkit.bo_jira.mixins import (
    JiraArgumentsMixin,
    JiraIssueIDArgumentsMixin,
    JiraTaskJenkinsStandURLArgumentMixin,
)
from botoolkit.bo_jira.settings import (
    TOOL_NAME as BOJIRA_TOOL_NAME,
)
from botoolkit.bo_postgres.mixins import (
    PostgresArgumentsMixin,
    PostgresServiceCommandMixin,
)
from botoolkit.bo_postgres.settings import (
    TOOL_NAME as BOPOSTGRES_TOOL_NAME,
)
from botoolkit.bo_registry.mixins import (
    RegistryArgumentsMixin,
    RegistryClientArgumentMixin,
)
from botoolkit.bo_registry.settings import (
    TOOL_NAME as BOREGISTRY_TOOL_NAME,
)
from botoolkit.bo_telegram.mixins import (
    TelegramArgumentMixin,
)
from botoolkit.bo_toolkit.mixins import (
    BOToolkitGeneralArgumentsMixin,
)
from botoolkit.bo_toolkit.settings import (
    TOOL_NAME as BOTOOLKIT_TOOL_NAME,
)
from botoolkit.bo_web_bb.mixins import (
    WebBBDockerMixin,
)
from botoolkit.core.commands import (
    BOConfigureCommand,
    BOConfiguredToolCommand,
)
from botoolkit.core.consts import (
    ALLOWED_ALL_EMPTY_CONFIG_PARAMETERS,
)
from botoolkit.core.helpers import (
    get_all_configured_tool_apps,
    get_tool_conf_file_path,
)
from botoolkit.core.loggers import (
    logger,
)
from botoolkit.core.mixins import (
    DockerServiceMixin,
    RemoveArtefactsOnAbortMixin,
)
from botoolkit.settings import (
    CONFIGURATION_DIRECTORY_PATH,
)


class ConfigureBOToolKitCommand(
    BOToolkitGeneralArgumentsMixin,
    JenkinsDatabaserArgumentsMixin,
    PostgresArgumentsMixin,
    RegistryArgumentsMixin,
    JiraArgumentsMixin,
    WebBBBranchesArgumentsMixin,
    ConfiguratorArgumentsMixin,
    WebBBDockerMixin,
    DatabaserGeneralArgumentsMixin,
    DatabaserArgumentsMixin,
    BOBARSDockGeneralArgumentsMixin,
    GuideArgumentsMixin,
    TelegramArgumentMixin,
    BOConfigureCommand,
):
    """
    Команда конфигурирования инструмента bo_toolkit
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

        self.description = 'Command for configuring the botoolkit.'

    def get_tool_name(self):
        return BOTOOLKIT_TOOL_NAME

    def get_allowed_empty_config_parameters(self):
        return ALLOWED_ALL_EMPTY_CONFIG_PARAMETERS

    def _create_configuration_directory(self):
        """
        Создание основной рабочей директории ~/.botoolkit
        """
        is_exists = CONFIGURATION_DIRECTORY_PATH.exists()

        CONFIGURATION_DIRECTORY_PATH.mkdir(
            mode=0o700,
            exist_ok=True,
        )

        if not is_exists:
            logger.write(
                'Configuration directory created.\n'
            )

    def _rewrite_all_configuration_files(self):
        """
        Переконфигурирование всех инструментов на основе генерируемого
        конфигурационного файла botoolkit.conf
        """
        all_tool_apps = get_all_configured_tool_apps(
            exclude=(
                self.tool_name,
            ),
        )

        sorted_tool_names = sorted(
            (
                (
                    tool_name,
                    tool_data['index'],
                )
                for tool_name, tool_data in all_tool_apps.items() if
                tool_name != self.tool_name
            ),
            key=lambda t: t[1],
        )

        for tool_name, index in sorted_tool_names:
            tool_data = all_tool_apps[tool_name]

            if tool_data['is_configured']:
                tool_conf_file_path = get_tool_conf_file_path(
                    tool_name=tool_name,
                )

                action = 'rewrite' if tool_conf_file_path.exists() else 'create'
                logger.write(
                    f'{action.capitalize()} configuration file of '
                    f'"{tool_name.replace("_", " ")}" tool from '
                    f'botoolkit.conf..\n'
                )

                tool_app = tool_data['app_class']()

                command = 'configure'

                sub_tool_name = ' '.join(tool_name.split('_')[1:])
                if sub_tool_name:
                    command = f'{sub_tool_name} {command}'

                tool_app.run(
                    argv=(
                        command,
                        '--clear',
                    ),
                )

    def get_parser(
        self,
        prog_name,
    ):
        parser = super().get_parser(
            prog_name=prog_name,
        )

        parser.add_argument(
            '--all',
            dest='all',
            action='store_true',
            default=False,
            help='Заполнить все конфигурационные файлы на основе параметров из botoolkit.conf.',
        )

        return parser

    def take_action(
        self,
        parsed_args: Namespace,
    ):
        self._create_configuration_directory()

        super().take_action(
            parsed_args=parsed_args,
        )

        if self._parsed_args.all:
            self._rewrite_all_configuration_files()


class BOToolkitWorkOnCommand(
    RegistryClientArgumentMixin,
    RegistryArgumentsMixin,
    JiraArgumentsMixin,
    JiraIssueIDArgumentsMixin,
    JiraTaskJenkinsStandURLArgumentMixin,
    WebBBProjectsArgumentsMixin,
    SkippedOptionsConfigArgumentMixin,
    PostgresArgumentsMixin,
    DockerServiceMixin,
    PostgresServiceCommandMixin,
    RemoveArtefactsOnAbortMixin,
    BOConfiguredToolCommand,
):
    """
    Команда для настройки окружения для работы над задачей. В текущий момент
    реализован функционал:

        - Если уже имеется срез БД для решаемой задачи, то образ скачивается из
        Registry и поднимается контейнер с именем <task_id>_database;
        - Следующим этапом генерируется конфигурационный файл на основе конфига
        тестового стенда, подключенных проектов и базой, с которой будет
        производиться работа.
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
            """Команда настройки окружения разработчика для работы над задачей.            
            
            Данная команда осуществляет следующие действия:
            
            - Проверяет и выкачивает Docker-образ содержащий срез базы данных, полученный при помощи Databaser, в 
              случае его наличия;
            - При наличии образа, поднимает контейнер с именем, формируемым по шаблону ``{issue_id_lower}-database``.
              По умолчанию, расшаривается порт ``5432``, указанный в конфигурационном файле. В случае необходимости, 
              можно произвести изменение порта в конфигурационном файле в секции ``postgres`` в параметре ``port``. Так 
              же порт можно указать при помощи параметра команды ``--postgres_port``. Если контейнер уже существует, 
              то он не будет пересоздан. В случае, если он был остановлен, он будет запущен заново;
            - В зависимости от наличия поднятого контейнера с Postgres и срезом БД, производится генерация 
              конфигурационного файла. Т.к. в качестве обязательного параметра команды является ``--jira_issue_id`` 
              идентификатор задачи в Jira, определение тестового стенда производится исходя из описания задачи. В 
              секции Параметры подключения указан URL, благодаря которому определяется UUID конфигурационного файла. 
              После определения конфигурационного файла, производится его разбор. Набор плагинов формируется на 
              основе проекта, указанного в задаче. В результате генерируется конфигурационный файл по пути, 
              указанному в конфигурационном файле в секции ``boconf_generator`` в параметре 
              ``generating_configuration_dir_path`` с именем ``project.conf`` Обычно это директория 
              ``web_bb_app/src/web_bb_app``. Можно указать абсолютный путь генерируемого конфигурационного файла 
              при помощи параметра ``--result_configuration_path``. Если по указанному пути уже существует 
              конфигурационный файл, то он будет затерт и создан новый. 
              
            После завершения работы команды, разработчик получает настроенное окружение, где ему остается только 
            создать необходимые ветки в изменяемых проектах и приступить к работе.
            
            Если в параметрах запуска указать ``--with-database=False``, то подготовка окружения будет производиться 
            без создания контейнера с базой данных. Это пригодится, когда нужно только сгенерировать
            конфигурационный файл. По умолчанию база данных создается по описанной ранее логике.
            
            Если в параметрах запуска указать ``--with-config=False``, то подготовка окружения будет производиться 
            без создания конфигурационного файла. Это понадобится, например, в случае поднятия контейнера с базой 
            данных на удаленной машине. 
            """
        )

        self._issue = None
        self._with_databaser_slice = False

        self._registry_api_client = None
        self._jira_client = None

    def get_required_config_tool_names(self):
        required_config_tool_names = super().get_required_config_tool_names()

        required_config_tool_names.extend(
            (
                BOJIRA_TOOL_NAME,
                BOCONF_TOOL_NAME,
                BOCONF_GENERATOR_TOOL_NAME,
                BOGIT_TOOL_NAME,
                BOPOSTGRES_TOOL_NAME,
                BOREGISTRY_TOOL_NAME,
                BOTOOLKIT_TOOL_NAME,
            )
        )

        return required_config_tool_names

    def get_allowed_empty_config_parameters(self):
        """
        Параметры, которые могут иметь пустые значения в конфиге или не
        указываться вовсе
        """
        allowed_empty_config_parameters = (
            super().get_allowed_empty_config_parameters()
        )

        allowed_empty_config_parameters.update(
            {
                'jira': [
                    'issue_id',
                ],
            }
        )

        return allowed_empty_config_parameters

    def patch_arguments_schema(self):
        super().patch_arguments_schema()

        self._arguments_schema.extend(
            (
                {
                    'section': 'docker',
                    'option': 'network',
                    'help': 'Network using in running containers.',
                },
                {
                    'section': 'docker',
                    'option': 'shm_size',
                    'help': 'Size of /dev/shm.',
                },
                {
                    'section': 'docker',
                    'option': 'cpu_max_count',
                    'help': 'Max count CPUs in which to allow execution.',
                },

            )
        )

    def get_parser(
        self,
        prog_name,
    ):
        parser = super().get_parser(
            prog_name=prog_name,
        )

        parser.add_argument(
            '--result_configuration_path',
            action='store',
            type=str,
            default=str(
                Path(self._boconf_config['boconf_generator']['generating_configuration_dir_path'].value) / 'project.conf'
            ),
            help='Абсолютный путь генерируемого конфигурационного файла',
        )

        parser.add_argument(
            '--with_database',
            dest='with_database',
            action='store',
            default=True,
            type=lambda x: bool(strtobool(x)),
            help='Осуществлять подготовку окружения с созданием контейнера с базой данных. По умолчанию True',
        )

        parser.add_argument(
            '--with_config',
            dest='with_config',
            action='store',
            default=True,
            type=lambda x: bool(strtobool(x)),
            help='Осуществлять подготовку окружения с генерацией конфигурационного файла. По умолчанию True',
        )

        return parser

    def _prepare_jira_client(self):
        """
        Подготовка клиента Jira
        """
        self._jira_client = JiraAPIClient(
            url=self._parsed_args.jira_url,
            username=self._parsed_args.jira_username,
            password=self._parsed_args.jira_password,
        )

    def _prepare_registry_api_client(self):
        """
        Подготовка клиента Registry
        """
        self._registry_api_client = self._parsed_args.registry_client(
            registry_domain=self._parsed_args.registry_url,
            username=self._parsed_args.registry_user,
            password=self._parsed_args.registry_password,
            verify=False,
        )

    def _remove_artefacts(self):
        """
        Удаление образов и контейнеров в случае неудачи
        """
        self._remove_container(
            container_id=self._get_postgres_container_name(),
        )

    def _get_postgres_container_name(self):
        """
        Возвращает имя контейнера с Postgres
        """
        issue_id_lower = self._parsed_args.jira_issue_id.lower()

        return f'{issue_id_lower}-database'

    def _check_and_up_db_container(self):
        """
        Проверяет наличие среза БД в Registry. В случае наличия скачивает его и
        поднимает контейнер с базой
        """
        issue_id_lower = self._parsed_args.jira_issue_id.lower()

        issue_repositories = [
            repository
            for repository in self._registry_api_client.get_repositories()
            if issue_id_lower in repository
        ]

        if issue_repositories:
            issue_repository = issue_repositories[0]

            if '/' in issue_repository:
                issue_repository_parts = issue_repository.split('/')

                issue_repository = issue_repository_parts[1]

            self._parsed_args.postgres_image = (
                f'{self._parsed_args.registry_url}/{issue_repository}:latest'
            )
            self._parsed_args.pull_postgres_image = True

            self._start_postgres_container()

            self._with_databaser_slice = True

    def _generate_configuration_file(self):
        """
        Генерация конфигурационного файла
        """
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

        skipped_options = []
        skipped_options_str = (
            self._boconf_config.get('boconf_generator', 'skipped_options').value
        )
        if skipped_options_str:
            skipped_options = list(
                map(
                    lambda s_o: s_o.strip(),
                    skipped_options_str.split(',')
                )
            )

        bo_config_generator = BOBARSDockConfigGenerator(
            stand_url=self._parsed_args.stand_url,
            projects_combination=self._projects_combination,
            settings_config=self._boconf_generator_config,
            configurations_path=configurations_path,
            configurations_git_repository_url=configurations_git_repository_url,
            skipped_options=skipped_options,
            with_databaser_slice=self._with_databaser_slice,
        )

        config = bo_config_generator.generate()

        if self._with_databaser_slice:
            config.set(
                section='database',
                option='database_host',
                value=self._get_postgres_container_name(),
            )

            config.set(
                section='async_database',
                option='database_host',
                value=self._get_postgres_container_name(),
            )

        bo_config_generator.export(
            result_configuration_path=Path(self._parsed_args.result_configuration_path),  # noqa
        )

    def _validate_arguments(self):
        self._prepare_jira_client()

        super()._validate_arguments()

        self._prepare_registry_api_client()

    def take_action(
        self,
        parsed_args: Namespace,
    ):
        super().take_action(
            parsed_args=parsed_args,
        )

        logger.write(
            f'configuring environment for Issue with number '
            f'{self._parsed_args.jira_issue_id}..\n'
        )

        if self._parsed_args.with_database:
            self._check_and_up_db_container()

        if self._parsed_args.with_config:
            self._generate_configuration_file()

        logger.write(
            f'configuring environment for Issue with number '
            f'{self._parsed_args.jira_issue_id} finished. \n'
        )


class BOToolkitWorkOffCommand(
    JiraArgumentsMixin,
    JiraIssueIDArgumentsMixin,
    DockerServiceMixin,
    BOConfiguredToolCommand,
):
    """
    Команда завершения работы над задачей
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.description = (
            """Команда завершения работы над задачей. 
            
            Занимается удалением контейнеров с БД и образов срезов БД, связанных с задачей, на локальной машине. Таким 
            образом, удаляются все артефакты, после завершения работы над задачей.
            """
        )

        self._jira_client = None

    def get_required_config_tool_names(self):
        required_config_tool_names = super().get_required_config_tool_names()

        required_config_tool_names.extend((BOTOOLKIT_TOOL_NAME,))

        return required_config_tool_names

    def get_allowed_empty_config_parameters(self):
        """
        Параметры, которые могут иметь пустые значения в конфиге или не
        указываться вовсе
        """
        allowed_empty_config_parameters = super().get_allowed_empty_config_parameters()

        allowed_empty_config_parameters.update({'jira': ['issue_id']})

        return allowed_empty_config_parameters

    def _prepare_jira_client(self):
        """
        Подготовка клиента Jira
        """
        self._jira_client = JiraAPIClient(
            url=self._parsed_args.jira_url,
            username=self._parsed_args.jira_username,
            password=self._parsed_args.jira_password,
        )

    def _validate_arguments(self):
        self._prepare_jira_client()

        super()._validate_arguments()

    def _remove_containers(self):
        """
        Удаление контейнеров связанных с задачей
        """
        logger.write(f'start removing containers of Jira issue {self._parsed_args.jira_issue_id}..\n')

        containers = self._docker_client.containers.list(all=True)

        issue_id_lower = self._parsed_args.jira_issue_id.lower()

        issue_containers = [c for c in containers if issue_id_lower in c.name.lower()]

        if issue_containers:
            for container in issue_containers:
                logger.write(f'removing container with name {container.name}..\n')

                container.remove(v=True, force=True)

            logger.write(f'removing containers of Jira issue {self._parsed_args.jira_issue_id} finised.\n')
        else:
            logger.write(f'containers of Jira issue {self._parsed_args.jira_issue_id} not found.\n')

    def _remove_images(self):
        """
        Удаление образов связанных с задачей
        """
        logger.write(f'start removing images of Jira issue {self._parsed_args.jira_issue_id}..\n')

        issue_id_lower = self._parsed_args.jira_issue_id.lower()

        images = self._docker_client.images.list()
        issue_images = [
            image
            for image in images if (
                image.attrs['RepoTags']
                and any([issue_id_lower in tag for tag in image.attrs['RepoTags']])
            )
        ]

        if issue_images:
            for image in issue_images:
                repo_tag = [tag for tag in image.attrs['RepoTags'] if issue_id_lower in tag][0]
                logger.write(f'removing image with repo tag {repo_tag}..\n')

                self._docker_client.images.remove(image=image.id, force=True)

            logger.write(f'removing images of Jira issue {self._parsed_args.jira_issue_id} finished.\n')
        else:
            logger.write(f'images of Jira issue {self._parsed_args.jira_issue_id} not found.\n')

    def take_action(
        self,
        parsed_args: Namespace,
    ):
        super().take_action(parsed_args=parsed_args)

        logger.write(f'start removing artefacts of Jira issue {parsed_args.jira_issue_id}..\n')

        self._remove_containers()
        self._remove_images()

        logger.write(f'removing artefacts of Jira issue {parsed_args.jira_issue_id} finished.\n')
