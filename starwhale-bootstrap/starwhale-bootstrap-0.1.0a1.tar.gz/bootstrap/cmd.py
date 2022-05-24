import typing as t
from pathlib import Path

import click

# from starwhale.consts import DEFAULT_MODEL_YAML_NAME
# from starwhale.consts.env import SWEnv
from .swbs import deploy

@click.group("deploy", help="StarWhale Bootstrap deploy")
def bootstrap_cmd() -> None:
    pass

@bootstrap_cmd.command(
    "run", help="deploy starwhale to cluster"
)
#@click.argument("deploy")
@click.option(
    "-f",
    "--model-yaml",
    #default=DEFAULT_MODEL_YAML_NAME,
    #help="mode yaml filename, default use ${workdir}/model.yaml file",
)
@click.option(
    "--status-dir",
    #envvar=SWEnv.status_dir,
    #help=f"ppl status dir, env is {SWEnv.status_dir}",
)
@click.option(
    "--log-dir", #envvar=SWEnv.log_dir, help=f"ppl log dir, env is {SWEnv.log_dir}"
)
@click.option(
    "--result-dir",
    #envvar=SWEnv.result_dir,
    #help=f"ppl result dir, env is {SWEnv.result_dir}",
)
@click.option(
    "--input-config",
    #envvar=SWEnv.input_config,
    #help=f"ppl swds config.json path, env is {SWEnv.input_config}",
)
def _deploy(
    model_yaml: str,
    status_dir: str,
    log_dir: str,
    result_dir: str,
    input_config: str,
) -> None:
    deploy()
