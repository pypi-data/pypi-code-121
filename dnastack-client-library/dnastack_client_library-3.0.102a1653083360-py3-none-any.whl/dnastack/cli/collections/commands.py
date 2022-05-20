import click
from typing import Optional

from .local_client_repository import LocalClientRepository
from ..dataconnect.helper import handle_query
from ..exporter import normalize, to_json
from ..utils import command, ArgumentSpec
from ...helpers.collections import switch_to_data_connect


@click.group("collections")
def collection_command_group():
    """ Interact with Collection Service or Explorer Service (e.g., Viral AI) """


@command(collection_command_group, 'list')
def list_collections(endpoint_id: str):
    """ List collections """
    click.echo(to_json(normalize(LocalClientRepository.get(endpoint_id).list_collections())))


@command(collection_command_group,
         'query',
         [
             ArgumentSpec(
                 name='collection',
                 arg_names=['--collection'],
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
                 arg_names=['--collection'],
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
