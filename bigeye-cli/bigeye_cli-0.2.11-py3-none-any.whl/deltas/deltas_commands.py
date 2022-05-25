from typing import Optional, List

import typer

from bigeye_cli.functions import cli_api_conf_factory
from bigeye_sdk.client.datawatch_client import CoreDatawatchClient
from bigeye_sdk.generated.com.torodata.models.generated import PredefinedMetricName
from bigeye_sdk.log import get_logger
from bigeye_sdk.model.enums import SimpleMetricType

log = get_logger(__file__)

app = typer.Typer(help='Deltas Commands for Bigeye CLI')


@app.command()
def create_delta(
        bigeye_conf: str = typer.Option(
            None
            , "--bigeye_conf"
            , "-b"
            , help="Bigeye Basic Auth Configuration File"),
        name: str = typer.Option(
            ...
            , "--delta_name"
            , "-n"
            , help="Name of delta."),
        source_table_id: int = typer.Option(
            ...
            , "--source_table_id"
            , "-sid"
            , help="Source Table ID"),
        target_table_id: int = typer.Option(
            ...
            , "--target_table_id"
            , "-tid"
            , help="Target Table ID"),
        metrics_to_enable: Optional[List[str]] = typer.Option(
            None
            , "--metric_name"
            , "-m"
            , help=f"List of predefined metric names to enable for the delta."
                   f"{', '.join([i.name for i in PredefinedMetricName])}"),
        source_filters: Optional[List[str]] = typer.Option(
            None
            , "--source_filter"
            , "-sf"
            , help=f"Filters to apply to the source table."),
        target_filters: Optional[List[str]] = typer.Option(
            None
            , "--target_filter"
            , "-tf"
            , help=f"Filters to apply to the target table.")
):
    """Creates a delta between two tables.  Enforces 1:1 column comparisons by case-insensitive column names.  Will
    search and replace by name."""
    api_conf = cli_api_conf_factory(bigeye_conf)
    client = CoreDatawatchClient(api_conf=api_conf)

    log.info('Looking for existing Delta with same name.')
    existing_deltas = client.get_delta_information(delta_ids=[])

    filtered = [d for d in existing_deltas if d.comparison_table_configuration.name == name]
    if filtered:
        log.info('Delta found.  Deleting existing Delta.')
        client.delete_delta(comparison_table_id=filtered[0].comparison_table_configuration.id)

    log.info('Creating new Delta.')
    mts = [SimpleMetricType.PREDEFINED.factory(m) for m in metrics_to_enable]
    client.create_delta(name=name, source_table_id=source_table_id, target_table_id=target_table_id,
                        metrics_to_enable=mts, source_filters=source_filters, target_filters=target_filters)


@app.command()
def run_delta(
        bigeye_conf: str = typer.Option(
            None
            , "--bigeye_conf"
            , "-b"
            , help="Bigeye Basic Auth Configuration File"),
        delta_id: int = typer.Option(
            ...
            , "--delta_id"
            , "-did"
            , help="Id of delta.")
):
    """Runs a delta by Delta ID."""
    print("Running a Delta now ... ")
    api_conf = cli_api_conf_factory(bigeye_conf)
    client = CoreDatawatchClient(api_conf=api_conf)
    client.run_a_delta(delta_id=delta_id)


# Renee work create_deltas_between_schemas
# @app.command()
# def create_deltas_between_schemas(
#         bigeye_conf: str = typer.Option(
#             ...
#             , "--bigeye_conf"
#             , "-b"
#             , help="Bigeye Basic Auth Configuration File"),
#         source_warehouse_id: int = typer.Option(
#             ...
#             , "--source_warehouse_id"
#             , "-swhid"
#             , help="Source warehouse ID"),
#         source_schema_name: str = typer.Option(
#                     ...
#                     , "--source_schema_name"
#                     , "-sschema"
#                     , help="Source schema name"),
#         target_warehouse_id: int = typer.Option(
#             ...
#             , "--target_warehouse_id"
#             , "-twhid"
#             , help="Target warehouse ID"),
#         target_schema_name: str = typer.Option(
#                             ...
#                             , "--target_schema_name"
#                             , "-tschema"
#                             , help="target schema name"),
# ):
#     #bigeye_conf = '/Users/reneeliu/.bigeye/conf/renee_quadpay.conf'
#     api_conf = cli_api_conf_factory(bigeye_conf)
#     client = CoreDatawatchClient(api_conf=api_conf)
#
#     source_list = client.get_tables(warehouse_id=[source_warehouse_id], schema=[source_schema_name])
#     target_list = client.get_tables(warehouse_id=[target_warehouse_id], schema=[target_schema_name])
#
#     source_names_dict = {}
#     target_names_dict = {}
#
#     # refactor get_list_tablenames
#     for s in source_list.tables:
#         source_names_dict[s.name] = s.id
#
#     for t in target_list.tables:
#         target_names_dict[t.name] = t.id
#
#     # TODO: need to import this function from a place
#     table_pairs = create_tablename_pairs(source_names_dict.keys(), target_names_dict.keys())
#
#     for t_pair in table_pairs:
#         source_t_id = source_names_dict[t_pair[0]]
#         print('source table id: ' + str(source_t_id))
#         target_t_id = target_names_dict[t_pair[1]]
#         print('target table id: ' + str(target_t_id))
#         x = client.create_delta("Bigeye testing " + S_SCHEMA_NAME + " ." + t_pair[0] + " "
#                                 + emoji.emojize(':magnifying_glass_tilted_right:') + " " + T_SCHEMA_NAME + " ." +
#                                 t_pair[1], source_t_id, target_t_id)
#         delta_id = x.comparison_table_configuration.id
#         client.run_a_delta(delta_id)
