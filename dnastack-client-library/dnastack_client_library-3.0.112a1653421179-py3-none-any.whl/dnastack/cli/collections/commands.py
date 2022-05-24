import re

import click
from typing import Optional, Any, Dict

from .local_client_repository import LocalClientRepository
from ..dataconnect.helper import handle_query
from ..exporter import normalize, to_json, display_result_iterator
from ..utils import command, ArgumentSpec, echo_header
from ...common.logger import get_logger
from ...helpers.collections import switch_to_data_connect


@click.group("collections")
def collection_command_group():
    """ Interact with Collection Service or Explorer Service (e.g., Viral AI) """


@command(collection_command_group, 'list')
def list_collections(endpoint_id: str):
    """ List collections """
    click.echo(to_json(normalize(LocalClientRepository.get(endpoint_id).list_collections())))


@command(collection_command_group,
         specs=[
             ArgumentSpec(
                 name='collection',
                 arg_names=['--collection', '-c'],
                 as_option=True,
                 help='The ID or slug name of the target collection; required only by an explorer service',
             ),
             ArgumentSpec(
                 name='limit',
                 arg_names=['--limit', '-l'],
                 as_option=True,
                 help='The maximum number of items to display',
             )
         ])
def list_items(endpoint_id: Optional[str],
               collection: str,
               limit: Optional[int] = 50):
    """ List items of the given collection """
    logger = get_logger('CLI/list-items')
    limit_override = False

    limit = int(limit)

    collection_service_client = LocalClientRepository.get(endpoint_id)
    actual_collection = collection_service_client.get(collection)
    data_connect_client = switch_to_data_connect(collection_service_client, actual_collection.slugName)
    items_query = actual_collection.itemsQuery.strip()

    if re.search(r' limit\s*\d+$', items_query, re.IGNORECASE):
        logger.warning('The items query already has the limit defined and the CLI will not override that limit.')
    else:
        logger.debug(f'Only shows {limit} row(s)')
        limit_override = True
        items_query = f'{items_query} LIMIT {limit + 1}'  # We use +1 as an indicator whether there are more results.

    def __simplify_item(row: Dict[str, Any]) -> Dict[str, Any]:
        # NOTE: It is implemented this way to guarantee that "id" and "name" are more likely to show first.
        property_names = ['type', 'size', 'size_unit', 'version', 'item_updated_at']

        item = dict(
            id=row['id'],
            name=row.get('qualified_table_name') or row['preferred_name'],
        )

        if row['type'] == 'blob':
            property_names.extend([
                'checksums',
                'metadata_url',
                'mime_type',
            ])
        elif row['type'] == 'table':
            property_names.extend([
                'json_schema',
            ])

        item.update({
            k: v
            for k, v in row.items()
            if k in property_names
        })

        return item

    row_count = display_result_iterator(data_connect_client.query(items_query), __simplify_item, limit)

    click.secho(f'Displayed {row_count} item{"s" if row_count != 1 else ""} from this collection',
                fg='green',
                err=True)

    if limit_override:
        click.secho(f'There exists more than {limit} item{"s" if row_count != 1 else ""} in this collection.',
                    fg='blue',
                    err=True)


@command(collection_command_group,
         'query',
         [
             ArgumentSpec(
                 name='collection',
                 arg_names=['--collection', '-c'],
                 as_option=True,
                 help='The ID or slug name of the target collection; required only by an explorer service',
             ),
             ArgumentSpec(
                 name='format',
                 arg_names=["-f", "--format"],
                 as_option=True,
                 help='Output format',
                 choices=["json", "csv"],
             ),
             ArgumentSpec(
                 name='decimal_as',
                 arg_names=['--decimal-as'],
                 as_option=True,
                 help='The format of the decimal value',
                 choices=["string", "float"],
             ),
         ])
def query_collection(endpoint_id: Optional[str],
                     collection: Optional[str],
                     query: str,
                     format: str = 'json',
                     decimal_as: str = 'string'):
    """ Query data """
    client = switch_to_data_connect(LocalClientRepository.get(endpoint_id), collection)
    return handle_query(client, query, format, decimal_as)


@click.group("tables")
def table_command_group():
    """ Data Client API for Collections """


@command(table_command_group,
         'list',
         [
             ArgumentSpec(
                 name='collection',
                 arg_names=['--collection', '-c'],
                 as_option=True,
                 help='The ID or slug name of the target collection; required only by an explorer service',
             ),
         ])
def list_tables(endpoint_id: str, collection: Optional[str]):
    """ List all accessible tables """
    client = switch_to_data_connect(LocalClientRepository.get(endpoint_id), collection)
    click.echo(to_json([t.dict() for t in client.list_tables()]))


# noinspection PyTypeChecker
collection_command_group.add_command(table_command_group)
