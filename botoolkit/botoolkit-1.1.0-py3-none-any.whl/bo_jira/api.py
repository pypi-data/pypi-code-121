from jira import (
    JIRA,
)


class JiraAPIClient:
    """
    Клиент Jira
    """

    def __init__(
        self,
        url: str,
        username: str,
        password: str,
    ):
        self._server = JIRA(
            server=url,
            basic_auth=(
                username,
                password,
            ),
        )

    def get_issue(
        self,
        issue_id: str,
    ):
        """
        Получение задачи по идентификатору
        """
        return self._server.issue(issue_id)

    def search_issues(
        self,
        jql_str: str,
        max_results: int = 50,
    ):
        """
        Получение списка задач согласно переданного фильтра
        """
        issues = self._server.search_issues(
            jql_str=jql_str,
            maxResults=max_results,
        )

        return issues

    def add_comment_by_task_id(
        self,
        task_id: str,
        comment: str,
    ):
        """
        Добавление комментария к задаче
        """
        self._server.add_comment(
            issue=task_id,
            body=comment,
        )

    def update_field(
        self,
        issue,
        field: str,
        value: str,
    ):
        """
        Обновление значения поля задачи
        """
        issue.update(
            fields={
                field: value,
            },
        )
