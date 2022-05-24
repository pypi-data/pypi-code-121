from argparse import (
    Namespace,
)
from configparser import (
    NoOptionError,
)
from typing import (
    Dict,
    List,
    Optional,
)

from cliff.command import (
    Command,
)
from cliff.lister import (
    Lister,
)
from configupdater import (
    ConfigUpdater,
)
from prettytable import (
    PrettyTable,
)

from botoolkit import (
    settings,
)
from botoolkit.core.consts import (
    ALLOWED_ALL_EMPTY_CONFIG_PARAMETERS,
)
from botoolkit.core.helpers import (
    get_tool_conf_file_path,
    raise_exception,
)
from botoolkit.core.loggers import (
    logger,
)
from botoolkit.core.mixins import (
    ClearArgumentMixin,
)
from botoolkit.core.strings import (
    CONFIGURATION_DIRECTORY_DOES_NOT_EXIST,
    CONFIGURATION_FILE_DOES_NOT_EXIST,
    EMPTY_REQUIRED_TOOL_CONF_PARAMETER_VALUES_ERROR,
    EMPTY_TOOL_CONF_FILE_PARAMETER_VALUES_ERROR,
    PROPERTY_NOT_FOUND_IN_REQUIRED_CONFIGS,
)
from botoolkit.settings import (
    CONFIGURATION_DIRECTORY_PATH,
)


class BaseBOCommand(Command):
    """
    Базовый класс для создания команд
    """

    def __init__(
        self,
        *args,
        **kwargs,
    ):
        self._arguments_schema: List[Dict[str, str]] = []

        self.description = ''

        self.patch_arguments_schema()

        self._allowed_empty_config_parameters = (
            self.get_allowed_empty_config_parameters()
        )

        self._parsed_args: Optional[Namespace] = None

        super().__init__(
            *args,
            **kwargs,
        )

    def patch_arguments_schema(self) -> List[Dict[str, str]]:
        """
        Патчинг схемы параметров команды.

        Схема параметров команды, совпадающая с параметрами конфигурационного
        файла
        (
          {
              'section': '',
              'option': '',
              'action': 'store',
              'type': str,
              'default': '',
              'help': '',
          },
          ...
        )
        """

    def get_description(self):
        return self.description

    def get_allowed_empty_config_parameters(self) -> Dict[str, List[str]]:
        """
        Указывает, какие параметры могут иметь пустые значения
        {
          section: [
              option,
              ...
          ],
          ...
        }
        Если не нужно проверять никакие параметры, необходимо указать
        _allowed_empty_config_parameters = ALLOWED_ALL_EMPTY_CONFIG_PARAMETERS
        """
        return {}

    def _validate_arguments(self):
        """
        Валидация переданных значений параметров. У экземпляра ищутся методы
        по шаблону _validate_{argument_name}
        """
        for argument_data in self._arguments_schema:
            argument_name = (
                f'{argument_data["section"]}_{argument_data["option"]}'
            )

            argument_validation_function = getattr(
                self,
                f'_validate_{argument_name}',
                None,
            )

            if argument_validation_function:
                argument_validation_function()

    def _validate(self):
        """
        Валидация перед выполнением команды
        """
        self._validate_arguments()

    def get_parser(self, prog_name):
        """
        Производится добавление декларативно описанных параметров из свойства
        _arguments_schema
        """
        parser = super().get_parser(
            prog_name=prog_name,
        )

        for argument_data in self._arguments_schema:
            argument_name = (
                f'{argument_data["section"]}_{argument_data["option"]}'
            )

            parser.add_argument(
                f'--{argument_name}',
                dest=f'{argument_name}',
                action=argument_data.get('action', 'store'),
                type=argument_data.get('type', str),
                default=argument_data.get('default', ''),
                help=argument_data.get('help', ''),
            )

        return parser

    def get_epilog(self):
        """
        Переопределенный метод, возвращаемый эпилог команды
        """
        # replace a None in self._epilog with an empty string
        parts = [self._epilog or '']
        hook_epilogs = filter(
            None,
            (h.obj.get_epilog() for h in self._hooks),
        )
        parts.extend(hook_epilogs)

        return '\n\n'.join(parts)

    def take_action(
        self,
        parsed_args: Namespace,
    ):
        self._parsed_args = parsed_args

        self._validate()


