from argparse import (
    Namespace,
)
from distutils.util import (
    strtobool,
)

from botoolkit.bo_jenkins.mixins import (
    JenkinsDatabaserArgumentsMixin,
)
from botoolkit.bo_jenkins.settings import (
    TOOL_NAME as BOJENKINS_TOOL_NAME,
)
from botoolkit.bo_jira.api import (
    JiraAPIClient,
)
from botoolkit.bo_jira.helpers import (
    prepare_jira_issue_url,
)
from botoolkit.bo_jira.mixins import (
    JiraArgumentsMixin,
)
from botoolkit.bo_jira.settings import (
    TOOL_NAME as BOJIRA_TOOL_NAME,
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
from botoolkit.core.commands import (
    BOConfiguredToolConfigureCommand,
    BOConfiguredToolLister,
)
from botoolkit.core.consts import (
    ALLOWED_ALL_EMPTY_CONFIG_PARAMETERS,
)


class ConfigureBOJiraCommand(
    JiraArgumentsMixin,
    BOConfiguredToolConfigureCommand,
):
    """
    Конфигурирование инструмента bojira
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
            'Configure bojira for working with Jira instance.'
        )

    def get_tool_name(self):
        return BOJIRA_TOOL_NAME

    def get_allowed_empty_config_parameters(self):
        return ALLOWED_ALL_EMPTY_CONFIG_PARAMETERS

    def get_required_config_tool_names(self):
        required_config_tool_names = super().get_required_config_tool_names()

        required_config_tool_names.append(BOTOOLKIT_TOOL_NAME)

        return required_config_tool_names


class BOJenkinsDatabaserBuildErrorsJiraIssuesLister(
    JiraArgumentsMixin,
    JenkinsDatabaserArgumentsMixin,
    BOConfiguredToolLister,
):
    """
    Команда получения списка задач с ошибками при сборке срезов БД
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
            'Команда получения списка задач с ошибками при сборке срезов БД.'
        )

    def get_required_config_tool_names(self):
        required_config_tool_names = super().get_required_config_tool_names()

        required_config_tool_names.extend([
            BOJIRA_TOOL_NAME,
            BOJENKINS_TOOL_NAME,
            BOTELEGRAM_TOOL_NAME,
            BOTOOLKIT_TOOL_NAME,
        ])

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
            help='Оповестить разработчиков о наличии задач с ошибочными сборками срезов БД.',
        )

        return parser

    def _prepare_jira_client(self):
        """
        Подготовка клиента Jira
        """
        self._jira_client = JiraAPIClient(
            url=self._bojira_config['jira']['url'].value,
            username=self._bojira_config['jira']['username'].value,
            password=self._bojira_config['jira']['password'].value,
        )

    def _parse_jira_issues_by_filter(
        self,
        jql_str: str,
    ):
        """
        Получение идентификатора задачи Jira из фильтра
        """
        issues = self._jira_client.search_issues(
            jql_str=jql_str,
        )

        return issues

    def take_action(
        self,
        parsed_args: Namespace,
    ):
        super().take_action(
            parsed_args=parsed_args,
        )

        self._prepare_jira_client()

        issues = self._parse_jira_issues_by_filter(
            jql_str=self._bojenkins_config['jenkins']['databaser_errors_jira_filter'].value,
        )

        issues_urls = []

        for issue in issues:
            issues_urls.append(
                prepare_jira_issue_url(
                jira_url=self._bojira_config['jira']['url'].value,
                issue_id=issue.key,
            )
        )

        if parsed_args.notify and issues_urls:
            telegram_sender = TelegramMessageSender(
                bot_api_token=self._botelegram_config['telegram']['bot_api_token'].value,
                chat_ids=(
                    self._bojenkins_config['jenkins']['databaser_notification_telegram_chat_id'].value,
                ),
            )

            issues_urls_str = '\n'.join(sorted(issues_urls))

            message = (
                f'\U00002757\U00002757\U00002757 \nДля ряда задач не удалось создать срезы баз данных:\n'
                f'{issues_urls_str}'
            )

            telegram_sender.send(
                message=message,
            )

        columns = (
            'Issue',
        )

        rows = (
            (
                issue_url,
            )
            for issue_url in issues_urls
        )

        return columns, rows
