import validators
from jenkins import (
    Jenkins,
)

from botoolkit.bo_jenkins.enums import (
    StandStateEnum,
)
from botoolkit.bo_jenkins.parsers import (
    JenkinsJobParser,
)
from botoolkit.bo_jenkins.settings import (
    TOOL_NAME as BOJENKINS_TOOL_NAME,
)
from botoolkit.bo_jenkins.strings import (
    STAND_URL_IS_NOT_URL_ERROR,
    STAND_WITH_SAME_URL_UNAVAILABLE_OR_NOT_FOUND,
)
from botoolkit.core.strings import (
    WRONG_ARGUMENT_VALUE,
)


class JenkinsArgumentsMixin:
    """
    Добавляет параметры
        --jenkins_url
        --jenkins_username
        --jenkins_password
    """

    def patch_arguments_schema(self):
        super().patch_arguments_schema()

        self._arguments_schema.extend(
            (
                {
                    'section': 'jenkins',
                    'option': 'url',
                    'help': 'URL сервиса Jenkins.',
                },
                {
                    'section': 'jenkins',
                    'option': 'username',
                    'help': 'Имя пользователя в Jenkins.',
                },
                {
                    'section': 'jenkins',
                    'option': 'password',
                    'help': 'Пароль пользователя в Jenkins.',
                },
            )
        )

    def _validate_jenkins_url(self):
        """
        Валидация параметра jenkins_url
        """
        if (
            self._parsed_args.jenkins_url and
            not validators.url(self._parsed_args.jenkins_url)
        ):
            raise RuntimeError(
                WRONG_ARGUMENT_VALUE.format(
                    argument_name='jenkins_url',
                )
            )


class JenkinsDatabaserArgumentsMixin(JenkinsArgumentsMixin):
    """
    Добавляет параметры
        --jenkins_url
        --jenkins_username
        --jenkins_password
        --jenkins_databaser_job_name
        --jenkins_databaser_excluded_tables
        --jenkins_databaser_new_jira_filter
        --jenkins_databaser_running_jira_filter
        --jenkins_databaser_errors_jira_filter
        --jenkins_databaser_build_url_template
        --jenkins_databaser_notification_telegram_chat_id
    """

    def patch_arguments_schema(self):
        super().patch_arguments_schema()

        self._arguments_schema.extend(
            (
                {
                    'section': 'jenkins',
                    'option': 'databaser_job_name',
                    'help': 'Имя Job-а для запуска сборки среза БД при помощи Databaser в Jenkins.',
                },
                {
                    'section': 'jenkins',
                    'option': 'databaser_expired',
                    'help': 'Время работы сборки среза, после которой считается, что она зависла (в секундах).',
                },
                {
                    'section': 'jenkins',
                    'option': 'databaser_excluded_tables',
                    'help': 'Исключаемые из сборки среза БД  таблицы.',
                },
                {
                    'section': 'jenkins',
                    'option': 'databaser_new_jira_filter',
                    'help': 'Фильтр задач Jira для автоматического запуска срезов БД.',
                },
                {
                    'section': 'jenkins',
                    'option': 'databaser_running_jira_filter',
                    'help': 'Фильтр задач Jira с уже запущенными сборками срезов БД.',
                },
                {
                    'section': 'jenkins',
                    'option': 'databaser_errors_jira_filter',
                    'help': 'Фильтр задач Jira с ошибками при сборок срезов БД.',
                },
                {
                    'section': 'jenkins',
                    'option': 'databaser_build_url_template',
                    'help': (
                        'Шаблон для формирования адреса запущенной сборки среза БД в Jenkins. Например, '
                        '{jenkins_url}view/БЦ БО Разное/job/{jenkins_databaser_job_name}/{build_number}/'
                    ),
                },
                {
                    'section': 'jenkins',
                    'option': 'databaser_notification_telegram_chat_id',
                    'help': 'Telegram Chat ID для отсылки оповещений.',
                },
            )
        )


class JenkinsStandURLArgumentMixin:
    """
    Добавляет параметр --stand_url в команду
    """

    def get_required_config_tool_names(self):
        required_config_tool_names = super().get_required_config_tool_names()

        required_config_tool_names.append(BOJENKINS_TOOL_NAME)

        return required_config_tool_names

    def get_parser(
        self,
        prog_name,
    ):
        parser = super().get_parser(
            prog_name=prog_name,
        )

        parser.add_argument(
            '--stand_url',
            dest='stand_url',
            action='store',
            type=str,
            help='URL тестового стенда.'
        )

        return parser

    def _validate_stand_url(self):
        """
        Валидация параметра stand_url
        """
        if self._parsed_args.stand_url:
            if not validators.url(self._parsed_args.stand_url):
                raise RuntimeError(STAND_URL_IS_NOT_URL_ERROR)

            jenkins_url = self._bojenkins_config.get(
                section='jenkins',
                option='url',
            ).value

            jenkins_username = self._bojenkins_config.get(
                section='jenkins',
                option='username',
            ).value

            jenkins_password = self._bojenkins_config.get(
                section='jenkins',
                option='password',
            ).value

            jenkins_server = Jenkins(
                url=jenkins_url,
                username=jenkins_username,
                password=jenkins_password,
            )

            jenkins_job_parser = JenkinsJobParser(
                jenkins_server=jenkins_server,
            )

            jenkins_job_parser.parse()

            unavailable_stand_urls = jenkins_job_parser.get_stand_urls(
                state=StandStateEnum.UNAVAILABLE,
            )

            if self._parsed_args.stand_url in unavailable_stand_urls:
                raise RuntimeError(STAND_WITH_SAME_URL_UNAVAILABLE_OR_NOT_FOUND)

    def _validate_arguments(self):
        super()._validate_arguments()

        self._validate_stand_url()
