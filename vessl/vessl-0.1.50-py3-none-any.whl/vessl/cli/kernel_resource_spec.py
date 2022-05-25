import click

from openapi_client import ResponseKernelResourceSpec
from vessl.cli._base import VesslGroup, vessl_argument, vessl_option
from vessl.cli._util import format_bool, print_data, print_table, prompt_choices
from vessl.cli.kernel_cluster import cluster_id_prompter
from vessl.cli.organization import organization_name_option
from vessl.kernel_resource_spec import (
    list_kernel_resource_specs,
    read_kernel_resource_spec,
)


def resource_name_prompter(
    ctx: click.Context, param: click.Parameter, value: str
) -> str:
    cluster = ctx.obj.get("cluster")
    if cluster is None:
        raise click.BadOptionUsage(
            option_name="--cluster",
            message="Cluster (`--cluster`) must be specified before resource (`--resource`).",
        )

    if ctx.params.get("processor_type") is None:
        resources = list_kernel_resource_specs(cluster_id=cluster.id)
        options = [(x.name, x) for x in resources]
        if cluster.provider != "VESSL":
            options.append(
                ("Custom", ResponseKernelResourceSpec(name="")),
            )

        resource = prompt_choices("Resource", options)
        if resource.processor_type is not None:
            ctx.obj["processor_type"] = resource.processor_type

        return resource.name


def resource_name_callback(
    ctx: click.Context, param: click.Parameter, value: str
) -> str:
    if "cluster" not in ctx.obj:
        raise click.BadOptionUsage(
            option_name="--cluster",
            message="Cluster (`--cluster`) must be specified before resource (`--resource`).",
        )

    cluster = ctx.obj.get("cluster")
    if value and "resource" not in ctx.obj:
        ctx.obj["resource"] = read_kernel_resource_spec(cluster.id, value)

    return value


@click.command(name="resource", cls=VesslGroup)
def cli():
    pass


@cli.vessl_command()
@vessl_argument(
    "cluster",
    type=click.INT,
    required=True,
    prompter=cluster_id_prompter,
)
@vessl_argument(
    "name", type=click.STRING, required=True, prompter=resource_name_prompter
)
@organization_name_option
def read(cluster: int, name: str):
    resource = read_kernel_resource_spec(
        cluster_id=cluster, kernel_resource_spec_name=name
    )
    print_data(
        {
            "ID": resource.id,
            "Name": resource.name,
            "Description": resource.description,
            "CPU Type": resource.cpu_type,
            "CPU Limit": resource.cpu_limit,
            "GPU Type": resource.gpu_type,
            "GPU Limit": resource.gpu_limit,
            "Memory Limit": resource.memory_limit,
            "Spot": format_bool(resource.spot),
        }
    )


@cli.vessl_command()
@vessl_argument(
    "cluster",
    type=click.INT,
    required=True,
    prompter=cluster_id_prompter,
)
@organization_name_option
def list(cluster: int):
    resources = list_kernel_resource_specs(cluster_id=cluster)
    print_table(
        resources,
        [
            "ID",
            "Name",
            "CPU Type",
            "CPU Limit",
            "GPU Type",
            "GPU Limit",
            "Memory Limit",
            "Spot",
        ],
        lambda x: [
            x.id,
            x.name,
            x.cpu_type,
            x.cpu_limit,
            x.gpu_type,
            x.gpu_limit,
            x.memory_limit,
            x.spot,
        ],
    )


resource_option = vessl_option(
    "-r",
    "--resource",
    type=click.STRING,
    prompter=resource_name_prompter,
    callback=resource_name_callback,
    help="Resource type to run experiment.",
)
