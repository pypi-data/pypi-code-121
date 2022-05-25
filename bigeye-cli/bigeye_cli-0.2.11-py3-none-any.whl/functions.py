import os
from dataclasses import asdict
from typing import List

from bigeye_sdk.model.protobuf_extensions import MetricDebugQueries

from bigeye_sdk.generated.com.torodata.models.generated import MetricInfoList, Issue, Table, GetDebugQueriesResponse

from bigeye_sdk.functions.metric_functions import get_file_name_for_metric
from bigeye_sdk.functions.file_functs import create_subdir_if_not_exists, serialize_listdict_to_json_file

from bigeye_sdk.log import get_logger
from bigeye_sdk.model.api_credentials import BasicAuthRequestLibApiConf

log = get_logger(__file__)


def cli_api_conf_factory(api_conf_file: str = None) -> BasicAuthRequestLibApiConf:
    """
    TODO: Think about defining a factory abc in SDK?  Or tie into datawatch client factory.
    Args:
        api_conf_file: file containing the api_conf.  If none will look for environment var BIGEYE_API_CRED_FILE

    Returns: an ApiConf workspace.

    """
    environ_api_conf_file = os.environ['BIGEYE_API_CRED_FILE']
    if api_conf_file:
        return BasicAuthRequestLibApiConf.load_api_conf(api_conf_file)
    elif environ_api_conf_file:
        return BasicAuthRequestLibApiConf.load_api_conf(environ_api_conf_file)
    else:
        raise Exception('No credential file passed and BIGEYE_API_CRED_FILE environment variable not set.')


def write_metric_info(output_path: str, metrics: MetricInfoList,
                      file_name: str = None, only_metric_conf: bool = False):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    for metric in metrics.metrics:
        """Writes individual metrics to files in the output path."""
        mc = metric.metric_configuration
        md = metric.metric_metadata

        if only_metric_conf:
            datum = mc
            log.info('Persisting metric configurations.')
        else:
            datum = metric
            log.info('Persisting metric info.')

        if not file_name:
            subpath = f"{output_path}/metric_info/warehouse_id-{md.warehouse_id}"

            create_subdir_if_not_exists(path=subpath)
            fn = get_file_name_for_metric(metric)
            url = f'{subpath}/{fn}'
        else:
            url = f'{output_path}/metric_info/{file_name}'

        serialize_listdict_to_json_file(url=url,
                                        data=[datum.to_dict()])


def write_debug_queries(output_path: str, queries: List[MetricDebugQueries], file_name: str = None,
                        only_metric_conf: bool = False):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    for q in queries:
        if not file_name:
            subpath = f"{output_path}/debug_queries"

            create_subdir_if_not_exists(path=subpath)
            fn = f'{q.metric_id}.json'
            url = f'{subpath}/{fn}'
        else:
            url = f'{output_path}/debug_queries/{file_name}'

        serialize_listdict_to_json_file(url=url,
                                        data=[asdict(q)])


def write_table_info(output_path: str, tables: List[Table], file_name: str = None):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    for table in tables:
        """Writes individual issues to files in the output path."""
        log.info('Persisting issue.')
        if not file_name:
            subpath = f"{output_path}/table_info/warehouse_id-{table.warehouse_id}"

            create_subdir_if_not_exists(path=subpath)
            fn = f'{table.id}-{table.schema_name}-{table.name}.json'
            url = f'{subpath}/{fn}'
        else:
            url = f'{output_path}/{file_name}'

        serialize_listdict_to_json_file(url=url,
                                        data=[table.to_dict()])


def write_issue_info(output_path: str, issues: List[Issue], file_name: str = None):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    for issue in issues:
        """Writes individual issues to files in the output path."""
        log.info('Persisting issue.')
        if not file_name:
            subpath = f"{output_path}/issue_info/warehouse_id-{issue.metric_configuration.warehouse_id}" \
                      f"/dataset_id-{issue.metric_configuration.dataset_id}" \
                      f"/{issue.metric_configuration.name.replace(' ', '_')}"

            create_subdir_if_not_exists(path=subpath)
            fn = f'{issue.id}-{issue.name}.json'
            url = f'{subpath}/{fn}'
        else:
            url = f'{output_path}/{file_name}'

        serialize_listdict_to_json_file(url=url,
                                        data=[issue.to_dict()])
