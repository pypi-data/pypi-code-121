from argparse import (
    Namespace,
)

from jira import (
    JIRAError,
)

from botoolkit.bo_databaser.consts import (
    DATABASER_DB_PREFIX,
)
from botoolkit.bo_jira.api import (
    JiraAPIClient,
)
from botoolkit.bo_jira.consts import (
    JIRA_CLOSED_TASK_STATUS_NAME,
)
from botoolkit.bo_jira.mixins import (
    JiraArgumentsMixin,
)
from botoolkit.bo_jira.settings import (
    TOOL_NAME as BOJIRA_TOOL_NAME,
)
from botoolkit.bo_registry.helpers import (
    RegistryAPIClient,
    RegistryAuxiliaryTool,
)
from botoolkit.bo_registry.mixins import (
    RegistryArgumentsMixin,
    RegistryClientArgumentMixin,
)
from botoolkit.bo_registry.settings import (
    TOOL_NAME as BOREGISTRY_TOOL_NAME,
)
from botoolkit.bo_toolkit.settings import (
    TOOL_NAME as BOTOOLKIT_TOOL_NAME,
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


class ConfigureBORegistryCommand(
    RegistryArgumentsMixin,
    BOConfiguredToolConfigureCommand,
):
    """
    Команда для конфигурирования инструмента boregistry
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
            'Configure boregistry for working with Registry instance.'
        )

    def get_tool_name(self):
        return BOREGISTRY_TOOL_NAME

    def get_allowed_empty_config_parameters(self):
        return ALLOWED_ALL_EMPTY_CONFIG_PARAMETERS

    def get_required_config_tool_names(self):
        required_config_tool_names = super().get_required_config_tool_names()

        required_config_tool_names.append(BOTOOLKIT_TOOL_NAME)

        return required_config_tool_names


class RemoveImagesBORegistryCommand(
    RegistryClientArgumentMixin,
    JiraArgumentsMixin,
    RegistryArgumentsMixin,
    BOConfiguredToolCommand,
):
    """
    Команда для удаления образов баз данных закрытых задач
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
            'Removing images from Registry for closed tasks.'
        )

    def get_required_config_tool_names(self):
        required_config_tool_names = super().get_required_config_tool_names()

        required_config_tool_names.extend(
            (
                BOJIRA_TOOL_NAME,
                BOREGISTRY_TOOL_NAME,
                BOTOOLKIT_TOOL_NAME,
            )
        )

        return required_config_tool_names

    def get_required_config_options(self):
        required_config_options = super().get_required_config_options()

        required_config_options.update(
            {
                'jira': [
                    'url',
                    'username',
                    'password',
                ],
                'registry': [
                    'url',
                    'user',
                    'password',
                ],
            }
        )

        return required_config_options

    def take_action(
        self,
        parsed_args: Namespace,
    ):
        super().take_action(
            parsed_args=parsed_args,
        )

        registry_auxiliary_tool = RegistryAuxiliaryTool(
            registry_host_ip=self._parsed_args.registry_host_ip,
            registry_host_username=self._parsed_args.registry_host_username,
            registry_container_name=self._parsed_args.registry_container_name,
        )

        registry_api_client = parsed_args.registry_client(
            registry_domain=self._parsed_args.registry_url,
            username=self._parsed_args.registry_user,
            password=self._parsed_args.registry_password,
            verify=False,
            registry_auxiliary_tool=registry_auxiliary_tool,
        )

        jira_client = JiraAPIClient(
            url=self._parsed_args.jira_url,
            username=self._parsed_args.jira_username,
            password=self._parsed_args.jira_password,
        )

        repositories = filter(
            lambda r: DATABASER_DB_PREFIX in r,
            registry_api_client.get_repositories()
        )

        need_remove_repositories = []

        for repository_name in repositories:
            temp_repository_name = repository_name

            if '/' in repository_name:
                repository_name_parts = repository_name.split('/')
                repository_name = repository_name_parts[1]

            *_, project_abbr, task_number = (
                repository_name.split(f'{DATABASER_DB_PREFIX}-')[1].split('-')
            )

            need_remove = False

            try:
                issue_id = f'{project_abbr.upper()}-{task_number}'
                issue = jira_client.get_issue(
                    issue_id=issue_id,
                )

                if issue.fields.status.name == JIRA_CLOSED_TASK_STATUS_NAME:
                    need_remove = True
            except JIRAError:
                logger.write(f'JiraError with issue_id "{issue_id}"\n')

                need_remove = False

            if need_remove:
                need_remove_repositories.append(temp_repository_name)

        registry_api_client.delete_repositories(
            repository_names=need_remove_repositories,
        )


