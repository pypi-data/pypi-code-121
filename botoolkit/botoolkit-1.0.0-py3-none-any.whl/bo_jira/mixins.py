import re
from typing import (
    Optional,
)

import validators

from botoolkit.bo_jenkins.mixins import (
    JenkinsStandURLArgumentMixin,
)
from botoolkit.bo_jira.consts import (
    JIRA_PROJECTS_CONFORMITY,
    JIRA_STAND_URL_RE,
)
from botoolkit.core.helpers import (
    findfirst,
)
from botoolkit.core.strings import (
    WRONG_ARGUMENT_VALUE,
)


class JiraIssueIDArgumentsMixin:
    """
    Добавляет параметры
        --jira_issue_id

    Для использования требуется, чтобы предварительно было создан клиент Jira
    """

    def patch_arguments_schema(self):
        super().patch_arguments_schema()

        self._arguments_schema.extend(
            (
                {
                    'section': 'jira',
                    'option': 'issue_id',
                    'help': 'Jira issue id',
                },
            )
        )

    def _validate_jira_issue_id(self):
        """
        Валидация параметра jira_issue_id
        """
        regexes = [
            f'{project_name}-[\d]+'
            for project_name in JIRA_PROJECTS_CONFORMITY.keys()
        ]

        if (
            not self._parsed_args.jira_issue_id or
            not any(findfirst(regex, self._parsed_args.jira_issue_id) for regex in regexes)  # noqa
        ):
            raise RuntimeError(
                WRONG_ARGUMENT_VALUE.format(
                    argument_name='jira_issue_id',
                )
            )
        else:
            self._issue = self._jira_client.get_issue(
                issue_id=self._parsed_args.jira_issue_id,
            )


class JiraArgumentsMixin:
    """
    Добавляет параметры
        --jira_url
        --jira_username
        --jira_password
    """

    def patch_arguments_schema(self):
        super().patch_arguments_schema()

        self._arguments_schema.extend(
            (
                {
                    'section': 'jira',
                    'option': 'url',
                    'help': 'URL сервиса Jira',
                },
                {
                    'section': 'jira',
                    'option': 'username',
                    'help': 'Имя пользователя в Jira.',
                },
                {
                    'section': 'jira',
                    'option': 'password',
                    'help': 'Пароль пользователя в Jira.',
                }
            )
        )

    def _validate_jira_url(self):
        """
        Валидация параметра jira_url
        """
        if (
            self._parsed_args.jira_url and
            not validators.url(self._parsed_args.jira_url)
        ):
            raise RuntimeError(
                WRONG_ARGUMENT_VALUE.format(
                    argument_name='jira_url',
                )
            )


class JiraTaskJenkinsStandURLArgumentMixin(JenkinsStandURLArgumentMixin):
    """
    Пропатченный миксин добавление параметра stand_url с его валидацией. Если
    значение не указано, то производится попытка парсинга
    """

    def _parse_stand_url(self) -> Optional[str]:
        """
        Получение URL тестового стенда и Идентификатора учреждения из описания
        задачи
        """
        stand_url = None

        parsing_result = re.findall(
            JIRA_STAND_URL_RE,
            self._issue.fields.description,
        )

        if parsing_result:
            stand_url= parsing_result[0]

        return stand_url

    def _validate_stand_url(self):
        """
        Валидация параметра stand_url
        """
        if not self._parsed_args.stand_url:
            self._parsed_args.stand_url = self._parse_stand_url()

        super()._validate_stand_url()