class BaseBOConfigureCommand(
    ClearArgumentMixin,
    BaseBOCommand,
):
    """
    Базовый класс для создания команд конфигурирования инструментов
    """

    def __init__(
        self,
        *args,
        **kwargs,
    ):
        self.tool_name = self.get_tool_name()

        self._config: Optional[ConfigUpdater] = None

        self._old_config = None

        tool_conf_file_path = get_tool_conf_file_path(
            tool_name=self.tool_name,
        )

        if tool_conf_file_path.exists():
            self._old_config = ConfigUpdater()
            self._old_config.read(str(tool_conf_file_path))

        # Указывает на возможность ускоренного конфигурирования при выполнении
        # команды botoolkit configure --all
        self._is_force_configure = True

        super().__init__(
            *args,
            **kwargs,
        )

    @property
    def is_force_configure(self):
        return self._is_force_configure

    def get_tool_name(self) -> str:
        """
        Конфигурируемый инструмент
        """
        return ''

    def _create_config(self):
        """
        Создание конфига инструмента на основе шаблона и перезаписью значений
        из уже созданного конфигурационного файла
        """
        template_tool_conf_file_path = getattr(
            settings,
            f'{self.tool_name.upper()}_TEMPLATE_CONF_FILE_PATH',
        )

        self._config = ConfigUpdater()
        self._config.read(str(template_tool_conf_file_path))

    def _fill_argument_default_values_from_config(self):
        """
        Заполнение дефолтных значений параметров команды. Сразу установить
        дефолтные значения нет возможности, т.к. необходимо руководствоваться
        наличием существующего конфига и ключом clear.

        Заполнение дефолтных значений производится по следующему принципу:
        1) Значения параметров переданные при запуске команды имеют наивысший
            приоритет;
        2) Если ранее уже производилось конфигурирование инструмента и не
            указан ключ --clear, то значения из существующего конфига берутся
            в качестве значений по умолчанию, после пользовательских.
        """
        for argument_data in self._arguments_schema:
            argument_name = (
                f'{argument_data["section"]}_{argument_data["option"]}'
            )

            user_argument_value = getattr(
                self._parsed_args,
                argument_name,
                None,
            )

            if (
                not user_argument_value and
                self._old_config and
                not self._parsed_args.clear
            ):
                try:
                    config_argument_value = self._old_config.get(
                        section=argument_data['section'],
                        option=argument_data['option'],
                    ).value
                except NoOptionError:
                    # Если был добавлен новый параметр, то нужно будет установить значение по умолчанию
                    config_argument_value = ''

                setattr(
                    self._parsed_args,
                    argument_name,
                    config_argument_value
                )

    def _fill_config_from_arguments(self):
        """
        Заполнение конфига значениями параметров
        """
        for argument_data in self._arguments_schema:
            argument_name = (
                f'{argument_data["section"]}_{argument_data["option"]}'
            )

            argument_value = getattr(
                self._parsed_args,
                argument_name,
            )

            argument_filling_function = getattr(
                self,
                f'_fill_{argument_name}',
                None,
            )

            if argument_filling_function:
                argument_filling_function(
                    value=argument_value,
                )
            elif argument_value:
                self._config.set(
                    section=argument_data['section'],
                    option=argument_data['option'],
                    value=str(argument_value),
                )

    def _check_config_fullness(self):
        """
        Проверка заполнения параметров конфигурационного файла с учетом
        значений в _allowed_empty_config_parameters
        """
        if self._allowed_empty_config_parameters != ALLOWED_ALL_EMPTY_CONFIG_PARAMETERS:  # noqa
            errors = []
            for section in self._config.sections():
                for option in self._config[section]:
                    if (
                        section in self._allowed_empty_config_parameters and
                        option in self._allowed_empty_config_parameters[section]
                    ):
                        continue

                    value = self._config.get(
                        section=section,
                        option=option,
                    ).value

                    if not value:
                        errors.append(
                            (
                                section,
                                option,
                            )
                        )

            if errors:
                wrong_parameters_table = PrettyTable()

                wrong_parameters_table.field_names = [
                    'Section',
                    'Option',
                ]

                for wrong_parameter in errors:
                    wrong_parameters_table.add_row(wrong_parameter)

                raise RuntimeError(
                    EMPTY_TOOL_CONF_FILE_PARAMETER_VALUES_ERROR.format(
                        tool_name=self.tool_name,
                        wrong_parameters_table=wrong_parameters_table,
                    )
                )

    def _write_config(self):
        """
        Запись конфига в файл
        """
        tool_conf_file_path = get_tool_conf_file_path(
            tool_name=self.tool_name,
        )

        with open(str(tool_conf_file_path), 'w') as configuration_file:  # noqa
            self._config.write(
                fp=configuration_file,
            )

        tool_conf_file_path.chmod(
            mode=0o700,
        )

        logger.write(
            f'Configuration file created successfully. Configuration file '
            f'path - {tool_conf_file_path}\n'
        )

    def take_action(
        self,
        parsed_args: Namespace,
    ):
        self._parsed_args = parsed_args

        self._fill_argument_default_values_from_config()
        self._validate()
        self._create_config()
        self._fill_config_from_arguments()
        self._check_config_fullness()
        self._write_config()


