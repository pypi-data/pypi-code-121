from teko.helpers.clog import CLog


class TekoJiraException(Exception):
    pass


class ExportTestException(Exception):
    pass


def raise_jira_exception(msg: str = ""):
    CLog.error(msg)
    raise TekoJiraException(msg) from None
