from datetime import datetime
from typing import List

import click

from openapi_client import ResponseSimpleModelInfo
from vessl import list_experiment_output_files, list_experiments
from vessl.cli._base import VesslGroup, vessl_argument, vessl_option
from vessl.cli._util import (
    Endpoint,
    format_size,
    format_url,
    generic_prompter,
    print_data,
    print_table,
    print_volume_files,
    prompt_checkbox,
    prompt_choices,
    truncate_datetime,
)
from vessl.cli.dataset import download_dest_path_prompter
from vessl.cli.organization import organization_name_option
from vessl.cli.project import project_name_option
from vessl.experiment import read_experiment_by_id
from vessl.model import (
    create_model,
    create_model_repository,
    delete_model_volume_file,
    download_model_volume_file,
    list_model_repositories,
    list_model_volume_files,
    list_models,
    read_model,
    read_model_repository,
    upload_model_volume_file,
)
from vessl.util.constant import MODEL_SOURCE_EXPERIMENT, MODEL_SOURCE_LOCAL


def model_repository_status(latest_model: ResponseSimpleModelInfo) -> str:
    if latest_model:
        return latest_model.status
    return "Empty repository"


def model_repository_update_dt(
    latest_model: ResponseSimpleModelInfo, default: datetime
) -> datetime:
    if latest_model:
        return truncate_datetime(latest_model.created_dt)
    return truncate_datetime(default)


def model_repository_name_callback(
    ctx: click.Context, param: click.Parameter, value: str
) -> str:
    if value:
        ctx.obj["repository"] = value
    return value


def model_repository_name_prompter(
    ctx: click.Context,
    param: click.Parameter,
    value: str,
) -> str:
    model_repositories = list_model_repositories()
    if len(model_repositories) == 0:
        raise click.UsageError(
            message="Create model repository with `vessl model-repository create`"
        )
    repository = prompt_choices(
        "Model repository", [x.name for x in model_repositories]
    )
    ctx.obj["repository"] = repository
    return repository


@click.command(name="model-repository", cls=VesslGroup)
def model_repository_cli():
    pass


@model_repository_cli.vessl_command()
@vessl_argument(
    "name", type=click.STRING, required=True, prompter=model_repository_name_prompter
)
@organization_name_option
def read(name: str):
    model_repository = read_model_repository(repository_name=name)
    print_data(
        {
            "ID": model_repository.id,
            "Name": model_repository.name,
            "Description": model_repository.description,
            "Status": model_repository_status(
                model_repository.model_summary.latest_model
            ),
            "Organization": model_repository.organization.name,
            "Created": truncate_datetime(model_repository.created_dt),
            "Updated": truncate_datetime(model_repository.updated_dt),
        }
    )
    print(
        f"For more info: {format_url(Endpoint.model_repository.format(model_repository.organization.name, model_repository.name))}"
    )


@model_repository_cli.vessl_command()
@organization_name_option
def list():
    model_repositories = list_model_repositories()
    print_table(
        model_repositories,
        ["Name", "Status", "Models", "Created", "Updated"],
        lambda x: [
            x.name,
            model_repository_status(x.model_summary.latest_model),
            x.model_summary.total,
            truncate_datetime(x.created_dt),
            model_repository_update_dt(x.model_summary.latest_model, x.updated_dt),
        ],
    )


@model_repository_cli.vessl_command()
@vessl_argument(
    "name",
    type=click.STRING,
    required=True,
    prompter=generic_prompter("Model repository name"),
)
@click.option("-m", "--description", type=click.STRING)
@organization_name_option
def create(
    name: str,
    description: str,
):
    model_repository = create_model_repository(
        name=name,
        description=description,
    )
    print(
        f"Created '{model_repository.name}'.\n"
        f"For more info: {format_url(Endpoint.model_repository.format(model_repository.organization.name, model_repository.name))}"
    )


def model_number_prompter(
    ctx: click.Context,
    param: click.Parameter,
    value: int,
) -> int:
    repository = ctx.obj.get("repository")
    if repository is None:
        raise click.BadArgumentUsage(
            message="Argument `REPOSITORY_NAME` must be specified before `MODEL_NUMBER`.",
        )
    models = list_models(repository_name=repository)
    return prompt_choices("Model", [x.number for x in models])


@click.command(name="model", cls=VesslGroup)
def model_cli():
    pass


