# create logger
from os import listdir
from os.path import join, isfile
from typing import Optional, List, Dict

import smart_open
import typer
import json

from bigeye_cli import HOME_DIR
from bigeye_cli.enums import MetricFileType
from bigeye_sdk.client.datawatch_client import CoreDatawatchClient
from bigeye_sdk.functions.metric_functions import get_file_name_for_metric
from bigeye_sdk.model.enums import MetricStatus

from bigeye_sdk.log import get_logger
from bigeye_cli.functions import write_metric_info, cli_api_conf_factory, write_debug_queries
from bigeye_sdk.generated.com.torodata.models.generated import MetricInfoList, MetricInfo, TableList, Table, \
    MetricConfiguration
from bigeye_sdk.model.configuration_templates import SimpleUpsertMetricRequest

log = get_logger(__file__)

app = typer.Typer(help='Metric Commands for Bigeye CLI')

"""
File should contain commands that impact metrics by id or ids.
"""


@app.command()
def run(
        bigeye_conf: str = typer.Option(
            None
            , "--bigeye_conf"
            , "-b"
            , help="Bigeye Basic Auth Configuration File"),
        metric_ids: List[int] = typer.Option(
            ...
            , "--metric_id"
            , "-mid"
            , help="Metric Ids."
        )
):
    """Run metric by id(s)"""
    api_conf = cli_api_conf_factory(bigeye_conf)
    client = CoreDatawatchClient(api_conf=api_conf)

    r = client.run_metric_batch(metric_ids=metric_ids)
    log.info(r.to_json())


@app.command()
def get_info(
        bigeye_conf: str = typer.Option(
            None
            , "--bigeye_conf"
            , "-b"
            , help="Bigeye Basic Auth Configuration File"),
        metric_ids: List[int] = typer.Option(
            ...
            , "--metric_id"
            , "-mid"
            , help="Metric Ids."
        ),
        metric_status: MetricStatus = typer.Option(
            None
            , "--metric_status"
            , "-ms"
            , help="Used to query metric of particular status."),
        output_path: str = typer.Option(
            ...
            , "--output_path"
            , "-op"
            , help="File to write the failed metric configurations to."),
        only_metric_conf: bool = typer.Option(
            False
            , "--conf_only"
            , help="Output only the metric configuration.")
):
    """Outputs metric info to a file.  Includes metric configuration and details about recent runs."""
    api_conf = cli_api_conf_factory(bigeye_conf)
    client = CoreDatawatchClient(api_conf=api_conf)

    if metric_status:
        metric_status_name = metric_status.name
    else:
        metric_status_name = None

    mil: MetricInfoList = client.get_metric_info_batch_post(metric_ids=metric_ids,
                                                            status=metric_status_name
                                                            )

    write_metric_info(output_path=output_path, metrics=mil, only_metric_conf=only_metric_conf)


