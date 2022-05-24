from collections import defaultdict

import click
from rich.console import Console

from grid import get_instance_types
from grid.cli import rich_click
from grid.cli.observables import BaseObservable
from grid.sdk import env
from grid.sdk.rest.exceptions import GridException
from grid.cli.cli.grid_run import _aws_node_to_nickname


@rich_click.command('instance-types')
@click.option(
    '--cluster',
    'cluster_id',
    type=str,
    required=False,
    default=env.CONTEXT,
    help='Cluster ID whence the instance types needs to be fetched. (Bring Your Own Cloud Customers Only).'
)
def instance_types(cluster_id: str):
    """List the compute node instance types which are available for computation.

    For bring your own cloud customers, the instance types available are
    defined by the organizational administrators who created the cluster.
    """
    try:
        instances = get_instance_types(cluster_id=cluster_id)
    except GridException as e:
        raise click.ClickException(str(e))
    except Exception as e:
        raise click.ClickException(f"Could not fetch instance types: {e}")

    instance_dict = defaultdict(dict)
    table = BaseObservable.create_table(
        columns=['Instance Type', 'On-demand Cost', 'Spot Cost', 'CPU', 'GPU', 'Memory', 'Accelerator']
    )

    for i in instances:
        if i.spot:
            instance_dict[i.name]['spot_cost'] = i.hourly_cost
        else:
            instance_dict[i.name]['on_demand_cost'] = i.hourly_cost
        # these fields shouldn't be different for spot/on-demand
        instance_dict[i.name]['cpu'] = i.cpu
        instance_dict[i.name]['gpu'] = i.gpu
        instance_dict[i.name]['memory'] = i.memory

    for name, det in instance_dict.items():
        on_demand_cost = str(det.get('on_demand_cost') or "Not Available")
        spot_cost = str(det.get('spot_cost') or "Not Available")
        # We'll extract accelerator type from nickname
        nickname = _aws_node_to_nickname().get(name)
        accelerator = "" if nickname is None else nickname.split('_')[1]
        table.add_row(name, on_demand_cost, spot_cost, det['cpu'], det['gpu'], det['memory'], accelerator)
    console = Console()
    console.print(table)
