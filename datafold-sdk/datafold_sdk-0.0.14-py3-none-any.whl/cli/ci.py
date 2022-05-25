import json
import logging
import sys

import click

from datafold_sdk.sdk.ci import run_diff, CiDiff

logger = logging.getLogger(__file__)


@click.group()
def manager():
    """CI management."""


@manager.command()
@click.option('--ci-config-id',
              help="The ID of the CI config in Datafold (see CI settings screen)",
              type=int,
              required=True)
@click.option('--pr-num',
              help="The number of the Pull Request",
              type=int,
              required=True)
@click.option('--diffs',
              help='compose file to work with',
              type=click.File('r'),
              default=sys.stdin)
@click.pass_context
def submit(ctx: click.Context, ci_config_id: int, pr_num: int, diffs):
    """Submit the CI"""
    with diffs:
        diffs_json = diffs.read()
    diffs_dicts = json.loads(diffs_json)
    ci_diffs = [CiDiff(**d) for d in diffs_dicts]

    run_id = run_diff(
        host=ctx.obj.host,
        api_key=ctx.obj.api_key,
        ci_config_id=ci_config_id,
        pr_num=pr_num,
        diffs=ci_diffs
    )
    if run_id:
        logger.info(f"Successfully started a diff under Run ID {run_id}")
    else:
        logger.info("Could not find an active job for the pull request, is the CI set up correctly?")
