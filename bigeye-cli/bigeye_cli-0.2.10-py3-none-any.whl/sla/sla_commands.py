# create logger
from os import listdir
from os.path import join, isfile
from typing import List, Optional, Dict

import smart_open
import typer

from bigeye_cli.functions import cli_api_conf_factory, write_debug_queries
from bigeye_sdk.client.datawatch_client import CoreDatawatchClient
from bigeye_sdk.generated.com.torodata.models.generated import TableList, Table, MetricConfiguration, MetricInfo
from bigeye_sdk.model.sla_models import SlaMetrics
from bigeye_cli import HOME_DIR

from bigeye_sdk.log import get_logger
from bigeye_sdk.functions.file_functs import serialize_listdict_to_json_file

log = get_logger(__file__)

app = typer.Typer(help='SLA Commands for Bigeye CLI')


@app.command()
def add_metric(
        bigeye_conf: str = typer.Option(
            f'{HOME_DIR}/.bigeye/conf/bigeye_demo.conf'
            , "--bigeye_conf"
            , "-b"
            , help="Bigeye Basic Auth Configuration File"),
        metric_ids: List[int] = typer.Option(
            ...
            , "--metric_id"
            , "-mid"
            , help="Metric ID"),
        sla_id: int = typer.Option(
            ...
            , "--sla_id"
            , "-sid"
            , help="SLA ID"),
):
    """Add metric to an SLA."""
    log.info(f'Adding metric to SLA.')
    log.info(f'Bigeye API Configuration: {bigeye_conf} | Metric IDs: {metric_ids} | SLA ID: {sla_id}')

    api_conf = cli_api_conf_factory(bigeye_conf)
    client = CoreDatawatchClient(api_conf=api_conf)

    client.upsert_metric_to_collection(add_metric_ids=metric_ids, collection_id=sla_id)


@app.command()
def get_metric_info(bigeye_conf: str = typer.Option(
    ...
    , "--bigeye_conf"
    , "-b"
    , help="Bigeye Basic Auth Configuration File")
        , from_slas: bool = typer.Option(
            False
            , "--from_slas"
            , help="Scrapes all SLAs in customer workspace for Metric Info.")
        , sla_ids: Optional[List[int]] = typer.Option(
            None
            , "--sla_ids"
            , help="SLA IDs.  Scrape certain SLAs for Metric Info.")
        , output_path: str = typer.Option(
            ...
            , "--output_path"
            , "-op"
            , help="File to write the failed metric configurations to."), ):
    """Get metric info for all metrics in SLA."""
    api_conf = cli_api_conf_factory(bigeye_conf)
    client = CoreDatawatchClient(api_conf=api_conf)
    collections = client.get_collections()
    collections_to_migrate = [c for c in collections.collections if c.id in sla_ids] if not from_slas else collections

    for c in collections_to_migrate.collections:
        sla_metric = SlaMetrics(c, client.get_metric_info_batch_post(metric_ids=c.metric_ids))

        url = f'{output_path}/{c.name}.json'

        serialize_listdict_to_json_file(url=url,
                                        data=[sla_metric.as_dict()])


