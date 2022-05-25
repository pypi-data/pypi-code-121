from typing import Optional, List

import typer

from bigeye_cli.functions import cli_api_conf_factory, write_issue_info
from bigeye_sdk.client.datawatch_client import CoreDatawatchClient
from bigeye_sdk.log import get_logger

log = get_logger(__file__)

app = typer.Typer(help='Issues Commands for Bigeye CLI')

"""
File should contain commands that impact issues.
"""


@app.command()
def get_issues(
        bigeye_conf: str = typer.Option(
            None
            , "--bigeye_conf"
            , "-b"
            , help="Bigeye Basic Auth Configuration File"),
        warehouse_ids: Optional[List[int]] = typer.Option(
            None
            , "--warehouse_id"
            , "-wid"
            , help="Warehouse IDs."),
        schemas: Optional[List[str]] = typer.Option(
            None
            , "--schema_name"
            , "-sn"
            , help="Schema names"),
        metric_ids: Optional[List[int]] = typer.Option(
            None
            , "--metric_id"
            , "-mid"
            , help="Metric IDs."
        ),
        sla_ids: Optional[List[int]] = typer.Option(
            None
            , "--sla_id"
            , "-sla"
            , help="SLA IDs"),
        issue_ids: Optional[List[int]] = typer.Option(
            None
            , "--issue_id"
            , "-iid"
            , help="Issue IDs"),
        output_path: str = typer.Option(
            ...
            , "--output_path"
            , "-op"
            , help="File to write the failed metric configurations to.")
):
    """Gets issues and writes info to files."""
    api_conf = cli_api_conf_factory(bigeye_conf)
    client = CoreDatawatchClient(api_conf=api_conf)

    issues = client.get_issues(warehouse_ids=warehouse_ids,
                               schemas=schemas,
                               metric_ids=metric_ids,
                               sla_ids=sla_ids,
                               issue_ids=issue_ids)

    write_issue_info(output_path=output_path, issues=issues)


@app.command()
def update_issue(
        bigeye_conf: str = typer.Option(
            None
            , "--bigeye_conf"
            , "-b"
            , help="Bigeye Basic Auth Configuration File"),
        issue_id: int = typer.Option(
            ...
            , "--issue_id"
            , "-iid"
            , help="Issue ID"),
        issue_status: str = typer.Option(
            None
            , "--issue_status"
            , "-status"
            , help="The status update. Options are ACKNOWLEDGED or CLOSED."),
        updated_by: str = typer.Option(
            None
            , "--updated_by"
            , "-by"
            , help="The user providing the update."),
        message: str = typer.Option(
            None
            , "--message"
            , "-m"
            , help="The message to attach to the issue."),
        closing_label: str = typer.Option(
            None
            , "--closing_label"
            , "-cl"
            , help="Used to train Bigeye when closing an issue. Options are TRUE_POSITIVE, FALSE_POSITIVE, EXPECTED.")
):
    """Updates an issue in Bigeye and returns the Issue object from the protobuff."""
    api_conf = cli_api_conf_factory(bigeye_conf)
    client = CoreDatawatchClient(api_conf=api_conf)

    client.update_issue(issue_id=issue_id,
                        issue_status=issue_status,
                        updated_by=updated_by,
                        update_message=message,
                        closing_label=closing_label)
