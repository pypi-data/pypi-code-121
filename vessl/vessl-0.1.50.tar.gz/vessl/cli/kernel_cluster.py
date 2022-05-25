import click

from vessl.cli._base import VesslGroup, vessl_argument, vessl_option
from vessl.cli._util import (
    format_string,
    generic_prompter,
    print_data,
    print_table,
    prompt_choices,
)
from vessl.cli.organization import organization_name_option
from vessl.kernel_cluster import (
    delete_cluster,
    list_cluster_nodes,
    list_clusters,
    read_cluster,
    rename_cluster,
)


def cluster_name_prompter(
    ctx: click.Context, param: click.Parameter, value: str
) -> str:
    clusters = list_clusters()
    return prompt_choices("Cluster", [x.name for x in clusters])


def custom_cluster_name_prompter(
    ctx: click.Context, param: click.Parameter, value: str
) -> str:
    clusters = list_clusters()
    clusters = [x for x in clusters if not x.is_savvihub_managed]
    return prompt_choices("Cluster", [x.name for x in clusters])


@click.command(name="cluster", cls=VesslGroup)
def cli():
    pass


@cli.vessl_command()
@vessl_argument(
    "name", type=click.STRING, required=True, prompter=cluster_name_prompter
)
@organization_name_option
def read(name: str):
    cluster = read_cluster(cluster_name=name)
    print_data(
        {
            "ID": cluster.id,
            "Name": cluster.name,
            "Type": "Managed" if cluster.is_savvihub_managed else "Custom",
            "Region": format_string(cluster.region),
            "Status": cluster.status.replace("-", " "),
            "K8s Master Endpoint": format_string(cluster.name),
            "K8s Namespace": format_string(cluster.kubernetes_namespace),
            "K8s Service Type": cluster.kubernetes_service_type,
        }
    )


@cli.vessl_command()
@organization_name_option
def list():
    clusters = list_clusters()
    print_table(
        clusters,
        ["ID", "Name", "Type", "Status", "K8s Master Endpoint", "K8s Namespace"],
        lambda x: [
            x.id,
            x.name,
            "Managed" if x.is_savvihub_managed else "Custom",
            x.status.replace("-", " "),
            format_string(x.name),
            format_string(x.kubernetes_namespace),
        ],
    )


@cli.vessl_command()
@vessl_argument(
    "name", type=click.STRING, required=True, prompter=custom_cluster_name_prompter
)
@organization_name_option
def delete(name: str):
    click.confirm(f"Are you sure you want to delete '{name}'?", abort=True)
    cluster = read_cluster(cluster_name=name)
    data = delete_cluster(cluster_id=cluster.id)
    print(f"Deleted '{name}'.")


@cli.vessl_command()
@vessl_argument(
    "name", type=click.STRING, required=True, prompter=custom_cluster_name_prompter
)
@vessl_argument(
    "new_name", type=click.STRING, required=True, prompter=generic_prompter("New name")
)
@organization_name_option
def rename(name: str, new_name: str):
    cluster = read_cluster(cluster_name=name)
    cluster = rename_cluster(cluster_id=cluster.id, new_cluster_name=new_name)
    print(f"Renamed '{name}' to '{cluster.name}'.")


@cli.vessl_command()
@vessl_argument(
    "name", type=click.STRING, required=True, prompter=custom_cluster_name_prompter
)
@organization_name_option
def list_nodes(name: str):
    cluster = read_cluster(cluster_name=name)
    cluster_nodes = list_cluster_nodes(cluster_id=cluster.id)
    print_table(
        cluster_nodes,
        ["ID", "Name", "CPU Limits", "GPU Limits", "Memory Limits"],
        lambda x: [x.id, x.name, x.cpu_limits, x.gpu_limits, x.memory_limits],
    )


def cluster_id_prompter(ctx: click.Context, param: click.Parameter, value: str) -> int:
    clusters = list_clusters()
    cluster = prompt_choices(
        "Cluster",
        [(f"{x.name}", x) for x in clusters],
    )
    ctx.obj["cluster"] = cluster
    return cluster.id


def cluster_name_prompter(
    ctx: click.Context, param: click.Parameter, value: str
) -> str:
    clusters = list_clusters()
    cluster = prompt_choices(
        "Cluster",
        [(f"{x.name}", x) for x in clusters],
    )
    ctx.obj["cluster"] = cluster
    return cluster.name


def cluster_name_callback(
    ctx: click.Context, param: click.Parameter, value: str
) -> str:
    if "cluster" not in ctx.obj:
        ctx.obj["cluster"] = read_cluster(value)
    return value


cluster_option = vessl_option(
    "-c",
    "--cluster",
    type=click.STRING,
    required=True,
    prompter=cluster_name_prompter,
    callback=cluster_name_callback,
    help="Must be specified before resource-related options (`--resource`, `--processor`, ...).",
)
