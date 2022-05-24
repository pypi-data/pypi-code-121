from configparser import (
    NoOptionError,
)
from pathlib import (
    Path,
)
from typing import (
    Iterable,
    List,
    Optional,
)

from configupdater import (
    ConfigUpdater,
)
from validators import (
    ipv4,
)

from botoolkit.bo_conf.consts import (
    ALL,
    SECTION_OPTION_DELIMITER,
)
from botoolkit.bo_conf.enums import (
    WebBBConfigOptionEnum,
    WebBBConfigSectionEnum,
)
from botoolkit.bo_conf.helpers import (
    get_web_bb_test_stands_configurations_dir_path,
)
from botoolkit.bo_git.helpers import (
    clone_or_pull_repository,
)
from botoolkit.bo_postgres.consts import (
    POSTGRES_DEFAULT_PORT,
)
from botoolkit.bo_web_bb.api import (
    WebBBAPI,
)
from botoolkit.bo_web_bb.enums import (
    ProjectEnum,
    ProjectPluginEnum,
)
from botoolkit.bo_web_bb.exceptions import (
    ConfigurationFileNotFoundByUUID,
)
from botoolkit.core.helpers import (
    fill_config_from_source,
)
from botoolkit.core.loggers import (
    logger,
)


class BOConfigGenerator:
    """
    Генератор конфигурационных файлов приложения web_bb на основе конфигов
    тестовых стендов
    """

    def __init__(
        self,
        stand_url: str,
        projects_combination: Iterable[ProjectEnum],
        configurations_path: Path,
        configurations_git_repository_url: str,
        settings_config: Optional[ConfigUpdater] = None,
        skipped_options: Optional[List[str]] = None,
    ):
        self._stand_url = stand_url
        self._stand_config: Optional[ConfigUpdater] = None
        self._stand_config_path: Optional[Path] = None

        self._projects_combination = projects_combination
        self._settings_config = settings_config

        self._configurations_path = configurations_path
        self._configurations_git_repository_url = (
            configurations_git_repository_url
        )

        self._skipped_options = skipped_options

        self._result_config = ConfigUpdater(allow_no_value=True)

    @property
    def stand_configuration_path(self) -> Path:
        """
        Возвращает абсолютный путь конфигурационного файла
        """
        return self._stand_config_path

    def _get_stand_config_uuid(self) -> str:
        """
        Получение UUID конфигурационного файла тестового стенда
        """
        web_bb_api = WebBBAPI(
            stand_url=self._stand_url,
        )
        config_uuid = web_bb_api.get_app_config_uuid()

        return config_uuid

    def _get_stand_config(self):
        """
        Поиск и установка конфига тестового стенда
        """
        stand_config_uuid = self._get_stand_config_uuid()

        test_stands_configs_dir_path = (
            get_web_bb_test_stands_configurations_dir_path(
                configurations_path=self._configurations_path,
            )
        )

        clone_or_pull_repository(
            path=self._configurations_path,
            url=self._configurations_git_repository_url,
        )

        config_paths = test_stands_configs_dir_path.glob('*.conf')

        for config_path in config_paths:
            config = ConfigUpdater()
            config_path_str = str(config_path)
            config.read(config_path_str)

            try:
                config_uuid = config.get(
                    section='runtime',
                    option='app_config_uuid',
                )
            except NoOptionError:
                logger.write(f'{config_path}\n')

                raise NoOptionError(
                    section='runtime',
                    option='app_config_uuid',
                )

            if config_uuid.value == stand_config_uuid:
                self._stand_config = config
                self._stand_config_path = config_path

                break

        if not self._stand_config:
            raise ConfigurationFileNotFoundByUUID()

    def _prepare_stand_database_options(self):
        """
        Подготовка параметров подключения к базе из секции database
        """
        database_engine = self._stand_config.get(
            section='database',
            option='database_engine',
            fallback=None,
        )

        if not database_engine:
            self._stand_config.set(
                section='database',
                option='database_engine',
                value='django.db.backends.postgresql_psycopg2',
            )

        database_user = self._stand_config.get(
            section='database',
            option='database_user',
            fallback=None,
        )

        if not database_user:
            self._stand_config.set(
                section='database',
                option='database_user',
                value='bars_web_bb',
            )

        database_password = self._stand_config.get(
            section='database',
            option='database_password',
            fallback=None,
        )

        if not database_password:
            self._stand_config.set(
                section='database',
                option='database_password',
                value='bars_web_bb',
            )

        database_name = self._stand_config.get(
            section='database',
            option='database_name',
            fallback=None,
        )

        if not database_name:
            self._stand_config.set(
                section='database',
                option='database_name',
                value='bars_web_bb',
            )

        database_host = self._stand_config.get(
            section='database',
            option='database_host',
            fallback='localhost',
        )

        database_host = database_host if isinstance(database_host, str) else database_host.value

        if (
            database_host in ['127.0.0.1', 'localhost'] or
            not ipv4(database_host)
        ):
            self._stand_config.set(
                section='database',
                option='database_host',
                value=self._stand_config_path.name.split('_')[0],
            )

        database_port = self._stand_config.get(
            section='database',
            option='database_port',
            fallback=POSTGRES_DEFAULT_PORT,
        )

        database_port = database_port if isinstance(database_port, str) else database_port.value

        self._stand_config.set(
            section='database',
            option='database_port',
            value=database_port,
        )

    def _prepare_stand_async_database_options(self):
        """
        Подготовка параметров подключения к базе из секции async_database
        """
        if not self._stand_config.has_section(key=WebBBConfigSectionEnum.ASYNC_DATABASE):
            self._stand_config.add_section(WebBBConfigSectionEnum.ASYNC_DATABASE)

        database_engine = self._stand_config.get(
            section='async_database',
            option='database_engine',
            fallback=None,
        )

        if not database_engine:
            self._stand_config.set(
                section='async_database',
                option='database_engine',
                value=self._stand_config.get(
                    section='database',
                    option='database_engine',
                ).value,
            )

        database_user = self._stand_config.get(
            section='async_database',
            option='database_user',
            fallback=None,
        )

        if not database_user:
            self._stand_config.set(
                section='async_database',
                option='database_user',
                value=self._stand_config.get(
                    section='database',
                    option='database_user',
                ).value,
            )

        database_password = self._stand_config.get(
            section='async_database',
            option='database_password',
            fallback=None,
        )

        if not database_password:
            self._stand_config.set(
                section='async_database',
                option='database_password',
                value=self._stand_config.get(
                    section='database',
                    option='database_password',
                ).value,
            )

        database_name = self._stand_config.get(
            section='async_database',
            option='database_name',
            fallback=None,
        )

        if not database_name:
            self._stand_config.set(
                section='async_database',
                option='database_name',
                value=self._stand_config.get(
                    section='database',
                    option='database_name',
                ).value,
            )

        database_host = self._stand_config.get(
            section='async_database',
            option='database_host',
            fallback='localhost',
        )

        database_host = database_host if isinstance(database_host, str) else database_host.value

        if (
            database_host in ['127.0.0.1', 'localhost'] or
            not ipv4(database_host)
        ):
            self._stand_config.set(
                section='async_database',
                option='database_host',
                value=self._stand_config_path.name.split('_')[0],
            )

        database_port = self._stand_config.get(
            section='async_database',
            option='database_port',
            fallback=POSTGRES_DEFAULT_PORT,
        )

        database_port = database_port if isinstance(database_port, str) else database_port.value

        self._stand_config.set(
            section='async_database',
            option='database_port',
            value=database_port,
        )

    def _prepare_stand_config_options(self):
        """
        Подготовка параметров конфига тестового стенда к работе локально
        """
        self._prepare_stand_database_options()
        self._prepare_stand_async_database_options()

    def _prepare_result_config_activated_plugins(self):
        """
        Подготовка активных плагинов согласно подключенным проектам для
        результирующего конфига
        """
        parsed_plugins = set(
            map(
                lambda x: x.strip(),
                self._result_config['plugins']['activated_plugins'].value.split(',')  # noqa
            )
        )

        if self._projects_combination:
            plugins = ProjectPluginEnum.get_enums_by_str_plugins(
                plugins=parsed_plugins,
            )

            activated_plugins = list(map(
                lambda plugin: plugin.value,
                (
                    ProjectPluginEnum.get_filtered_plugins_for_projects_combination(  # noqa
                        projects_combination=self._projects_combination,
                        plugins=plugins,
                    )
                )
            ))
        else:
            activated_plugins = parsed_plugins

        self._result_config.set(
            section='plugins',
            option='activated_plugins',
            value=','.join(activated_plugins),
        )

    def _clear_skipped_options(self):
        """
        Зачистка значений опций, которые должны быть пропущены
        """
        if self._skipped_options:
            section_options_map = (
                map(
                    lambda s_o: s_o.split(SECTION_OPTION_DELIMITER),
                    self._skipped_options
                )
            )

            for section, option in section_options_map:
                if (
                    option == ALL and
                    self._result_config.has_section(section)
                ):
                    for option_ in self._result_config[section]:
                        if self._result_config.has_option(
                            section=section,
                            option=option_,
                        ):
                            self._result_config.set(
                                section=section,
                                option=option_,
                                value='',
                            )
                else:
                    if self._result_config.has_option(
                        section=section,
                        option=option,
                    ):
                        self._result_config.set(
                            section=section,
                            option=option,
                            value='',
                        )

    def generate(self) -> ConfigUpdater:
        """
        Генерация конфига для локального использования на основе конфига
        тестового стенда
        """
        self._get_stand_config()
        self._prepare_stand_config_options()

        sections = WebBBConfigSectionEnum.values.keys()

        for section in sections:
            self._result_config.add_section(
                section=section,
            )

            self._result_config[section].add_after.space(1)

        for (section, option), description in WebBBConfigOptionEnum.values.items():
            self._result_config.set(
                section=section,
                option=option,
                value='',
            )

            description = WebBBConfigOptionEnum.values.get((section, option))
            if description:
                self._result_config[section][option].add_before.comment(
                    text=f'# {description}',
                )

        fill_config_from_source(
            src_config=self._stand_config,
            dst_config=self._result_config,
        )

        self._clear_skipped_options()

        if self._settings_config:
            fill_config_from_source(
                src_config=self._settings_config,
                dst_config=self._result_config,
            )

        self._prepare_result_config_activated_plugins()

        return self._result_config

    def export(
        self,
        result_configuration_path: Path,
    ):
        """
        Экспорт результирующего конфига в файл
        """
        with open(str(result_configuration_path), 'w') as configuration_file:
            self._result_config.write(
                fp=configuration_file,
            )

        result_configuration_path.chmod(
            mode=0o700,
        )


