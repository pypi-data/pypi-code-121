import os
from argparse import (
    Namespace,
)
from collections import (
    defaultdict,
)
from copy import (
    copy,
)
from distutils.util import (
    strtobool,
)
from pathlib import (
    Path,
)
from typing import (
    Any,
    Dict,
    List,
    Set,
)

from configupdater import (
    ConfigUpdater,
)
from jenkins import (
    Jenkins,
)

from botoolkit.bo_conf.api import (
    BOConfigGenerator,
    BOBARSDockConfigGenerator,
)
from botoolkit.bo_conf.enums import (
    WebBBConfigOptionEnum,
    WebBBConfigSectionEnum,
)
from botoolkit.bo_conf.helpers import (
    get_stands_configs,
)
from botoolkit.bo_conf.mixins import (
    ConfiguratorArgumentsMixin,
    SkippedOptionsConfigArgumentMixin,
    WebBBConfigArgumentsMixin,
)
from botoolkit.bo_conf.settings import (
    GENERATOR_TOOL_NAME as BOCONF_GENERATOR_TOOL_NAME,
    TOOL_NAME as BOCONF_TOOL_NAME,
)
from botoolkit.bo_conf.strings import (
    FOUND_CONSISTENCY_CONFIGURATIONS_ERRORS,
    FOUND_DUPLICATED_CONFIGURATION_FILE_UUID_ERROR,
    FOUND_NOT_CONSISTENCY_PLUGINS_ERROR,
)
from botoolkit.bo_git.enums import (
    BranchEnum,
)
from botoolkit.bo_git.helpers import (
    clone_or_pull_repository,
)
from botoolkit.bo_git.mixins import (
    WebBBProjectsArgumentsMixin,
)
from botoolkit.bo_git.settings import (
    TOOL_NAME as BOGIT_TOOL_NAME,
)
from botoolkit.bo_guide.consts import (
    GUIDES_DIR_PATH,
)
from botoolkit.bo_jenkins.enums import (
    StandStateEnum,
)
from botoolkit.bo_jenkins.mixins import (
    JenkinsStandURLArgumentMixin,
)
from botoolkit.bo_jenkins.parsers import (
    JenkinsJobParser,
)
from botoolkit.bo_jenkins.settings import (
    TOOL_NAME as BOJENKINS_TOOL_NAME,
)
from botoolkit.bo_jenkins.strings import (
    STAND_URL_IS_NOT_URL_ERROR,
)
from botoolkit.bo_telegram.helpers import (
    TelegramMessageSender,
)
from botoolkit.bo_telegram.settings import (
    TOOL_NAME as BOTELEGRAM_TOOL_NAME,
)
from botoolkit.bo_toolkit.settings import (
    TOOL_NAME as BOTOOLKIT_TOOL_NAME,
)
from botoolkit.bo_web_bb.enums import (
    ProjectEnum,
    ProjectPluginEnum,
)
from botoolkit.core.commands import (
    BOConfiguredToolCommand,
    BOConfiguredToolConfigureCommand,
)
from botoolkit.core.consts import (
    ALLOWED_ALL_EMPTY_CONFIG_PARAMETERS,
)
from botoolkit.core.helpers import (
    fill_config_from_source,
    get_tool_conf_file_path,
)
from botoolkit.core.loggers import (
    logger,
)