@model_cli.vessl_command()
@vessl_argument(
    "repository_name",
    type=click.STRING,
    required=True,
    prompter=model_repository_name_prompter,
    callback=model_repository_name_callback,
)
@vessl_argument(
    "model_number",
    type=click.INT,
    required=True,
    prompter=model_number_prompter,
)
@organization_name_option
def read(repository_name: str, model_number: int):
    model = read_model(repository_name=repository_name, model_number=model_number)
    experiment_numbers = []
    if model.experiment:
        experiment_numbers.append(model.experiment.number)

    metrics_summary = "None"
    if model.metrics_summary:
        metrics_keys = model.metrics_summary.latest.keys()
        metrics_summary = {}
        for key in metrics_keys:
            metrics_summary[key] = model.metrics_summary.latest[key].value

    print_data(
        {
            "ID": model.id,
            "Number": model.number,
            "Name": model.name,
            "Status": model.status,
            "Related experiments": experiment_numbers,
            "Creator": model.created_by.username,
            "Created": truncate_datetime(model.created_dt),
            "Metrics summary": metrics_summary,
        }
    )
    print(
        f"For more info: {format_url(Endpoint.model.format(model.model_repository.organization.name, model.model_repository.name, model.number))}"
    )


@model_cli.vessl_command()
@vessl_argument(
    "repository",
    type=click.STRING,
    required=True,
    prompter=model_repository_name_prompter,
)
@organization_name_option
def list(repository: str):
    models = list_models(repository_name=repository)
    print_table(
        models,
        ["Number", "Created", "Status"],
        lambda x: [x.number, truncate_datetime(x.created_dt), x.status],
    )


@model_cli.vessl_command()
@vessl_argument(
    "repository_name",
    type=click.STRING,
    required=True,
    prompter=model_repository_name_prompter,
)
@vessl_argument(
    "model_number",
    type=click.INT,
    required=True,
    prompter=model_number_prompter,
)
@click.option("-p", "--path", type=click.Path(), default="", help="Defaults to root.")
@click.option("-r", "--recursive", is_flag=True)
@organization_name_option
def list_files(repository_name: str, model_number: int, path: str, recursive: bool):
    files = list_model_volume_files(
        repository_name=repository_name,
        model_number=model_number,
        need_download_url=False,
        path=path,
        recursive=recursive,
    )
    print_volume_files(files)


def model_source_prompter(
    ctx: click.Context,
    param: click.Parameter,
    value: str,
) -> str:
    return prompt_choices(
        "Source",
        [
            ("From an experiment", MODEL_SOURCE_EXPERIMENT),
            ("From local files", MODEL_SOURCE_LOCAL),
        ],
    )


def model_source_callback(
    ctx: click.Context,
    param: click.Parameter,
    value: str,
):
    if value:
        ctx.obj["model_source"] = value
    return value


def experiment_id_prompter(
    ctx: click.Context,
    param: click.Parameter,
    value: int,
) -> int:
    model_source = ctx.obj.get("model_source")
    if model_source is None:
        raise click.BadOptionUsage(
            option_name="--source",
            message="Model source (`--source`) must be specified before experiment_id (`--experiment-id`).",
        )
    if model_source == MODEL_SOURCE_EXPERIMENT:
        experiments = list_experiments(statuses=["completed"])
        experiment = prompt_choices(
            "Experiment",
            [(f"{x.name} #{x.number}", x) for x in reversed(experiments)],
        )
        ctx.obj["experiment_number"] = experiment.number
        return experiment.id


def experiment_id_callback(
    ctx: click.Context,
    param: click.Parameter,
    value: int,
):
    if value and "experiment_number" not in ctx.obj:
        experiment = read_experiment_by_id(value)
        ctx.obj["experiment_number"] = experiment.number
    return value


def paths_prompter(
    ctx: click.Context,
    param: click.Parameter,
    value: List[str],
) -> List[str]:
    model_source = ctx.obj.get("model_source")
    if model_source is None:
        raise click.BadOptionUsage(
            option_name="--source",
            message="Model source (`--source`) must be specified before experiment_id (`--experiment-id`).",
        )
    paths = ["/"]
    if model_source == MODEL_SOURCE_EXPERIMENT:
        experiment_number = ctx.obj.get("experiment_number")
        if experiment_number is None:
            raise click.BadOptionUsage(
                option_name="--experiment-id",
                message="Experiment id (`--experiment-id`) must be specified before paths (`--paths`).",
            )
        files = list_experiment_output_files(
            experiment_number=experiment_number,
            need_download_url=False,
            recursive=True,
            worker_number=0,
        )
        if len(files) > 0:
            paths = prompt_checkbox(
                "Paths (Press -> to select and <- to unselect)",
                choices=[(f"{x.path} {format_size(x.size)}", x.path) for x in files],
            )
            if len(paths) == 0:
                paths = ["/"]

    return paths