class BOConfigureCommand(
    BaseBOConfigureCommand,
):
    """
    Класс для создания команд конфигурирования
    """


class BOCommand(
    BaseBOCommand,
):
    """
    Базовый клас для создания команд
    """
    pass


class BaseBOConfiguredToolCommand(BaseBOCommand):
    """
    Базовый класс для создания команд, требующих предварительное
    конфигурирование указанных инструментов. Если все указанные инструменты
    сконфигурированы, то конфиги можно найти в атрибутах экземпляра по шаблону
    _<tool_name>_config
    """

    def __init__(
        self,
        *args,
        **kwargs,
    ):
        self.required_config_tool_names = self.get_required_config_tool_names()
        self.required_config_options = self.get_required_config_options()

        self._parse_and_set_required_configs()

        super().__init__(
            *args,
            **kwargs,
        )

    def get_required_config_tool_names(self) -> List[str]:
        """
        Имена инструментов, от которых зависит выполнение команды. Инструменты
        должны быть предварительно сконфигурированы
        """
        return []

    def get_required_config_options(self) -> Dict[str, List[str]]:
        """
        Обязательные для заполнения параметры. Поиск производится по всем
        конфигурационным файлам инструментов, указанных в
        required_config_tool_names
        {
          'section': [
              'option',
              'option',
              ...
          ],
          ...
        }
        """
        return {}

    def _get_property_value_from_required_configs(
        self,
        section: str,
        option: str,
    ):
        """
        Поиск значения параметра конфига в обязательных конфигах
        """
        option_value = None

        for tool_name in self.required_config_tool_names:
            config: ConfigUpdater = getattr(
                self,
                f'_{tool_name}_config',
            )

            if config.has_section(section):
                option_item = config.get(
                    section=section,
                    option=option,
                    fallback=None,
                )

                if not option_value and option_item is not None:
                    option_value = option_item.value

        if (
            option_value is None and not (
                section in self._allowed_empty_config_parameters and
                option in self._allowed_empty_config_parameters[section]
            )
        ):
            raise RuntimeError(
                PROPERTY_NOT_FOUND_IN_REQUIRED_CONFIGS.format(
                    section=section,
                    option=option,
                    required_config_tool_names=(
                        ', '.join(self.required_config_tool_names)
                    )
                )
            )

        return option_value

    def _parse_and_set_required_configs(self):
        """
        Парсинг и установка обязательного конфига в экземпляр
        """
        for tool_name in self.required_config_tool_names:
            conf_file_path = get_tool_conf_file_path(
                tool_name=tool_name,
            )

            config = ConfigUpdater()

            try:
                config.read(str(conf_file_path))
            except FileNotFoundError:
                pass

            setattr(self, f'_{tool_name}_config', config)

    def _check_config_exists(
        self,
        tool_name: str,
        is_silent: bool = False,
    ):
        """
        Проверка существования конфига
        """
        conf_file_path = get_tool_conf_file_path(
            tool_name=tool_name,
        )

        result = True

        if not CONFIGURATION_DIRECTORY_PATH.exists():
            raise_exception(
                exception_class=RuntimeError,
                message=(
                    CONFIGURATION_DIRECTORY_DOES_NOT_EXIST.format(
                        tool_name=tool_name.replace('_', ' '),
                    )
                ),
                is_silent=is_silent,
            )

            result = False

        if not conf_file_path.exists():
            raise_exception(
                exception_class=RuntimeError,
                message=(
                    CONFIGURATION_FILE_DOES_NOT_EXIST.format(
                        tool_name=tool_name.replace('_', ' '),
                    )
                ),
                is_silent=is_silent,
            )

            result = False

        return result

    def _validate_configurations(self):
        """
        Валидация обязательных конфигов
        """
        for tool_name in self.required_config_tool_names:
            self._check_config_exists(
                tool_name=tool_name,
            )

    def _check_required_config_options(self):
        """
        Проверка обязательных к заполнению параметров конфигов. Параметры
        должны быть найдены в одном конфигурационных файлов инструментов,
        указанных в зависимостях
        """
        configs = []

        for attr in dir(self):
            if attr.endswith('_config'):
                configs.append(
                    getattr(
                        self,
                        attr,
                    )
                )

        errors = []

        for section in self.required_config_options.keys():
            for option in self.required_config_options[section]:
                value = None
                for config in configs:
                    if config.has_section(section):
                        value = config.get(
                            section=section,
                            option=option,
                            fallback=None,
                        )

                        if value:
                            break

                if not value:
                    errors.append(
                        (
                            section,
                            option,
                        )
                    )

        if errors:
            wrong_parameters_table = PrettyTable()

            wrong_parameters_table.field_names = [
                'Section',
                'Option',
            ]

            for wrong_parameter in errors:
                wrong_parameters_table.add_row(wrong_parameter)

            raise RuntimeError(
                EMPTY_REQUIRED_TOOL_CONF_PARAMETER_VALUES_ERROR.format(
                    wrong_parameters_table=wrong_parameters_table,
                )
            )

    def _validate(self):
        self._validate_configurations()
        self._check_required_config_options()

        super()._validate()

    def _fill_argument_default_values_from_required_configs(
        self,
        parser: ConfigUpdater,
    ):
        """
        Производится установка дефолтных значений параметров, декларативно
        описанных в свойстве _arguments_schema
        """
        defaults = {}

        for argument_data in self._arguments_schema:
            default_value = argument_data.get('default', None)

            if not default_value:
                argument_name = (
                    f'{argument_data["section"]}_{argument_data["option"]}'
                )

                defaults[argument_name] = (
                    self._get_property_value_from_required_configs(
                        section=argument_data['section'],
                        option=argument_data['option'],
                    )
                )

        parser.set_defaults(**defaults)

    def get_description(self):
        required_tool_names = ', '.join(
            map(
                lambda tn: tn.replace('_', ' '),
                self.required_config_tool_names,
            )
        )

        description = (
            f"""{self.description}
            
            Перед запуском этой команды, необходимо произвести конфигурирование следующих инструментов:
            {required_tool_names}.            
            """
        )

        return description

    def get_parser(self, prog_name):
        parser = super().get_parser(
            prog_name=prog_name,
        )

        self._fill_argument_default_values_from_required_configs(
            parser=parser,
        )

        return parser