class BORegistryShowImagesCommand(
    RegistryClientArgumentMixin,
    RegistryArgumentsMixin,
    BOConfiguredToolLister,
):
    """
    Команда для отображения всех образов в Registry
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
            'Command for showing all Docker images from Registry'
        )

    def get_required_config_tool_names(self):
        required_config_tool_names = super().get_required_config_tool_names()

        required_config_tool_names.extend(
            (
                BOREGISTRY_TOOL_NAME,
                BOTOOLKIT_TOOL_NAME,
            )
        )

        return required_config_tool_names

    def get_required_config_options(self):
        required_config_options = super().get_required_config_options()

        required_config_options.update(
            {
                'registry': [
                    'url',
                    'user',
                    'password',
                ],
            }
        )

        return required_config_options

    def take_action(
        self,
        parsed_args: Namespace,
    ):
        super().take_action(
            parsed_args=parsed_args,
        )

        registry_api_client = parsed_args.registry_client(
            registry_domain=self._parsed_args.registry_url,
            username=self._parsed_args.registry_user,
            password=self._parsed_args.registry_password,
            verify=False,
        )

        repositories = [
            (index, repository, )
            for index, repository in enumerate(sorted(registry_api_client.get_repositories()), start=1)
        ]

        columns = (
            'index',
            'repository',
        )

        return columns, repositories


class BORegistryRemoveImageCommand(
    RegistryClientArgumentMixin,
    RegistryArgumentsMixin,
    BOConfiguredToolCommand,
):
    """
    Команда для удаления образов баз данных закрытых задач
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
            'Removing image from Registry. If you want remove multiple images, '
            'you should use | delimiter and parameter value in quotes.'
        )

    def get_required_config_tool_names(self):
        required_config_tool_names = super().get_required_config_tool_names()

        required_config_tool_names.extend(
            (
                BOREGISTRY_TOOL_NAME,
                BOTOOLKIT_TOOL_NAME,
            )
        )

        return required_config_tool_names

    def get_required_config_options(self):
        required_config_options = super().get_required_config_options()

        required_config_options.update(
            {
                'registry': [
                    'url',
                    'user',
                    'password',
                ],
            }
        )

        return required_config_options

    def get_parser(
        self,
        prog_name,
    ):
        parser = super().get_parser(
            prog_name=prog_name,
        )

        parser.add_argument(
            '--repository_name',
            action='store',
            type=str,
        )

        return parser

    def take_action(
        self,
        parsed_args: Namespace,
    ):
        super().take_action(
            parsed_args=parsed_args,
        )

        registry_auxiliary_tool = RegistryAuxiliaryTool(
            registry_host_ip=self._parsed_args.registry_host_ip,
            registry_host_username=self._parsed_args.registry_host_username,
            registry_container_name=self._parsed_args.registry_container_name,
        )

        registry_api_client = parsed_args.registry_client(
            registry_domain=self._parsed_args.registry_url,
            username=self._parsed_args.registry_user,
            password=self._parsed_args.registry_password,
            verify=False,
            registry_auxiliary_tool=registry_auxiliary_tool,
        )

        registry_api_client.delete_repositories(
            repository_names=parsed_args.repository_name.split('|'),
        )

