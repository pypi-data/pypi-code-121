import logging

import click
import yaml

from edos.cli.common import cluster_id_completion
from edos.services.database_service import DatabaseService

LOG = logging.getLogger(__name__)


@click.group()
def cluster():
    """Database cluster management"""


@cluster.command()
def ls():
    """List clusters - IDs and names"""
    cluster_dict = DatabaseService().get_clusters()
    for key, value in cluster_dict.items():
        click.echo(f"{key} - {value}")


@cluster.command()
@click.argument("cluster_id", shell_complete=cluster_id_completion)
def inspect(cluster_id: str):
    """Inspect cluster"""
    cl = DatabaseService().get_cluster(cluster_id)
    cl_dict = {
        "id": cl.id,
        "name": cl.name,
        "status": cl.status,
        "engine": cl.engine,
        "version": cl.version,
        "size": cl.size,
        "tags": cl.tags,
        "databases": [db.name for db in cl.db_names]
        if cl.db_names is not None
        else "N/A",
        "users": [user.name for user in cl.users] if cl.users is not None else "N/A",
    }
    click.echo_via_pager(
        yaml.dump(cl_dict, indent=4, sort_keys=False, default_flow_style=False)
    )