@app.command()
def migrate_from_json(bigeye_conf: str = typer.Option(
    ...
    , "--bigeye_conf"
    , "-b"
    , help="Bigeye Basic Auth Configuration File")
        , target_warehouse_id: int = typer.Option(
            ...
            , "--target_warehouse_id"
            , "-twid"
            , help="Deploy Metrics to target Warehouse ID.")
        , input_path: str = typer.Option(
            ...
            , "--input_path"
            , "-ip"
            , help="Path to read from.")
        , keep_notifications: bool = typer.Option(
            False
            , "--keep_notifications"
            , "-kn"
            , help="Keep Notifications from versioned or templated metric configuration.")
        , keep_ids: bool = typer.Option(
            False
            , "--keep_ids"
            , "-kid"
            , help="Keep Metric and SLA IDs from versioned or templated metric configuration.  "
                   "If kept this would update existing metrics and slas.  If not kept it would "
                   "create new.")
):
    """Loads metrics from SLA oriented metric info output.  Used to migrate metrics from one warehouse to
    another, identical, warehouse"""
    api_conf = cli_api_conf_factory(bigeye_conf)
    client = CoreDatawatchClient(api_conf=api_conf)

    all_files = [join(input_path, f) for f in listdir(input_path) if isfile(join(input_path, f)) and '.json' in f]

    def open_sla_metrics(file) -> SlaMetrics:
        with smart_open.open(file) as fin:
            return SlaMetrics.from_json(fin.read())

    for f in all_files:
        """One SLA per File."""
        sla_metrics = open_sla_metrics(f)

        # Clearing workspace specific settings.
        if not keep_notifications:
            sla_metrics.sla.id = None
        sla_metrics.sla.entity_info = None
        sla_metrics.sla.owner = None
        if not keep_ids:
            sla_metrics.sla.metric_ids = []
        if keep_notifications:
            sla_metrics.sla.notification_channels = []
        m: MetricInfo
        for m in sla_metrics.metrics.metrics:
            if not keep_ids:
                m.metric_configuration.id = None
            if not keep_notifications:
                m.metric_configuration.notification_channels = []

        table_names = {m.metric_metadata.dataset_name for m in sla_metrics.metrics.metrics}

        tables: TableList = client.get_tables(warehouse_id=[target_warehouse_id], table_name=list(table_names))

        t_ix: Dict[str, Table] = {t.name: t for t in tables.tables}

        for m in sla_metrics.metrics.metrics:
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

                sla_metrics.sla.metric_ids.append(rmc.id)

            except Exception as e:
                log.exception(f"Error for SLA: {sla_metrics.sla.name}")
                log.exception(e)

        client.create_collection(sla_metrics.sla)


@app.command()
def backfill_metrics(bigeye_conf: str = typer.Option(
    ...
    , "--bigeye_conf"
    , "-b"
    , help="Bigeye Basic Auth Configuration File")
        , from_slas: bool = typer.Option(
            False
            , "--from_slas"
            , help="Scrapes all SLAs in customer workspace for Metric Info.")
        , sla_ids: Optional[List[int]] = typer.Option(
            None
            , "--sla_ids"
            , help="SLA IDs.  Scrape certain SLAs for Metric Info.")):
    """Backfill all metrics in an SLA."""
    api_conf = cli_api_conf_factory(bigeye_conf)
    client = CoreDatawatchClient(api_conf=api_conf)
    collections = client.get_collections()
    collections_to_migrate = [c for c in collections.collections if c.id in sla_ids] if not from_slas else collections

    mids = []

    slaids = []

    for c in collections_to_migrate.collections:
        sla_metrics = SlaMetrics(c, client.get_metric_info_batch_post(metric_ids=c.metric_ids).metrics)
        mids.extend([m.metric_configuration.id for m in sla_metrics.metrics])
        slaids.append(c.id)

    for mid in mids:
        try:
            client.backfill_metric(metric_ids=[mid])
        except Exception as e:
            log.exception(e)

    client.run_metric_batch(metric_ids=mids)


@app.command()
def run_metrics(
        bigeye_conf: str = typer.Option(
            f'{HOME_DIR}/.bigeye/conf/bigeye_demo.conf'
            , "--bigeye_conf"
            , "-b"
            , help="Bigeye Basic Auth Configuration File"),
        sla_id: int = typer.Option(
            ...
            , "--sla_id"
            , "-sid"
            , help="SLA ID"),
):
    """Run all metrics in an SLA."""
    api_conf = cli_api_conf_factory(bigeye_conf)
    client = CoreDatawatchClient(api_conf=api_conf)
    collection = client.get_collection(collection_id=sla_id)
    mids: List[int] = collection.collection.metric_ids
    client.run_metric_batch(metric_ids=mids)

@app.command()
def get_metric_queries(
        bigeye_conf: str = typer.Option(
            None
            , "--bigeye_conf"
            , "-b"
            , help="Bigeye Basic Auth Configuration File"),
        sla_id: int = typer.Option(
            ...
            , "--sla_id"
            , "-sid"
            , help="SLA ID"),
        output_path: str = typer.Option(
            ...
            , "--output_path"
            , "-op"
            , help="File to write the failed metric configurations to.")
):
    """Gets the debug queries for all metrics by warehouse id, schema names, or table ids."""
    api_conf = cli_api_conf_factory(bigeye_conf)
    client = CoreDatawatchClient(api_conf=api_conf)

    collection = client.get_collection(collection_id=sla_id)
    mids: List[int] = collection.collection.metric_ids

    r = client.get_debug_queries(metric_ids=mids)

    write_debug_queries(output_path=output_path, queries=r)