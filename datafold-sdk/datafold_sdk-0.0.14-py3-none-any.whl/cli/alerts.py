import logging
import time
import sys
from typing import Optional

from datetime import datetime
import click

from datafold_sdk.sdk.utils import prepare_api_url, prepare_headers, post_data, get_data

logger = logging.getLogger(__file__)

DATE_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"


@click.group()
def manager():
    """Alert queries management."""


@manager.command()
@click.option('--id', 'query_id', type=int, required=True)
@click.option('--wait', type=int, default=None,
              help="How long to wait for the query (seconds).")
@click.option('--interval', type=click.IntRange(1, 60), default=3,
              help="How often to poll for the query result (seconds).")
@click.pass_context
def run(ctx: click.Context, query_id: int, wait: Optional[int], interval: int):
    """ Run the query, trigger the alerts. """
    headers = prepare_headers(ctx.obj.api_key)

    api_segment = f"api/v1/alerts/{query_id}/checks"
    url = prepare_api_url(ctx.obj.host, api_segment)
    resp = post_data(url, json={}, headers=headers)
    data = resp.json()
    result_id = data['id']
    logger.debug(f"API response={data!r}")

    started = time.monotonic()
    last_status: Optional[str] = None
    while wait and time.monotonic() < started + wait:
        # Sleep first, as it is never done immediately on creation.
        remaining_time = started + wait - time.monotonic()
        time.sleep(min(float(interval), remaining_time))

        api_segment = f"api/alert_query_result/{result_id}"
        url = prepare_api_url(ctx.obj.host, api_segment)
        resp = get_data(url, headers=headers)
        data = resp.json()
        last_status = data['status']
        logger.debug(f"API response={data!r}")

        if last_status in ["done", "failed"]:
            break

    if last_status in ["done", "failed"]:
        logger.info(f"Finished a run {result_id} for the query {query_id}: "
                    f"status={last_status}")

        if wait and last_status == 'done':
            api_result = f"api/alert_query/{query_id}"
            url = prepare_api_url(ctx.obj.host, api_result)
            resp = get_data(url, headers=headers)
            data = resp.json()
            logger.debug(f"API response={data!r}")
            # If there is no trigger, then last_triggered will be null
            if data['last_triggered']:
                last_triggered = datetime.strptime(data['last_triggered']['value'], DATE_FORMAT)
                last_run = datetime.strptime(data['last_run']['value'], DATE_FORMAT)
                if last_triggered >= last_run:
                    # The alert triggered, so we should error
                    logger.warning(f"The alert triggered, check for details: {ctx.obj.host}/query_alert/{query_id}")
                    sys.exit(22)

        if last_status == 'failed':
            sys.exit(22)

    elif wait:
        logger.warning(f"Timed out waiting for a run {result_id} for the query {query_id}. "
                       "It is still running, but we do not wait.")
    else:
        logger.warning(f"Started a run {result_id} for the query {query_id}.")
