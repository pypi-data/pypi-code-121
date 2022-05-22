from botoolkit.bo_conf.enums import (
    WebBBConfigOptionEnum,
)
from botoolkit.bo_conf.helpers import (
    get_configurations_path,
)
from botoolkit.bo_git.helpers import (
    ls_remote,
)
from botoolkit.core.strings import (
    WRONG_ARGUMENT_VALUE,
)
from botoolkit.settings import (
    CONFIGURATION_DIRECTORY_PATH,
)


class ConfiguratorArgumentsMixin:
    """
    Добавляет параметры
        --boconf_configurations_path
        --boconf_configurations_git_repository_url
        --boconf_generating_configuration_dir_path
    """

    def patch_arguments_schema(self):
        super().patch_arguments_schema()

        self._arguments_schema.extend(
            (
                {
                    'section': 'boconf',
                    'option': 'configurations_path',
                    'help': (
                        'Абсолютный путь к директории, в которую будет (уже) осуществлено клонирование репозитория с '
                        'конфигурационными файлами тестовых стендов.'
                    ),
                },
                {
                    'section': 'boconf',
                    'option': 'configurations_git_repository_url',
                    'help': 'URL репозитория с конфигурационными файлами тестовых стендов.',
                },
                {
                    'section': 'boconf',
                    'option': 'notification_telegram_chat_id',
                    'help': 'Telegram Chat ID для отсылки оповещений',
                },
                {
                    'section': 'boconf_generator',
                    'option': 'generating_configuration_dir_path',
                    'help': (
                        'Абсолютный путь до директории, в которую будет осуществляться сохранение генерируемого '
                        'конфигурационного файла.'
                    ),
                },
            )
        )

    def _validate_configurations_git_repository_url(self):
        """
        Валидация значения параметра
        configurator_configurations_git_repository_url
        """
        if self._parsed_args.configurator_configurations_git_repository_url:
            references = ls_remote(
                url=self._parsed_args.configurator_configurations_git_repository_url,  # noqa
            )

            if not references['HEAD']:
                raise RuntimeError(
                    WRONG_ARGUMENT_VALUE.format(
                        argument_name='configurator_configurations_git_repository_url',  # noqa
                    )
                )

    def _fill_boconf_configurations_path(
        self,
        value: str,
    ):
        """
        Заполнение значения параметра configurations_path секции boconf
        """
        if not value:
            value = str(get_configurations_path())

        self._config.set(
            section='boconf',
            option='configurations_path',
            value=value,
        )

    def _fill_boconf_generator_generating_configuration_dir_path(
        self,
        value: str,
    ):
        """
        Заполнение значения параметра generating_configuration_dir_path секции
        boconf_generator
        """
        if not value:
            value = str(CONFIGURATION_DIRECTORY_PATH)

        self._config.set(
            section='boconf_generator',
            option='generating_configuration_dir_path',
            value=value,
        )


class WebBBConfigArgumentsMixin:
    """
    Добавляет параметры из конфигурационного файла как параметры
    """

    def patch_arguments_schema(self):
        super().patch_arguments_schema()

        for (section, option), description in WebBBConfigOptionEnum.values.items():  # noqa
            self._arguments_schema.append(
                {
                    'section': section,
                    'option': option,
                    'help': description,
                }
            )


class SkippedOptionsConfigArgumentMixin:
    """
    Добавляет параметр, указывающий параметры, которые не должны заполняться из
    конфигурационного файла тестового стенда
    """

    def patch_arguments_schema(self):
        super().patch_arguments_schema()

        self._arguments_schema.append(
            {
                'section': 'boconf_generator',
                'option': 'skipped_options',
                'help': 'Пропускаемые опции конфигурационного файла.',
            }
        )


class WebBBActivatedPluginsConfigArgumentsMixin:
    """
    Добавляет параметр конфига ACTIVATED_PLUGINS в качестве параметра команды
    """

    def patch_arguments_schema(self):
        super().patch_arguments_schema()

        self._arguments_schema.append(
            {
                'section': 'plugins',
                'option': 'activated_plugins',
                'help': 'Значение параметра ACTIVATED_PLUGINS конфигурационного файла.',
            }
        )


class WebBBAppRegionAbbreviationConfigArgumentsMixin:
    """
    Добавляет параметр конфига APP_REGION_ABBREVIATION в качестве параметра
    команды
    """

    def patch_arguments_schema(self):
        super().patch_arguments_schema()

        self._arguments_schema.append(
            {
                'section': 'runtime',
                'option': 'APP_REGION_ABBREVIATION',
                'help': 'Значение параметра APP_REGION_ABBREVIATION конфигурационного файла.',
            }
        )