class ConfigureBOConfCommand(
    ConfiguratorArgumentsMixin,
    SkippedOptionsConfigArgumentMixin,
    BOConfiguredToolConfigureCommand,
):
    """
    Конфигурирование инструмента boconf
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
            """Команда конфигурирования инструмента boconf для дальнейшего его использования.
            """
        )

    def get_tool_name(self):
        return BOCONF_TOOL_NAME

    def get_required_config_tool_names(self):
        required_config_tool_names = super().get_required_config_tool_names()

        required_config_tool_names.append(BOTOOLKIT_TOOL_NAME)

        return required_config_tool_names

    def get_allowed_empty_config_parameters(self):
        return ALLOWED_ALL_EMPTY_CONFIG_PARAMETERS

    def take_action(
        self,
        parsed_args: Namespace,
    ):
        super().take_action(
            parsed_args=parsed_args,
        )

        os.makedirs(
            name=str(GUIDES_DIR_PATH),
            exist_ok=True,
        )

        configurations_path = Path(
            self._config.get(
                section='boconf',
                option='configurations_path',
            ).value
        )
        configurations_git_repository_url = self._config.get(
            section='boconf',
            option='configurations_git_repository_url',
        )

        clone_or_pull_repository(
            path=configurations_path,
            url=configurations_git_repository_url.value,
        )


class BaseBOConfConfiguredCommand(
    BOConfiguredToolCommand,
):
    """
    Базовый класс для создания команд, для которых boconf должен быть
    сконфигурирован

    При выполнении команды производится считывание всех конфигов тестовых
    стендов
    """

    def get_required_config_tool_names(self):
        required_config_tool_names = super().get_required_config_tool_names()

        required_config_tool_names.append(BOCONF_TOOL_NAME)

        return required_config_tool_names

    def take_action(
        self,
        parsed_args: Namespace,
    ):
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

        self._test_stand_configs = get_stands_configs(
            configurations_git_repository_url=configurations_git_repository_url.value,
            configurations_path=configurations_path,
        )

        super().take_action(
            parsed_args=parsed_args,
        )


class CheckUnregisteredPluginsCommand(
    BaseBOConfConfiguredCommand,
):
    """
    Команда для поиска незарегистрированных и неиспользуемых плагинов
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
            'Проверка наличия незарегистрированных в botoolkit плагинов, находящихся в конфигурационных файлах '
            'тестовых  стендов.'
        )

    def take_action(
        self,
        parsed_args: Namespace,
    ):
        super().take_action(
            parsed_args=parsed_args,
        )

        plugins_from_configs = set()

        for _, config in self._test_stand_configs:
            plugins = map(
                lambda x: x.strip(),
                config['plugins']['ACTIVATED_PLUGINS'].value.split(',')
            )

            plugins_from_configs = plugins_from_configs.union(plugins)

        sorted_plugins = ProjectPluginEnum.get_all_plugins_str()

        unregistered_plugins = plugins_from_configs.difference(sorted_plugins)

        logger.write(
            f'Unregistered plugins: {", ".join(unregistered_plugins)}\n'
        )

        unused_plugins = sorted_plugins.difference(plugins_from_configs)

        logger.write(f'unused plugins: {", ".join(unused_plugins)}\n')


