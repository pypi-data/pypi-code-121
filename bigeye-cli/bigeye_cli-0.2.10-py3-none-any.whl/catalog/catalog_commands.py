# create logger
import json
from typing import Optional, List

import typer
from bigeye_sdk.client.enum import Method

from bigeye_aws.functions.aws import get_secret
from bigeye_cli.enums import OPS_METRICS
from bigeye_sdk.client.datawatch_client import CoreDatawatchClient
from bigeye_sdk.model.enums import MetricStatus, SimpleMetricType
from bigeye_cli import HOME_DIR
from bigeye_sdk.generated.com.torodata.models.generated import MetricInfoList, WarehouseType, CreateSourceRequest, \
    TimeIntervalType, PredefinedMetricName, MetricCreationState
from bigeye_sdk.log import get_logger
from bigeye_cli.functions import write_metric_info, cli_api_conf_factory, write_table_info, write_debug_queries
from bigeye_sdk.functions.metric_functions import has_auto_threshold
from bigeye_sdk.functions.core_py_functs import int_enum_enum_list_joined

log = get_logger(__file__)

app = typer.Typer(help='Catalog Commands for Bigeye CLI')

"""
File should contain commands that will impact catalog, table, or schema level changes to a Bigeye workspace.  This
would include metrics batched at any of these levels.
"""


@app.command()
def regen_autometrics(
        bigeye_conf: str = typer.Option(
            f'{HOME_DIR}/.bigeye/conf/bigeye_demo.conf'
            , "--bigeye_conf"
            , "-b"
            , help="Bigeye Basic Auth Configuration File"),
        warehouse_id: int = typer.Option(
            None
            , "--warehouse_id"
            , "-wid"
            , help="Warehouse ID.  If none will look for Table IDs.  If value then will pull all table ids for "
                   "warehouse"),
        schema_names: Optional[List[str]] = typer.Option(
            None
            , "--schema_name"
            , "-sn"
            , help="List of Schema Names  E.g. -sn schema_1 -sn schema_2.  Do not include warehouse name -- "
                   "GREENE_HOMES_DEMO_STANDARD.CONFORMED is fully qualified and CONFORMED is the schema name."),
        table_ids: Optional[List[int]] = typer.Option(
            None
            , "--table_id"
            , "-tid"
            , help="List of Table IDs.  E.g. -tid 123 -tid 124")
):
    """Regenerates Autometrics by warehouse id OR warehouse id and list of schema names OR list of table ids."""
    api_conf = cli_api_conf_factory(bigeye_conf)
    client = CoreDatawatchClient(api_conf=api_conf)

    if not table_ids:
        table_ids = client.get_table_ids(warehouse_id=[warehouse_id], schemas=schema_names)

    if table_ids:
        log.info(f'Regenerating autometrics on: {table_ids}')
        for tid in table_ids:
            client.regen_autometrics(table_id=tid)
    else:
        raise Exception('Could not identify table_ids to run.  Provide either a valid list of table ids OR a valid '
                        'warehouse ID OR a valid warehouse ID and list of valid schema names')