class BOConfiguredToolCommand(
    BaseBOConfiguredToolCommand,
):
    """
    Базовый класс для создания команд, требующих предварительного
    конфигурирования обязательных инструментов, которые используются в
    функционале команды
    """


class BOConfiguredToolLister(
    BaseBOConfiguredToolCommand,
    Lister,
):
    """
    Базовый класс для создания команд, выводящих результат в виде списка,
    требующих предварительного конфигурирования обязательных инструментов,
    которые используются в функционале команды
    """


class BOConfiguredToolConfigureCommand(
    BaseBOConfigureCommand,
    BaseBOConfiguredToolCommand,
):
    """
    Базовый класс для создания команд конфигурирования с набором инструментов,
    требующих предварительного конфигурирования, которые используются в
    функционале команды
    """

    def _fill_argument_default_values_from_required_configs(
        self,
        parser: ConfigUpdater,
    ):
        """
        Игнорируем заполнение дефолтных значений при формировании парсера, оно
        будет производиться в методе _fill_argument_default_values_from_config
        """
        pass

    def _fill_argument_default_values_from_config(self):
        """
        Заполнение дефолтных значений параметров команды. Сразу установить
        дефолтные значения нет возможности, т.к. необходимо руководствоваться
        наличием существующего конфига и ключом clear.

        Заполнение дефолтных значений производится по следующему принципу:
        1) Значения параметров переданные при запуске команды имеют наивысший
            приоритет;
        2) Если ранее уже производилось конфигурирование инструмента и не
            указан ключ --clear, то значения из существующего конфига берутся
            в качестве значений по умолчанию, после пользовательских;
        3) Если указан ключ --clear, то необходимо производить поиск в
            конфигурациях инструментов, от которых зависит конфигурируемый
            инструмент
        """
        for argument_data in self._arguments_schema:
            argument_name = (
                f'{argument_data["section"]}_{argument_data["option"]}'
            )

            user_argument_value = getattr(
                self._parsed_args,
                argument_name,
                None,
            )

            if not user_argument_value:
                if self._parsed_args.clear or not self._old_config:
                    required_config_argument_value = (
                        self._get_property_value_from_required_configs(
                            section=argument_data['section'],
                            option=argument_data['option'],
                        )
                    )

                    setattr(
                        self._parsed_args,
                        argument_name,
                        required_config_argument_value
                    )
                elif self._old_config:
                    config_argument_value = self._old_config.get(
                        section=argument_data['section'],
                        option=argument_data['option'],
                    ).value

                    if not config_argument_value:
                        config_argument_value = (
                            self._get_property_value_from_required_configs(
                                section=argument_data['section'],
                                option=argument_data['option'],
                            )
                        )

                    setattr(
                        self._parsed_args,
                        argument_name,
                        config_argument_value
                    )
