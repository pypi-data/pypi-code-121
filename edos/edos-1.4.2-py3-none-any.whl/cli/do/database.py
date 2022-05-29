import logging
import os
import uuid
from datetime import datetime

import click

from edos.cli.common import cluster_id_completion
from edos.exceptions import UserReadableException
from edos.services.database_service import DatabaseService

LOG = logging.getLogger(__name__)


@click.group()
def database():
    """Managing Digital Ocean databases"""


@database.command()
@click.argument("cluster_id", shell_complete=cluster_id_completion)
def ls(cluster_id):
    """command to get databases in certain cluster"""
    service = DatabaseService()
    databases = service.get_databases(cluster_id)
    for db in databases:
        click.echo(db)


@database.command()
@click.argument("cluster_id", shell_complete=cluster_id_completion)
@click.argument("name")
def create(cluster_id, name):
    """command for create a database in certain cluster"""
    service = DatabaseService()
    if not click.confirm(
        f"Are you sure, that you want to create {name} "
        f"database in {cluster_id} cluster?"
    ):
        return click.echo("creation cancelled")

    db_url = service.create_database(cluster_id, name)
    click.echo(f'DB url =>     "{db_url}"')


@database.command()
@click.argument("cluster_id", shell_complete=cluster_id_completion, type=str)
@click.argument("db_name", type=str)
@click.argument("db_user", type=str, required=False)
def dump(cluster_id, db_name, db_user):
    """
    command for create db snapshot and save it into yours /tmp,
    db_user is optional (default is db_name)
    """
    service = DatabaseService()
    cluster = service.get_cluster(cluster_id)
    _user = db_user if db_user else db_name
    user = service.get_database_user(cluster.id, _user)
    server_dumpfile_name = f"dump_{uuid.uuid4()}.sql"
    if cluster.engine == "pg":
        dump_command = (
            f"ssh swarm1 'PGPASSWORD={user.password} pg_dump -U "
            f"{user.name} -h {cluster.privateConnection.host} -p "
            f"{cluster.privateConnection.port} -d {db_name} > "
            f"/tmp/{server_dumpfile_name}'"
        )
    elif cluster.engine == "mysql":
        dump_command = (
            f"ssh swarm1 'mysqldump -u {user.name} -p {user.password} "
            f"-h {cluster.privateConnection.host} -P {cluster.privateConnection.port} "
            f"{db_name} > /tmp/{server_dumpfile_name}'"
        )
    else:
        raise UserReadableException(
            "Bad cluster. Only PG and Mysql clusters are supported"
        )
    timestamp: str = str(datetime.now().timestamp())
    local_filename = f"{db_name}_{timestamp}.sql"
    copy_command = f"scp swarm1:/tmp/{server_dumpfile_name} /tmp/{local_filename}"
    remove_command = f"ssh swarm1 rm /tmp/{server_dumpfile_name}"
    click.echo("Dumping database")
    os.system(dump_command)
    os.system(copy_command)
    os.system(remove_command)
    click.echo(
        f"Database was successfully dumped. You can find it in "
        f"your /tmp/{local_filename}"
    )


# @database.command()
# @click.argument('cluster_id')
# @click.argument('name')
# def recreate(cluster_id, name):
#     """command for recreate database
#     (when it needs to be dropped and created again)"""
#     service = DatabaseService()
#     if not confirm_action(f"Are you sure, that you want to
#     recreate {name} database in {cluster_id} cluster?"):
#         return click.echo('recreatin cancelled')
#     service.recreate_database(cluster_id, name)
#     return click.echo('successfully recreated database')