@app.command()
def deploy_all_autometrics(
        bigeye_conf: str = typer.Option(
            f'{HOME_DIR}/.bigeye/conf/bigeye_demo.conf'
            , "--bigeye_conf"
            , "-b"
            , help="Bigeye Basic Auth Configuration File"),
        warehouse_id: int = typer.Option(
            None
            , "--warehouse_id"
            , "-wid"
            , help="Deploy autometrics to all tables in warehouse."),
        schema_names: Optional[List[str]] = typer.Option(
            None
            , "--schema_name"
            , "-sn"
            , help="List of Schema Names.  E.g. -sn schema_1 -sn schema_2."),
        table_ids: Optional[List[int]] = typer.Option(
            None
            , "--table_id"
            , "-tid"
            , help="Table IDs.  E.g. -tid 123 -tid 124"),
        lookback_days: int = typer.Option(
            7
            , "--lookback_days"
            , "-lbd"
            , help="Look back days for the metrics."
        ),
        ops_only: bool = typer.Option(
            True
            , "--ops_only"
            , help="Deploy only operational metrics")
):
    """Deploys all Autometrics to specified warehouse OR warehouse and list of schema names OR warehouse and list of
    table ids."""
    # TODO: Add operational metrics only code.
    log.info(f'Deploying all metrics.')
    log.info(f'Bigeye API Configuration: {bigeye_conf} | Warehouse ID: {warehouse_id} | Table IDs: {table_ids}')

    api_conf = cli_api_conf_factory(bigeye_conf)
    client = CoreDatawatchClient(api_conf=api_conf)

    ms = MetricCreationState.METRIC_CREATION_STATE_SUGGESTED_AUTO

    mil = MetricInfoList()

    if not schema_names:
        mil = client.get_metric_info_batch_post(warehouse_ids=[warehouse_id], table_ids=table_ids,
                                                metric_creation_states=[ms])

    if schema_names:
        for sn in schema_names:
            submil = client.get_metric_info_batch_post(warehouse_ids=[warehouse_id], table_ids=table_ids,
                                                       metric_creation_states=[ms], schema_name=sn)
            mil.metrics.extend(submil.metrics)

    if ops_only:
        mil.metrics = [m for m in mil.metrics if m.metric_configuration.metric_type.predefined_metric in OPS_METRICS]

    mids: List[int] = [m.metric_configuration.id for m in mil.metrics]

    client.accept_autometrics(metric_ids=mids, lookback_days=lookback_days)


@app.command()
def delete_metrics(
        bigeye_conf: str = typer.Option(
            None
            , "--bigeye_conf"
            , "-b"
            , help="Bigeye Basic Auth Configuration File"),
        warehouse_id: int = typer.Option(
            None
            , "--warehouse_id"
            , "-wid"
            , help="Warehouse ID"),
        schema_names: Optional[List[str]] = typer.Option(
            None
            , "--schema_name"
            , "-sn"
            , help="List of Schema Names.  E.g. -sn schema_1 -sn schema_2."),

        table_ids: Optional[List[int]] = typer.Option(
            None
            , "--table_id"
            , "-tid"
            , help="Table IDs.  E.g. -tid 123 -tid 124"),
        metric_names: Optional[List[str]] = typer.Option(
            None
            , "--metric_name"
            , "-m"
            , help=f"Predefined Metric Names to filter by."
                   f"{', '.join([i.name for i in PredefinedMetricName])}"),
):
    """Delete metrics in a warehouse id, by schema names, or by table_ids.  Also, can filter by multipe
    metric types."""
    api_conf = cli_api_conf_factory(bigeye_conf)
    client = CoreDatawatchClient(api_conf=api_conf)

    mil: MetricInfoList = client.get_metric_info_batch_post(warehouse_ids=[warehouse_id],
                                                            table_ids=table_ids)
    if schema_names:
        mil.metrics = [m for m in mil.metrics if m.metric_metadata.schema_name in schema_names]

    if metric_names:
        mil.metrics = [m for m in mil.metrics
                       if SimpleMetricType.get_metric_name(m.metric_configuration.metric_type) in metric_names]

    for m in mil.metrics:
        client.delete_metric(metric_id=m.metric_configuration.id)


@app.command()
def rebuild(
        bigeye_conf: str = typer.Option(
            f'{HOME_DIR}/.bigeye/conf/bigeye_demo.conf'
            , "--bigeye_conf"
            , "-b"
            , help="Bigeye Basic Auth Configuration File"),
        warehouse_id: int = typer.Option(
            ...
            , "--warehouse_id"
            , "-wid"
            , help="Warehouse ID"),
        schema_name: str = typer.Option(
            None
            , "--schema_name"
            , "-sn"
            , help="Schema Name"),
):
    """Rebuilds/Reprofiles a source by warehouse id or a schema by warehouse id and schema name."""
    api_conf = cli_api_conf_factory(bigeye_conf)
    client = CoreDatawatchClient(api_conf=api_conf)

    log.info(f'Rebuilding Catalog Resource.  Warehouse ID: {warehouse_id}  Schema Name: {schema_name}')
    client.rebuild(warehouse_id=warehouse_id, schema_name=schema_name)