class BOBARSDockConfigGenerator(BOConfigGenerator):
    """
    Генератор конфигурационного файла для окружения основанного на bobarsdock
    """

    def __init__(
        self,
        *args,
        with_databaser_slice: bool = False,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

        self._with_databaser_slice = with_databaser_slice

    def _prepare_stand_database_options(self):
        """
        Подготовка параметров подключения к базе из секции database
        """
        if self._with_databaser_slice:
            self._stand_config.set(
                section='database',
                option='database_engine',
                value='web_bb.db_wrapper.postgresql_psycopg2_with_hooks',
            )

            self._stand_config.set(
                section='database',
                option='database_user',
                value='bars_web_bb',
            )

            self._stand_config.set(
                section='database',
                option='database_password',
                value='bars_web_bb',
            )

            self._stand_config.set(
                section='database',
                option='database_name',
                value='bars_web_bb',
            )

            self._stand_config.set(
                section='database',
                option='database_host',
                value='database',
            )

            self._stand_config.set(
                section='database',
                option='database_port',
                value=POSTGRES_DEFAULT_PORT,
            )
        else:
            super()._prepare_stand_database_options()

    def _prepare_stand_async_database_options(self):
        """
        Подготовка параметров подключения к базе из секции database
        """
        if self._with_databaser_slice:
            self._stand_config.set(
                section='async_database',
                option='database_engine',
                value='web_bb.db_wrapper.postgresql_psycopg2_with_hooks',
            )

            self._stand_config.set(
                section='async_database',
                option='database_user',
                value='bars_web_bb',
            )

            self._stand_config.set(
                section='async_database',
                option='database_password',
                value='bars_web_bb',
            )

            self._stand_config.set(
                section='async_database',
                option='database_name',
                value='bars_web_bb',
            )

            self._stand_config.set(
                section='async_database',
                option='database_host',
                value='database',
            )

            self._stand_config.set(
                section='async_database',
                option='database_port',
                value=POSTGRES_DEFAULT_PORT,
            )
        else:
            super()._prepare_stand_async_database_options()

    def generate(self) -> ConfigUpdater:
        """
        Генерация конфига для локального использования на основе конфига
        тестового стенда
        """
        self._get_stand_config()
        self._prepare_stand_config_options()

        sections = {
            section_option[0]
            for section_option in WebBBConfigOptionEnum.BARSDOCK_OPTIONS
        }

        for section in sorted(sections):
            self._result_config.add_section(
                section=section,
            )

            self._result_config[section].add_after.space(1)

            section_description = WebBBConfigSectionEnum.values.get(section)
            if section_description:
                self._result_config[section].add_before.comment(
                    text=f'# {section_description}',
                )

        section_options = WebBBConfigOptionEnum.BARSDOCK_OPTIONS

        for section, option in section_options:
            self._result_config.set(
                section=section,
                option=option,
                value='',
            )

            option_description = WebBBConfigOptionEnum.values.get((section, option))
            if option_description:
                self._result_config[section][option].add_before.comment(
                    text=f'# {option_description}',
                )

        fill_config_from_source(
            src_config=self._stand_config,
            dst_config=self._result_config,
        )

        self._clear_skipped_options()

        if self._settings_config:
            fill_config_from_source(
                src_config=self._settings_config,
                dst_config=self._result_config,
            )

        self._result_config.set(
            section=WebBBConfigOptionEnum.RUNTIME___DEBUG[0],
            option=WebBBConfigOptionEnum.RUNTIME___DEBUG[1],
            value='True',
        )

        self._prepare_result_config_activated_plugins()

        return self._result_config