class CheckUnregisteredOptionsCommand(
    BaseBOConfConfiguredCommand,
):
    """
    Команда незарегистрированных в инструменте опций конфигурационных файлов
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
            'Проверка наличия незарегистрированных опций конфигурационных файлов в botoolkit.'
        )

    def take_action(
        self,
        parsed_args: Namespace,
    ):
        super().take_action(
            parsed_args=parsed_args,
        )

        configs_options: Dict[str, Dict[str, List[str]]] = {}
        for config_path_str, config in self._test_stand_configs:
            for section in config.sections():
                if section not in configs_options:
                    configs_options[section] = {}
                for option in config[section]:
                    if option not in configs_options[section]:
                        configs_options[section][option] = []

                    configs_options[section][option].append(config_path_str)

        unregistered_options: Dict[str, Set] = defaultdict(set)
        for section in configs_options.keys():
            for option in configs_options[section]:
                if (section, option) not in WebBBConfigOptionEnum.values.keys():
                    unregistered_options[section].add(option)

        if unregistered_options:
            unregistered_options_strs = [
                'Found unregistered options!',
            ]
            for section in sorted(unregistered_options.keys()):
                unregistered_options_strs.append(
                    f'\n[{section}]'
                )

                for option in sorted(unregistered_options[section]):
                    unregistered_options_strs.append(
                        f'{option} = \n'
                        f'{",".join(configs_options[section][option])}'
                    )

            logger.write(
                '\n'.join(unregistered_options_strs)
            )
        else:
            logger.write('unregistered options not found!\n')


class ConfigureBOConfGeneratorCommand(
    WebBBConfigArgumentsMixin,
    BOConfiguredToolConfigureCommand,
):
    """
    Команда для конфигурирования генератора конфигурационных файлов web_bb
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

        self.description = 'Команда для конфигурирования генератора конфигурационных файлов (boconf generator).'

    def get_tool_name(self):
        return BOCONF_GENERATOR_TOOL_NAME

    def get_allowed_empty_config_parameters(self):
        return ALLOWED_ALL_EMPTY_CONFIG_PARAMETERS

    def get_required_config_tool_names(self):
        required_config_tool_names = super().get_required_config_tool_names()

        required_config_tool_names.append(BOCONF_TOOL_NAME)

        return required_config_tool_names

    def _create_config(self):
        """
        Создание конфига
        """
        self._config = ConfigUpdater()

        for section in WebBBConfigSectionEnum.values.keys():
            self._config.add_section(
                section=section,
            )

        for section, option in WebBBConfigOptionEnum.values.keys():
            self._config.set(
                section=section,
                option=option,
                value='',
            )

        tool_conf_file_path = get_tool_conf_file_path(
            tool_name=self.tool_name,
        )

        if not self._parsed_args.clear and tool_conf_file_path.exists():
            old_config = ConfigUpdater()
            old_config.read(str(tool_conf_file_path))

            fill_config_from_source(
                src_config=old_config,
                dst_config=self._config,
            )

    def _get_property_value_from_required_configs(
        self,
        section: str,
        option: str,
    ):
        """
        Получение значений параметров из обязательных конфигов
        """
        if (section, option) in WebBBConfigOptionEnum.values.keys():
            value = ''
        else:
            value = super()._get_property_value_from_required_configs(
                section=section,
                option=option,
            )

        return value


