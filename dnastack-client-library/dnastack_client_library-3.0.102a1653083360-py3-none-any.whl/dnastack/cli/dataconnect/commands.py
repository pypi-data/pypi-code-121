import click
from typing import Optional

from .helper import handle_query
from .local_client_repository import LocalClientRepository
from ..exporter import to_json
from ..utils import command, ArgumentSpec


@click.group("dataconnect")
def data_connect_command_group():
    """ Interact with Data Connect Service """


@command(data_connect_command_group,
         'query',
         [
             ArgumentSpec(
                 name='output',
                 arg_names=['-o', '--output'],
                 as_option=True,
                 help="""
                    The path to the output file (Note: If the option is specified, there will be no output to stdout.)
                 """,
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
def data_connect_query(endpoint_id: Optional[str],
                       query: str,
                       output: Optional[str] = None,
                       format: str = "json",
                       decimal_as: str = 'string'):
    """ Perform a search query """
    return handle_query(LocalClientRepository.get(endpoint_id),
                        query,
                        format,
                        decimal_as,
                        output_file=output)


@click.group("tables")
def table_command_group():
    """ Table API commands """


@command(table_command_group, 'list')
def list_tables(endpoint_id: str):
    """ List all accessible tables """
    click.echo(to_json([t.dict() for t in LocalClientRepository.get(endpoint_id).list_tables()]))


@command(table_command_group, 'get')
def get_table_info(endpoint_id: str, table_name: str):
    """ Get data from the given table """
    click.echo(to_json(LocalClientRepository.get(endpoint_id).table(table_name).info.dict()))


# noinspection PyTypeChecker
data_connect_command_group.add_command(table_command_group)
