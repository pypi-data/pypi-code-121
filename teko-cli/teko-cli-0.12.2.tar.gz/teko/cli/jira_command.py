import typer

from teko.helpers.clog import CLog
from teko.services.jira.jira_service import JiraService

app = typer.Typer()


@app.command(name="create-tests")
def create_tests(
        file: str = typer.Argument(..., help='The name of a testcase definition file'),
   ):
    """
    """
    CLog.info("Jira submit test cases")
    jira_srv = JiraService()
    testcases = jira_srv.read_test_from_file(file)
    jira_srv.create_or_update_testcases_by_name(testcases)


@app.command(name="create-cycle")
def create_cycles(
        file: str = typer.Argument(..., help='The name of a testcase result file'),
   ):
    """
    """
    CLog.info("Jira submit test cycles")
    jira_srv = JiraService()
    testcases = jira_srv.read_test_from_file(file)
    jira_srv.create_test_cycles(testcases)