@app.command()
def get_table_info(
        bigeye_conf: str = typer.Option(
            None
            , "--bigeye_conf"
            , "-b"
            , help="Bigeye Basic Auth Configuration File"),
        warehouse_id: int = typer.Option(
            None
            , "--warehouse_id"
            , "-wid"
            , help="Warehouse ID"),
        schema_names: Optional[List[str]] = typer.Option(
            None
            , "--schema_name"
            , "-sn"
            , help="List of Schema Names.  E.g. -sn schema_1 -sn schema_2."),

        table_ids: Optional[List[int]] = typer.Option(
            None
            , "--table_id"
            , "-tid"
            , help="Table IDs. E.g. -tid 123 -tid 124"),
        table_names: Optional[List[str]] = typer.Option(
            None
            , "--table_name"
            , "-tn"
            , help="Table Namess. E.g. -tn some_table -tn some_other_table"),
        output_path: str = typer.Option(
            ...
            , "--output_path"
            , "-op"
            , help="File to write the failed metric configurations to.")
):
    """Outputs table info to a file for an entire warehouse, certain schemas, or certain tables."""
    api_conf = cli_api_conf_factory(bigeye_conf)
    client = CoreDatawatchClient(api_conf=api_conf)

    wids = [] if not warehouse_id else [warehouse_id]

    tables = client.get_tables(warehouse_id=wids, schema=schema_names,
                               ids=table_ids, table_name=table_names)

    write_table_info(output_path=output_path, tables=tables.tables)


