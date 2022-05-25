def prepare_jira_issue_url(
    jira_url: str,
    issue_id: str,
):
    """
    Формирует URL задачи Jira
    """
    return f'{jira_url}browse/{issue_id}'
