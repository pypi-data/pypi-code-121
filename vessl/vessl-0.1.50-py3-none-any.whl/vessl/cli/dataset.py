import os

import click

from vessl.cli._base import VesslGroup, vessl_argument
from vessl.cli._util import (
    Endpoint,
    generic_prompter,
    print_data,
    print_table,
    print_volume_files,
    prompt_choices,
    truncate_datetime,
)
from vessl.cli.organization import organization_name_option
from vessl.dataset import (
    copy_dataset_volume_file,
    create_dataset,
    delete_dataset_volume_file,
    download_dataset_volume_file,
    list_dataset_volume_files,
    list_datasets,
    read_dataset,
    upload_dataset_volume_file,
)


def dataset_name_prompter(
    ctx: click.Context,
    param: click.Parameter,
    value: str,
) -> str:
    datasets = list_datasets()
    return prompt_choices("Dataset", [x.name for x in datasets])


def dataset_name_callback(
    ctx: click.Context,
    param: click.Parameter,
    value: str,
):
    if value:
        ctx.obj["dataset_name"] = value
    return value


def download_dest_path_prompter(
    ctx: click.Context,
    param: click.Parameter,
    value: str,
) -> str:
    return click.prompt(
        "Destination path",
        default=os.path.join(os.getcwd(), ctx.obj["dataset_name"])
        if ctx.obj.get("dataset_name")
        else ".",
    )


@click.command(name="dataset", cls=VesslGroup)
def cli():
    pass


@cli.vessl_command()
@vessl_argument(
    "name", type=click.STRING, required=True, prompter=dataset_name_prompter
)
@organization_name_option
def read(name: str):
    dataset = read_dataset(dataset_name=name)
    print_data(
        {
            "ID": dataset.id,
            "Name": dataset.name,
            "Organization": dataset.organization.name,
            "Versioning": dataset.is_version_enabled,
            "Volume ID": dataset.volume_id,
            "Source": dataset.source.type,
        }
    )
    print(
        f"For more info: {Endpoint.dataset.format(dataset.organization.name, dataset.name)}"
    )


@cli.vessl_command()
@organization_name_option
def list():
    datasets = list_datasets()
    print_table(
        datasets,
        ["Name", "Source", "Updated"],
        lambda x: [x.name, x.source.type, truncate_datetime(x.updated_dt)],
    )


@cli.vessl_command()
@vessl_argument(
    "name", type=click.STRING, required=True, prompter=generic_prompter("Dataset name")
)
@click.option("-m", "--description", type=click.STRING)
@click.option(
    "--is-public",
    type=click.BOOL,
    is_flag=True,
    help="Required if dataset sourced from a public bucket.",
)
@click.option(
    "-e",
    "--external-path",
    type=click.STRING,
    help="AWS S3 or Google Cloud Storage bucket URL (starts with `s3://` or `gs://`).",
)
@click.option("--aws-role-arn", type=click.STRING, help="Required for S3 datasets.")
@click.option("--enable-versioning", is_flag=True)
@click.option(
    "--version-path",
    type=click.STRING,
    help="Required to version AWS S3 or Google Cloud Storage dataset.",
)
@organization_name_option
def create(
    name: str,
    description: str,
    is_public: bool,
    external_path: str,
    aws_role_arn: str,
    enable_versioning: bool,
    version_path: str,
):
    dataset = create_dataset(
        dataset_name=name,
        description=description,
        is_version_enabled=enable_versioning,
        is_public=is_public,
        external_path=external_path,
        aws_role_arn=aws_role_arn,
        version_path=version_path,
    )
    print(
        f"Created '{dataset.name}'.\n"
        f"For more info: {Endpoint.dataset.format(dataset.organization.name, dataset.name)}"
    )


@cli.vessl_command()
@vessl_argument(
    "name", type=click.STRING, required=True, prompter=dataset_name_prompter
)
@click.option("-p", "--path", type=click.Path(), default="", help="Defaults to root.")
@click.option("-r", "--recursive", is_flag=True)
@organization_name_option
def list_files(
    name: str,
    path: str,
    recursive: bool,
):
    files = list_dataset_volume_files(
        dataset_name=name,
        path=path,
        need_download_url=False,
        recursive=recursive,
    )
    print_volume_files(files)


@cli.vessl_command()
@vessl_argument(
    "name", type=click.STRING, required=True, prompter=dataset_name_prompter
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
def upload(name: str, source: str, dest: str):
    upload_dataset_volume_file(
        dataset_name=name,
        source_path=source,
        dest_path=dest,
    )
    print(f"Uploaded {source} to {dest}.")


@cli.vessl_command()
@vessl_argument(
    "name",
    type=click.STRING,
    required=True,
    prompter=dataset_name_prompter,
    callback=dataset_name_callback,
)
@vessl_argument(
    "source",
    type=click.Path(),
    required=True,
    prompter=generic_prompter("Source path", default="/"),
)
@vessl_argument(
    "dest", type=click.Path(), required=True, prompter=download_dest_path_prompter
)
@organization_name_option
def download(name: str, source: str, dest: str):
    download_dataset_volume_file(
        dataset_name=name,
        source_path=source,
        dest_path=dest,
    )
    print(f"Downloaded {source} to {dest}.")


@cli.vessl_command()
@vessl_argument(
    "name", type=click.STRING, required=True, prompter=dataset_name_prompter
)
@vessl_argument(
    "source", type=click.Path(), required=True, prompter=generic_prompter("Source path")
)
@vessl_argument(
    "dest",
    type=click.Path(),
    required=True,
    prompter=generic_prompter("Destination path"),
)
@organization_name_option
def copy(name: str, source: str, dest: str):
    copy_dataset_volume_file(
        dataset_name=name,
        source_path=source,
        dest_path=dest,
    )
    print(f"Copied {source} to {dest}.")


@cli.vessl_command()
@vessl_argument(
    "name", type=click.STRING, required=True, prompter=dataset_name_prompter
)
@vessl_argument(
    "path", type=click.Path(), required=True, prompter=generic_prompter("File path")
)
@organization_name_option
def delete_file(name: str, path: str):
    delete_dataset_volume_file(
        dataset_name=name,
        path=path,
    )
    print(f"Deleted {path}.")