@app.command()
def upsert_from_path(
        bigeye_conf: str = typer.Option(
            f'{HOME_DIR}/.bigeye/conf/bigeye_demo.conf'
            , "--bigeye_conf"
            , "-b"
            , help="Bigeye Basic Auth Configuration File"),
        target_warehouse_id: int = typer.Option(
            ...
            , "--target_warehouse_id"
            , "-twid"
            , help="Deploy Metrics to target Warehouse ID."),
        source_path: str = typer.Option(
            ...
            , "--source_path"
            , "-sp"
            , help="Source path file containing the metrics to migrate.")
):
    """Upsert multiple metrics from files stored in path."""
    api_conf = cli_api_conf_factory(bigeye_conf)
    client = CoreDatawatchClient(api_conf=api_conf)

    all_files = [join(source_path, f) for f in listdir(source_path) if isfile(join(source_path, f)) and '.json' in f]

    def open_metric_info(file) -> MetricInfo:
        with smart_open.open(file) as fin:
            return MetricInfo().from_json(fin.read())

    mil: MetricInfoList = MetricInfoList()
    mil.metrics = [open_metric_info(f) for f in all_files]

    table_names = {m.metric_metadata.dataset_name for m in mil.metrics}

    tables: TableList = client.get_tables(warehouse_id=[target_warehouse_id], table_name=list(table_names))

    t_ix: Dict[str, Table] = {t.name: t for t in tables.tables}

    for m in mil.metrics:
        mc = m.metric_configuration

        log.info(mc)

        try:

            rmc = client.upsert_metric(
                schedule_frequency=mc.schedule_frequency,
                filters=mc.filters,
                group_bys=mc.group_bys,
                thresholds=mc.thresholds,
                notification_channels=mc.notification_channels,
                warehouse_id=target_warehouse_id,
                dataset_id=t_ix[m.metric_metadata.dataset_name].id,
                metric_type=mc.metric_type,
                parameters=mc.parameters,
                lookback=mc.lookback,
                lookback_type=mc.lookback_type,
                metric_creation_state=mc.metric_creation_state,
                grain_seconds=mc.grain_seconds,
                muted_until_epoch_seconds=mc.muted_until_epoch_seconds,
                name=mc.name,
                description=mc.description,
            )

        except Exception as e:
            log.exception(f"Error for file: {get_file_name_for_metric(m)}")
            log.exception(e)


@app.command()
def upsert(
        bigeye_conf: str = typer.Option(
            f'{HOME_DIR}/.bigeye/conf/bigeye_demo.conf'
            , "--bigeye_conf"
            , "-b"
            , help="Bigeye Basic Auth Configuration File"),
        file: str = typer.Option(
            ...
            , "--file"
            , "-f"
            , help="File containing SimpleUpsedrtMetricRequest or MetricConfiguration"),
        file_type: MetricFileType = typer.Option(
            ...
            , "--file_type"
            , "-t"
            , help="Metric File Type.  Simple conforms to SimpleUpsertMetricRequest and Full conforms to "
                   "MetricConfiguration"),
        target_warehouse_id: int = typer.Option(
            None
            , "--warehouse_id"
            , "-wid"
            , help="(Optional) Warehouse ID.  If specified it will reduce the text based search for the table."
                   "warehouse"),
        existing_metric_id: int = typer.Option(
            None
            , "--metric_id"
            , "-mid"
            , help="(Optional) Metric Id.  If specified it will reduce the text based search for existing metric."
        )
):
    """Upsert single metric from file."""
    api_conf = cli_api_conf_factory(bigeye_conf)
    client = CoreDatawatchClient(api_conf=api_conf)

    if file_type == MetricFileType.SIMPLE:
        with open(file, 'r') as file:
            simple_metric_conf = json.loads(file.read())

        simple_request = SimpleUpsertMetricRequest.from_dict(simple_metric_conf)

        client.upsert_metric_from_simple_template(target_warehouse_id=target_warehouse_id, sumr=simple_request,
                                                  existing_metric_id=existing_metric_id)

    elif file_type == MetricFileType.FULL:
        with open(file, 'r') as file:
            mcf = json.loads(file.read())

        mc = MetricConfiguration().from_json(mcf)

        client.upsert_metric(metric_configuration=mc)


@app.command()
def get_metric_queries(
        bigeye_conf: str = typer.Option(
            None
            , "--bigeye_conf"
            , "-b"
            , help="Bigeye Basic Auth Configuration File"),
        metric_ids: List[int] = typer.Option(
            ...
            , "--metric_id"
            , "-mid"
            , help="Metric Ids."),
        output_path: str = typer.Option(
            ...
            , "--output_path"
            , "-op"
            , help="File to write the failed metric configurations to.")
):
    """Gets the debug queries for all metrics by warehouse id, schema names, or table ids."""
    api_conf = cli_api_conf_factory(bigeye_conf)
    client = CoreDatawatchClient(api_conf=api_conf)

    r = client.get_debug_queries(metric_ids=metric_ids)

    write_debug_queries(output_path=output_path, queries=r)