class GenerateBOConfGeneratorCommand(
    JenkinsStandURLArgumentMixin,
    WebBBProjectsArgumentsMixin,
    SkippedOptionsConfigArgumentMixin,
    BOConfiguredToolCommand,
):
    """
    Команда генерации конфигурационных файлов
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
            'Команда генерации конфигурационного файла на основе конфигурационного файла указанно тестового стенда с '
            'учетом подключенных проектов.'
        )

    def get_required_config_tool_names(self):
        required_config_tool_names = super().get_required_config_tool_names()

        required_config_tool_names.extend(
            (
                BOCONF_TOOL_NAME,
                BOCONF_GENERATOR_TOOL_NAME,
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
            '--result_configuration_path',
            action='store',
            type=str,
            default=str(
                Path(self._boconf_config['boconf_generator']['generating_configuration_dir_path'].value) / 'project.conf'  # noqa
            ),
        )

        parser.add_argument(
            '--barsdock',
            dest='barsdock',
            action='store',
            default=False,
            type=lambda x: bool(strtobool(x)),
            help=(
                'Need generate configuration file (project.conf) for barsdock. '
                'Default: False.'
            ),
        )

        return parser

    def _validate_stand_url(self):
        """
        Валидация значения параметра stand_url
        """
        if self._parsed_args.stand_url:
            super()._validate_stand_url()
        else:
            raise RuntimeError(STAND_URL_IS_NOT_URL_ERROR)

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
        configurations_git_repository_url = self._boconf_config.get(
            section='boconf',
            option='configurations_git_repository_url',
        )

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

        generator_class = (
            BOBARSDockConfigGenerator
            if parsed_args.barsdock
            else BOConfigGenerator
        )

        bo_config_generator = generator_class(
            stand_url=self._parsed_args.stand_url,
            projects_combination=self._projects_combination,
            settings_config=self._boconf_generator_config,
            configurations_path=configurations_path,
            configurations_git_repository_url=configurations_git_repository_url.value,
            skipped_options=skipped_options,
        )

        bo_config_generator.generate()
        bo_config_generator.export(
            result_configuration_path=Path(self._parsed_args.result_configuration_path),  # noqa
        )

        logger.write(
            f'configuration file created successfully.\nConfiguration file '
            f'path - {self._parsed_args.result_configuration_path}\n'
        )


class CheckConfigurationConsistencyCommand(
    BOConfiguredToolCommand,
):
    """
    Команда для проверки консистентности конфигурационных файлов доступных
    тестовых стендов

    Проверка осуществляется по следующим направлениям:

    - Соответствие состава плагинов. Должно соблюдаться соответствие состава
        плагинов в следующем порядке default -> test -> dev Это означает, что
        все плагины, подключенные на default должны быть на test. Все плагины
        подключенные на test должны быть на dev. Плагины тестовых стендов с
        одинаковой веткой и регионом должны быть синхронизированы и полностью
        соответствовать

    - Уникальность UUID конфигурационных файлов
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
            'Команда для проверки консистентности конфигурационных файлов доступных тестовых стендов.'
        )

        self._configurations_map = {}
        self._duplicated_uuids = {}
        self._errors = []

    def get_required_config_tool_names(self):
        required_config_tool_names = super().get_required_config_tool_names()

        required_config_tool_names.extend(
            (
                BOTELEGRAM_TOOL_NAME,
                BOCONF_TOOL_NAME,
                BOJENKINS_TOOL_NAME,
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
            '--notify',
            dest='notify',
            action='store',
            default=False,
            type=lambda x: bool(strtobool(x)),
            help='Notify developers about configurations errors.',
        )

        return parser

    def _collect_configurations_data(self):
        """
        Сбор данных для дальнейшей проверки
        """
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

        jenkins_server = Jenkins(
            url=self._bojenkins_config['jenkins']['url'].value,
            username=self._bojenkins_config['jenkins']['username'].value,
            password=self._bojenkins_config['jenkins']['password'].value,
        )

        jenkins_job_parser = JenkinsJobParser(
            jenkins_server=jenkins_server,
        )

        jenkins_job_parser.parse()

        jobs_data = jenkins_job_parser.get_jobs_data_as_tuple(
            state=StandStateEnum.AVAILABLE,
        )

        for region, branch, url, configuration_file_uuid, job_url in jobs_data:
            branch = getattr(BranchEnum, branch.upper())

            if region not in self._configurations_map:
                self._configurations_map[region] = {}

            if branch not in self._configurations_map[region]:
                self._configurations_map[region][branch] = []

            bo_config_generator = BOConfigGenerator(
                stand_url=url,
                projects_combination=ProjectEnum.get_projects(),
                configurations_path=configurations_path,
                configurations_git_repository_url=(
                    configurations_git_repository_url.value
                ),
            )

            stand_config = bo_config_generator.generate()

            plugins = list(
                map(
                    lambda x: x.strip(),
                    stand_config.get(
                        section='plugins',
                        option='activated_plugins',
                    ).value.split(',')
                )
            )

            self._configurations_map[region][branch].append(
                {
                    'path': bo_config_generator.stand_configuration_path,
                    'url': url,
                    'plugins': plugins,
                    'uuid': configuration_file_uuid,
                    'is_main': False,
                    'job_url': job_url,
                }
            )

    def _check_plugins_consistency(
        self,
        region: str,
        branches: List[BranchEnum],
        main_configuration_params: Dict[str, Any],
        main_configuration_branch: BranchEnum,
    ):
        """
        Проверка целостности и согласованности конфигурационных файлов тестовых
        стендов одного региона по приоритету

        В параметрах передается главный конфиг на который должны
        ориентироваться остальные
        """
        for branch in branches:
            for configuration_params in self._configurations_map[region][branch]:  # noqa
                if configuration_params['is_main']:
                    continue

                plugins_difference = list(
                    set(main_configuration_params['plugins']).difference(
                        configuration_params['plugins']
                    )
                )

                if plugins_difference:
                    error_message = (
                        f'{FOUND_NOT_CONSISTENCY_PLUGINS_ERROR}\n'
                        f'Main configuration file path ('
                        f'{main_configuration_branch.value}) - '
                        f'{main_configuration_params["path"]}\n'
                        f'Configuration file path ({branch.value}) - '
                        f'{configuration_params["path"]}\n'
                        f'Difference - {", ".join(plugins_difference)}\n\n'
                    )

                    self._errors.append(error_message)

                    logger.write(
                        error_message
                    )

    def _check_unique_configuration_file_uuid(
        self,
        region: str,
        branch: BranchEnum,
    ):
        """
        Проверка UUID конфигурационных файлов на уникальность
        """
        for configuration_params in self._configurations_map[region][branch]:
            if configuration_params['uuid'] in self._duplicated_uuids:
                duplicated_configuration_params = self._duplicated_uuids[configuration_params['uuid']]

                error_message = (
                    f'{FOUND_DUPLICATED_CONFIGURATION_FILE_UUID_ERROR}\n'
                    f'UUID - {configuration_params["uuid"]}, stand urls:\n'
                    f'{duplicated_configuration_params[0]} - {duplicated_configuration_params[1]}\n'
                    f'{configuration_params["url"]} - {configuration_params["job_url"]}\n'
                )

                self._errors.append(error_message)

                logger.write(
                    error_message
                )
            else:
                self._duplicated_uuids[configuration_params['uuid']] = (
                    configuration_params['url'],
                    configuration_params['job_url'],
                )

    def _validate_configurations_data(self):
        """
        Проверка конфигурационных файлов сгруппированных по регионам и веткам
        """
        for region in self._configurations_map.keys():
            branches = list(
                sorted(
                    self._configurations_map[region].keys(),
                    key=lambda b: b.weight(),
                    reverse=True,
                )
            )

            # Запоминаем главный конфиг для дальнейшего сравнения
            main_configuration_params = (
                self._configurations_map[region][branches[0]][0]
            )
            main_configuration_params['is_main'] = True

            # Запоминаем ветку главного конфига
            main_configuration_branch = branches[0]

            for branch in copy(branches):
                self._check_plugins_consistency(
                    region=region,
                    branches=branches,
                    main_configuration_params=main_configuration_params,
                    main_configuration_branch=main_configuration_branch,
                )

                # Удаляется главная ветка с переходом на новый уровень проверки
                branches.remove(branch)

                # Установка главного конфига и ветки для дальнейшего перехода
                # на новый уровень проверки
                main_configuration_params = (
                    self._configurations_map[region][branch][0]
                )
                main_configuration_params['is_main'] = True
                main_configuration_branch = branch

                self._check_unique_configuration_file_uuid(
                    region=region,
                    branch=branch,
                )

    def take_action(
        self,
        parsed_args: Namespace,
    ):
        super().take_action(
            parsed_args=parsed_args,
        )

        self._collect_configurations_data()

        self._validate_configurations_data()

        if self._errors:
            if parsed_args.notify:
                telegram_sender = TelegramMessageSender(
                    bot_api_token=self._botelegram_config['telegram']['bot_api_token'].value,
                    chat_ids=(
                        self._boconf_config['boconf']['notification_telegram_chat_id'].value,
                    ),
                )

                error_messages = '\n'.join(self._errors)

                telegram_sender.send(
                    message=(
                        f'\U0001F640 При проверке конфигурационных файлов тестовых стендов были выявлены ошибки:\n\n'
                        f'{error_messages}'
                    ),
                )

            raise RuntimeError(FOUND_CONSISTENCY_CONFIGURATIONS_ERRORS)