@model_cli.vessl_command()
@vessl_argument(
    "repository_name",
    type=click.STRING,
    required=True,
    prompter=model_repository_name_prompter,
)
@vessl_option("--model-name", type=click.STRING, help="Model name.")
@vessl_option(
    "--source",
    type=click.STRING,
    expose_value=False,
    prompter=model_source_prompter,
    callback=model_source_callback,
    help=f"{MODEL_SOURCE_EXPERIMENT} or {MODEL_SOURCE_LOCAL}.",
)
@vessl_option(
    "--experiment-id",
    type=click.INT,
    prompter=experiment_id_prompter,
    callback=experiment_id_callback,
    help=f"Experiment id to create model (only works for {MODEL_SOURCE_EXPERIMENT}).",
)
@vessl_option(
    "--path",
    type=click.STRING,
    multiple=True,
    prompter=paths_prompter,
    help=f"Path to create model (only works for {MODEL_SOURCE_EXPERIMENT}). Default: `/`",
)
@organization_name_option
@project_name_option
def create(
    repository_name: str,
    model_name: str = None,
    experiment_id: int = None,
    repository_description: str = None,
    path: str = None,
):
    model = create_model(
        repository_name=repository_name,
        repository_description=repository_description,
        experiment_id=experiment_id,
        model_name=model_name,
        paths=path,
    )
    print(
        f"Created '{model.model_repository.name}-{model.number}'.\n"
        f"For more info: {format_url(Endpoint.model.format(model.model_repository.organization.name, model.model_repository.name, model.number))}"
    )


@model_cli.vessl_command()
@vessl_argument(
    "repository_name",
    type=click.STRING,
    required=True,
    prompter=model_repository_name_prompter,
    callback=model_repository_name_callback,
)
@vessl_argument(
    "model_number",
    type=click.INT,
    required=True,
    prompter=model_number_prompter,
)
@vessl_argument(
    "source",
    type=click.Path(exists=True),
    required=True,
    prompter=generic_prompter("Source path"),
)
@vessl_argument(
    "dest",
    type=click.Path(),
    required=True,
    prompter=generic_prompter("Destination path", default="/"),
)
@organization_name_option
def upload(repository_name: str, model_number: int, source: str, dest: str):
    upload_model_volume_file(
        repository_name=repository_name,
        model_number=model_number,
        source_path=source,
        dest_path=dest,
    )
    print(f"Uploaded {source} to {dest}.")


@model_cli.vessl_command()
@vessl_argument(
    "repository_name",
    type=click.STRING,
    required=True,
    prompter=model_repository_name_prompter,
    callback=model_repository_name_callback,
)
@vessl_argument(
    "model_number",
    type=click.INT,
    required=True,
    prompter=model_number_prompter,
)
@vessl_argument(
    "source",
    type=click.Path(),
    required=True,
    prompter=generic_prompter("Source path", default="/"),
)
@vessl_argument(
    "dest",
    type=click.Path(),
    required=True,
    prompter=download_dest_path_prompter,
)
@organization_name_option
def download(repository_name: str, model_number: int, source: str, dest: str):
    download_model_volume_file(
        repository_name=repository_name,
        model_number=model_number,
        source_path=source,
        dest_path=dest,
    )
    print(f"Downloaded {source} to {dest}.")


@model_cli.vessl_command()
@vessl_argument(
    "repository_name",
    type=click.STRING,
    required=True,
    prompter=model_repository_name_prompter,
    callback=model_repository_name_callback,
)
@vessl_argument(
    "model_number",
    type=click.INT,
    required=True,
    prompter=model_number_prompter,
)
@vessl_argument(
    "path", type=click.Path(), required=True, prompter=generic_prompter("File path")
)
@organization_name_option
def delete_file(repository_name: str, model_number: int, path: str):
    delete_model_volume_file(
        repository_name=repository_name,
        model_number=model_number,
        path=path,
    )
    print(f"Deleted {path}.")
