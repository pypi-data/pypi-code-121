from email.policy import default
import os
import click
import re

from ecsctrl.loader import VarsLoader

from .boto_client import BotoClient
from .yaml_converter import yaml_file_to_dict

from .service_updater import ServiceUpdater, WaitForUpdate


def check_var(ctx, param, value):
    for v in value:
        if not re.match("^[^=]+=.*$", v):
            raise click.BadParameter(
                f"'{v}'. Variable has to be in format variable=value"
            )
    return value


@click.group()
@click.pass_context
def cli(ctx):
    ctx.ensure_object(dict)
    ctx.obj["boto_client"] = BotoClient("ecs")


@cli.group(name="task-definition")
@click.pass_context
def task_definition(ctx):
    pass


# fmt: off
@task_definition.command()
@click.argument("spec-file", type=str)
@click.option("--env-file", "-e", multiple=True, type=str, help="Path to env-style file with variables")
@click.option("--json-file", "-j", multiple=True, type=str, help="Path to json file with variable")
@click.option("--var", "-v", multiple=True, type=str, callback=check_var, help="Single variable in format name=value")
@click.option("--sys-env/--no-sys-env", is_flag=True, default=False, help="Uses system env as a source for template variables")
@click.option("--update-services-in-cluster", "-c", multiple=True, type=str, help="Updates all services deployed with this task in a particular cluster")
@click.option("--wait-for-update", "-w", is_flag=True, help="Waits for services to finish update")
@click.pass_context
# fmt: on
def register(
    ctx,
    spec_file,
    env_file,
    json_file,
    var,
    sys_env,
    update_services_in_cluster,
    wait_for_update,
):
    vars = VarsLoader(env_file, var, json_file, sys_env).load()
    spec = yaml_file_to_dict(spec_file, vars)
    task_family = spec.get("family", "N/A")
    print(f"🗂 Registering task definition {task_family}.")
    response = ctx.obj["boto_client"].call("register_task_definition", **spec)
    task_definition_arn = response["taskDefinition"]["taskDefinitionArn"]
    print(f"\t✅ done, task definition arn: {task_definition_arn}.")

    if update_services_in_cluster:
        updated_services = {}

        for cluster_name in update_services_in_cluster:
            updater = ServiceUpdater(
                ctx.obj["boto_client"], task_definition_arn, cluster_name
            )
            updated_services_in_cluster = updater.update()
            updated_services[cluster_name] = updated_services_in_cluster

        if wait_for_update:
            waiter = WaitForUpdate(ctx.obj["boto_client"], updated_services)
            waiter.wait_for_all()


@cli.group(name="service")
@click.pass_context
def service(ctx):
    pass


# fmt: off
@service.command()
@click.argument("spec-file", type=str)
@click.option("--env-file", "-e", multiple=True, type=str, help="Path to env-style file with variables")
@click.option("--json-file", "-j", multiple=True, type=str, help="Path to json file with variable")
@click.option("--var", "-v", multiple=True, type=str, callback=check_var, help="Single variable in format name=value")
@click.option("--sys-env/--no-sys-env", is_flag=True, default=False, help="Uses system env as a source for template variables")
@click.pass_context
# fmt: on
def create(ctx, spec_file, env_file, json_file, var, sys_env):
    vars = VarsLoader(env_file, var, json_file, sys_env).load()
    spec = yaml_file_to_dict(spec_file, vars)
    service_name = spec.get("name", "N/A")
    print(f"🏸 Creating service {service_name}.")
    ctx.obj["boto_client"].call("create_service", **spec)
    print("\t✅ done.")


# fmt: off
@service.command()
@click.argument("spec-file", type=str)
@click.option("--env-file", "-e", multiple=True, type=str, help="Path to env-style file with variables")
@click.option("--json-file", "-j", multiple=True, type=str, help="Path to json file with variable")
@click.option("--var", "-v", multiple=True, type=str, callback=check_var, help="Single variable in format name=value")
@click.option("--sys-env/--no-sys-env", is_flag=True, default=False, help="Uses system env as a source for template variables")
@click.pass_context
# fmt: on
def update(ctx, spec_file, env_file, json_file, var, sys_env):
    vars = VarsLoader(env_file, var, json_file, sys_env).load()
    spec = yaml_file_to_dict(spec_file, vars)
    service_name = spec.get("serviceName", "N/A")
    print(f"🏸 Updating service {service_name}.")
    ctx.obj["boto_client"].call("update_service", **spec)
    print("\t✅ done.")


@cli.group(name="secrets")
@click.pass_context
def secrets(ctx):
    pass


# fmt: off
@secrets.command()
@click.argument("spec-file", type=str)
@click.option("--env-file", "-e", multiple=True, type=str, help="Path to env-style file with variables")
@click.option("--json-file", "-j", multiple=True, type=str, help="Path to json file with variable")
@click.option("--var", "-v", multiple=True, type=str, callback=check_var, help="Single variable in format name=value")
@click.option("--sys-env/--no-sys-env", is_flag=True, default=False, help="Uses system env as a source for template variables")
@click.pass_context
# fmt: on
def store(ctx, spec_file, env_file, json_file, var, sys_env):
    vars = VarsLoader(env_file, var, json_file, sys_env).load()
    spec = yaml_file_to_dict(spec_file, vars)
    ssm = BotoClient("ssm", dry_run=ctx.obj["boto_client"].dry_run)

    for secret_name, value in spec.items():
        ssm_params = {
            "Name": secret_name,
            "Value": value,
            "Type": "SecureString",
        }
        print(f"🔑 Storing secret {secret_name}.")
        response = ssm.call("put_parameter", **ssm_params)
        print(f"\t✅ done, parameter version: {response['Version']}")