@app.command()
def get_metric_info(
        bigeye_conf: str = typer.Option(
            None
            , "--bigeye_conf"
            , "-b"
            , help="Bigeye Basic Auth Configuration File"),
        warehouse_id: int = typer.Option(
            None
            , "--warehouse_id"
            , "-wid"
            , help="Warehouse ID"),
        schema_names: Optional[List[str]] = typer.Option(
            None
            , "--schema_name"
            , "-sn"
            , help="List of Schema Names.  E.g. -sn schema_1 -sn schema_2."),

        table_ids: Optional[List[int]] = typer.Option(
            None
            , "--table_id"
            , "-tid"
            , help="Table IDs. E.g. -tid 123 -tid 124"
                   "or schema names."),
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

    mil: MetricInfoList = client.get_metric_info_batch_post(warehouse_ids=[warehouse_id],
                                                            table_ids=table_ids,
                                                            status=metric_status_name)

    if schema_names:
        mil.metrics = [m for m in mil.metrics if m.metric_metadata.schema_name in schema_names]

    write_metric_info(output_path=output_path, metrics=mil, only_metric_conf=only_metric_conf)


@app.command()
def run_metrics(
        bigeye_conf: str = typer.Option(
            None
            , "--bigeye_conf"
            , "-b"
            , help="Bigeye Basic Auth Configuration File"),
        warehouse_id: int = typer.Option(
            None
            , "--warehouse_id"
            , "-wid"
            , help="Warehouse ID"),
        schema_names: Optional[List[str]] = typer.Option(
            None
            , "--schema_name"
            , "-sn"
            , help="List of Schema Names.  E.g. -sn schema_1 -sn schema_2."),

        table_ids: Optional[List[int]] = typer.Option(
            None
            , "--table_id"
            , "-tid"
            , help="Table IDs. E.g. -tid 123 -tid 124"),
        table_names: Optional[List[str]] = typer.Option(
            None
            , "--table_name"
            , "-tn"
            , help="Table Namess. E.g. -tn some_table -tn some_other_table")
):
    """Runs all metrics for a warehouse, particular schemas in a warehouse, or tables by id."""
    api_conf = cli_api_conf_factory(bigeye_conf)
    client = CoreDatawatchClient(api_conf=api_conf)

    wids = [] if not warehouse_id else [warehouse_id]

    mil = client.get_metric_info_batch_post(warehouse_ids=wids, table_ids=table_ids)

    if schema_names and table_names:
        mids = [m.metric_configuration.id for m in mil.metrics
                if m.metric_metadata.schema_name in schema_names and m.metric_metadata.dataset_name in table_names]
    elif schema_names:
        mids = [m.metric_configuration.id for m in mil.metrics if m.metric_metadata.schema_name in schema_names]
    elif table_names:
        mids = [m.metric_configuration.id for m in mil.metrics if m.metric_metadata.dataset_name in table_names]
    else:
        mids = [m.metric_configuration.id for m in mil.metrics]

    r = client.run_metric_batch(metric_ids=mids)
    log.info(r.to_json())


@app.command()
def add_source(
        bigeye_conf: str = typer.Option(
            None
            , "--bigeye_conf"
            , "-b"
            , help="Bigeye Basic Auth Configuration File"),
        secret_name: str = typer.Option(
            None
            , "--secret_name"
            , "-sn"
            , help="""The name of the secret to retrieve from AWS Secrets Manager"""),
        secret_region_name: str = typer.Option(
            'us-west-2'
            , "--secret_region_name"
            , "-srn"
            , help="AWS Secret Manager Region Name"),
        source_catalog_config_file: str = typer.Option(
            None
            , "--source_catalog_config_file"
            , "-sccf"
            , help="The file containing the necessary parameters for adding a source to Bigeye."
        )
):
    """Adds a source to specified Bigeye workspace.  Supports either source configs stored in AWS Secrets manager OR
    locally in file."""
    api_conf = cli_api_conf_factory(bigeye_conf)
    client = CoreDatawatchClient(api_conf=api_conf)

    if secret_name:
        secret = get_secret(secret_name, secret_region_name)
        source_config = json.loads(secret['SecretString'])
    else:
        log.info(f'Loading source config file: {source_catalog_config_file}')
        with open(source_catalog_config_file) as json_file:
            source_config = json.load(json_file)

    db_type = source_config['database_type'].upper()
    source_config['database_type'] = WarehouseType[f'DATABASE_TYPE_{db_type}']

    client.create_source(CreateSourceRequest(**source_config))


@app.command()
def delete_source(
        bigeye_conf: str = typer.Option(
            None
            , "--bigeye_conf"
            , "-b"
            , help="Bigeye Basic Auth Configuration File"),
        warehouse_id: int = typer.Option(
            None
            , "--warehouse_id"
            , "-wid"
            , help="""The ID of the warehouse to delete."""),
):
    """Delete a source from specified Bigeye workspace."""
    api_conf = cli_api_conf_factory(bigeye_conf)
    client = CoreDatawatchClient(api_conf=api_conf)

    client.delete_source(warehouse_id)


@app.command()
def backfill_autothresholds(
        bigeye_conf: str = typer.Option(
            None
            , "--bigeye_conf"
            , "-b"
            , help="Bigeye Basic Auth Configuration File"),
        warehouse_id: int = typer.Option(
            None
            , "--warehouse_id"
            , "-wid"
            , help="Warehouse ID"),
        schema_names: Optional[List[str]] = typer.Option(
            None
            , "--schema_name"
            , "-sn"
            , help="List of Schema Names.  E.g. -sn schema_1 -sn schema_2."),

        table_ids: Optional[List[int]] = typer.Option(
            None
            , "--table_id"
            , "-tid"
            , help="Table IDs.  E.g. -tid 123 -tid 124")
):
    """Backfills autothresholds by warehouse id, schema names, and/or table ids."""
    api_conf = cli_api_conf_factory(bigeye_conf)
    client = CoreDatawatchClient(api_conf=api_conf)

    mil: MetricInfoList = client.get_metric_info_batch_post(warehouse_ids=[warehouse_id],
                                                            table_ids=table_ids)
    if schema_names:
        mil.metrics = [m for m in mil.metrics if m.metric_metadata.schema_name in schema_names]

    mids = [m.metric_configuration.id for m in mil.metrics if has_auto_threshold(m.metric_configuration.thresholds)]

    client.backfill_autothresholds(metric_ids=mids)


@app.command()
def backfill_metrics(
        bigeye_conf: str = typer.Option(
            None
            , "--bigeye_conf"
            , "-b"
            , help="Bigeye Basic Auth Configuration File"),
        warehouse_id: int = typer.Option(
            None
            , "--warehouse_id"
            , "-wid"
            , help="Warehouse ID"),
        schema_names: Optional[List[str]] = typer.Option(
            None
            , "--schema_name"
            , "-sn"
            , help="List of Schema Names.  E.g. -sn schema_1 -sn schema_2."),

        table_ids: Optional[List[int]] = typer.Option(
            None
            , "--table_id"
            , "-tid"
            , help="Table IDs.  E.g. -tid 123 -tid 124")
):
    """Backfills metrics by warehouse id, schema names, and/or table ids."""
    api_conf = cli_api_conf_factory(bigeye_conf)
    client = CoreDatawatchClient(api_conf=api_conf)

    mil: MetricInfoList = client.get_metric_info_batch_post(warehouse_ids=[warehouse_id],
                                                            table_ids=table_ids)
    if schema_names:
        mil.metrics = [m for m in mil.metrics if m.metric_metadata.schema_name in schema_names]

    metadata_metric_mids = [m.metric_configuration.id for m in mil.metrics if m.metric_configuration.metric_type]

    mids = [m.metric_configuration.id for m in mil.metrics]

    for mid in mids:
        try:
            client.backfill_metric(metric_ids=[mid])
        except Exception as e:
            log.exception(e)
    client.run_metric_batch(metric_ids=mids)


@app.command()
def run_metrics(
        bigeye_conf: str = typer.Option(
            None
            , "--bigeye_conf"
            , "-b"
            , help="Bigeye Basic Auth Configuration File"),
        warehouse_id: int = typer.Option(
            None
            , "--warehouse_id"
            , "-wid"
            , help="Warehouse ID"),
        schema_names: Optional[List[str]] = typer.Option(
            None
            , "--schema_name"
            , "-sn"
            , help="List of Schema Names.  E.g. -sn schema_1 -sn schema_2."),

        table_ids: Optional[List[int]] = typer.Option(
            None
            , "--table_id"
            , "-tid"
            , help="Table IDs.  E.g. -tid 123 -tid 124")
):
    """Runs metrics by warehouse id, schema names, and/or table ids"""
    api_conf = cli_api_conf_factory(bigeye_conf)
    client = CoreDatawatchClient(api_conf=api_conf)

    mil: MetricInfoList = client.get_metric_info_batch_post(warehouse_ids=[warehouse_id],
                                                            table_ids=table_ids)
    if schema_names:
        mil.metrics = [m for m in mil.metrics if m.metric_metadata.schema_name in schema_names]

    metadata_metric_mids = [m.metric_configuration.id for m in mil.metrics if m.metric_configuration.metric_type]

    mids = [m.metric_configuration.id for m in mil.metrics]

    client.run_metric_batch(metric_ids=mids)


@app.command()
def schedule_all_metrics(
        bigeye_conf: str = typer.Option(
            None
            , "--bigeye_conf"
            , "-b"
            , help="Bigeye Basic Auth Configuration File"),
        warehouse_id: int = typer.Option(
            None
            , "--warehouse_id"
            , "-wid"
            , help="Warehouse ID"),
        time_interval_type: int = typer.Option(
            TimeIntervalType.HOURS_TIME_INTERVAL_TYPE.value
            , "--time_interval_type"
            , "-type"
            , help=f"Time interval type.\n {int_enum_enum_list_joined(enum=TimeIntervalType)}"),
        interval_value: int = typer.Option(
            ...
            , "--interval_value"
            , "-value"
            , help="Number of intervals to set on all metric schedules.  If 0 use unschedule all metrics.")
):
    """Updates schedule for all metrics in a warehouse."""
    api_conf = cli_api_conf_factory(bigeye_conf)
    client = CoreDatawatchClient(api_conf=api_conf)

    tit = TimeIntervalType(time_interval_type)

    wids: List[int] = [warehouse_id]

    # Could do bulk change by wid and metric type which are necessary in the api call.
    mcs: List[dict] = [mil['metricConfiguration']
                       for mil in client.get_metric_info_batch_post_dict(warehouse_ids=wids)]

    for mc in mcs:
        mc["scheduleFrequency"] = {
            "intervalType": tit.name,
            "intervalValue": interval_value
        }

        url = "/api/v1/metrics"

        response = client._call_datawatch(Method.POST, url=url, body=json.dumps(mc))


@app.command()
def set_metric_time(
        bigeye_conf: str = typer.Option(
            None
            , "--bigeye_conf"
            , "-b"
            , help="Bigeye Basic Auth Configuration File"),
        warehouse_id: int = typer.Option(
            None
            , "--warehouse_id"
            , "-wid"
            , help="Warehouse ID"),
        table_ids: Optional[List[int]] = typer.Option(
            None
            , "--table_id"
            , "-tid"
            , help="List of table IDs."),
        metric_column_names: Optional[List[str]] = typer.Option(
            ...
            , "--metric_column_name"
            , "-cn"
            , help="Possible metric column names.."),
        replace_set_metric_times: bool = typer.Option(
            False
            , "--replace"
            , "-r"
            , help="replace metric times if already present on tables?  Default is false."
        )
):
    """Sets metric times from a list of possible metric column names.  Can set for whole warehouse or for a list of
    table IDs."""
    api_conf = cli_api_conf_factory(bigeye_conf)
    client = CoreDatawatchClient(api_conf=api_conf)

    if warehouse_id and table_ids:
        raise Exception('Must include either table IDs OR warehouse id.')
    elif warehouse_id:
        client.set_source_metric_times(column_names=metric_column_names, wid=warehouse_id,
                                       replace=replace_set_metric_times)
    elif table_ids:
        client.set_table_metric_times(column_names=metric_column_names, table_ids=table_ids,
                                      replace=replace_set_metric_times)
    else:
        raise Exception('Must include either table IDs OR warehouse id.')


@app.command()
def unset_metric_time(
        bigeye_conf: str = typer.Option(
            None
            , "--bigeye_conf"
            , "-b"
            , help="Bigeye Basic Auth Configuration File"),
        warehouse_id: int = typer.Option(
            None
            , "--warehouse_id"
            , "-wid"
            , help="Warehouse ID"),
        table_ids: Optional[List[int]] = typer.Option(
            None
            , "--table_id"
            , "-tid"
            , help="List of table IDs.")
):
    """Unsets metric times for whole warehouse or for a list og table IDs."""
    api_conf = cli_api_conf_factory(bigeye_conf)
    client = CoreDatawatchClient(api_conf=api_conf)

    if warehouse_id and table_ids:
        raise Exception('Must include either table IDs OR warehouse id.')
    elif warehouse_id:
        client.unset_source_metric_times(wid=warehouse_id)
    elif table_ids:
        client.unset_table_metric_times(table_ids=table_ids)
    else:
        raise Exception('Must include either table IDs OR warehouse id.')


@app.command()
def get_metric_queries(
        bigeye_conf: str = typer.Option(
            None
            , "--bigeye_conf"
            , "-b"
            , help="Bigeye Basic Auth Configuration File"),
        warehouse_id: int = typer.Option(
            None
            , "--warehouse_id"
            , "-wid"
            , help="Warehouse ID"),
        schema_names: Optional[List[str]] = typer.Option(
            None
            , "--schema_name"
            , "-sn"
            , help="List of Schema Names.  E.g. -sn schema_1 -sn schema_2."),

        table_ids: Optional[List[int]] = typer.Option(
            None
            , "--table_id"
            , "-tid"
            , help="Table IDs.  E.g. -tid 123 -tid 124"),
        output_path: str = typer.Option(
            ...
            , "--output_path"
            , "-op"
            , help="File to write the failed metric configurations to.")
):
    """Gets the debug queries for all metrics by warehouse id, schema names, or table ids."""
    api_conf = cli_api_conf_factory(bigeye_conf)
    client = CoreDatawatchClient(api_conf=api_conf)

    mil: MetricInfoList = client.get_metric_info_batch_post(warehouse_ids=[warehouse_id],
                                                            table_ids=table_ids)
    if schema_names:
        mil.metrics = [m for m in mil.metrics if m.metric_metadata.schema_name in schema_names]

    mids = [m.metric_configuration.id for m in mil.metrics]

    r = client.get_debug_queries(metric_ids=mids)

    write_debug_queries(output_path=output_path, queries=r)

