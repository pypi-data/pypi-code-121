import json
import sys
import warnings
from functools import partial
from getpass import getpass
from pathlib import Path
from typing import IO, Any

import click
from pydantic.json import pydantic_encoder

from unfolded.data_sdk.data_sdk import DataSDK, RefreshToken
from unfolded.data_sdk.models import MediaType


class PathType(click.Path):
    """A Click path argument that returns a pathlib Path, not a string"""

    def convert(self, value: Any, param: Any, ctx: Any) -> Any:
        return Path(super().convert(value, param, ctx))


@click.group()
def main() -> None:
    pass


@click.command()
@click.option(
    "--organization/--no-organization",
    default=False,
    help="If True, list datasets for organization of authenticated user. For non-enterprise users, passing this flag will cause the request to fail with: `403: Insufficient permission level to perform this action",
    show_default=True,
)
def list_datasets(organization: bool) -> None:
    """List datasets for authenticated user"""
    data_sdk = DataSDK()
    output_data = [
        dataset.dict() for dataset in data_sdk.list_datasets(organization=organization)
    ]
    click.echo(json.dumps(output_data, indent=4, default=pydantic_encoder))


@click.command()
@click.option("--dataset-id", type=str, required=True, help="Dataset id.")
def get_dataset(dataset_id: str) -> None:
    """Get dataset given its id"""
    data_sdk = DataSDK()
    dataset = data_sdk.get_dataset_by_id(dataset=dataset_id)
    click.echo(dataset.json(indent=4))


@click.command()
@click.option("--dataset-id", type=str, required=True, help="Dataset id.")
@click.option(
    "-o",
    "--output-file",
    type=PathType(file_okay=True, writable=True),
    required=True,
    help="Output file for dataset.",
)
@click.option(
    "--progress/--no-progress",
    default=True,
    help="Whether to show progress bar.",
    show_default=True,
)
def download_dataset(dataset_id: str, output_file: Path, progress: bool) -> None:
    """Download data for existing dataset to disk"""
    data_sdk = DataSDK()
    data_sdk.download_dataset(
        dataset=dataset_id, output_file=output_file, progress=progress
    )


@click.command()
@click.option(
    "-n", "--name", type=str, required=False, default=None, help="Dataset name."
)
@click.option(
    "--media-type",
    type=click.Choice([c.value for c in MediaType], case_sensitive=False),
    required=False,
    default=None,
    help="Dataset media type.",
)
@click.option(
    "--dataset-id",
    type=str,
    required=False,
    default=None,
    help="Dataset id. If provided, will update the existing dataset.",
)
@click.option(
    "--desc",
    type=str,
    required=False,
    default=None,
    show_default=True,
    help="Dataset description.",
)
@click.option(
    "--progress/--no-progress",
    default=True,
    help="Whether to show progress bar.",
    show_default=True,
)
@click.argument("file", type=PathType(readable=True, file_okay=True))
def upload_file(
    file: Path, name: str, media_type: str, dataset_id: str, desc: str, progress: bool
) -> None:
    """Upload new dataset to Unfolded Studio"""
    data_sdk = DataSDK()
    new_dataset = data_sdk.upload_file(
        file=file,
        name=name,
        media_type=media_type,
        description=desc,
        dataset=dataset_id,
        progress=progress,
    )
    click.echo(new_dataset.json())


@click.command()
@click.option(
    "--dataset-id",
    type=str,
    required=False,
    default=None,
    help="Dataset id. If provided, will update the existing dataset.",
)
@click.option(
    "--media-type",
    type=click.Choice([c.value for c in MediaType], case_sensitive=False),
    required=False,
    default=None,
    help="Dataset media type.",
)
@click.option(
    "--progress/--no-progress",
    default=True,
    help="Whether to show progress bar.",
    show_default=True,
)
@click.argument("file", type=PathType(readable=True, file_okay=True))
def update_dataset(
    file: Path, dataset_id: str, media_type: str, progress: bool
) -> None:
    """Update data for existing Unfolded Studio dataset"""
    warnings.warn(
        "update-dataset is deprecated. Use upload-file with a --dataset-id option.",
        DeprecationWarning,
    )

    data_sdk = DataSDK()
    updated_dataset = data_sdk.upload_file(
        file=file, dataset=dataset_id, media_type=media_type, progress=progress
    )
    click.echo(updated_dataset.json())


def abort_if_false(ctx: Any, param: Any, value: Any) -> None:
    # pylint: disable=unused-argument
    if not value:
        ctx.abort()


@click.command()
@click.option("--dataset-id", type=str, required=True, help="Dataset id.")
@click.option(
    "--force",
    is_flag=True,
    callback=abort_if_false,
    expose_value=False,
    help="Delete dataset without prompting.",
    prompt="Are you sure you want to delete the dataset?",
)
def delete_dataset(dataset_id: str) -> None:
    """Delete dataset from Unfolded Studio

    Warning: This operation cannot be undone. If you delete a dataset currently
    used in one or more maps, the dataset will be removed from those maps,
    possibly causing them to render incorrectly.
    """
    data_sdk = DataSDK()
    data_sdk.delete_dataset(dataset=dataset_id)
    click.echo("Dataset deleted.", file=sys.stderr)


@click.command()
@click.option(
    "--organization/--no-organization",
    default=False,
    help="If True, list map records for organization of authenticated user. For non-enterprise users, passing this flag will cause the request to fail with: `403: Insufficient permission level to perform this action",
    show_default=True,
)
def list_maps(organization: bool) -> None:
    """List map records for authenticated user"""
    data_sdk = DataSDK()
    output_data = [
        map.dict(exclude_none=True)
        for map in data_sdk.list_maps(organization=organization)
    ]
    click.echo(json.dumps(output_data, indent=4, default=pydantic_encoder))


@click.command()
@click.argument("map_id", type=str)
def get_map(map_id: str) -> None:
    """Get an Unfolded map record by its id, including associated datasets and map state"""
    data_sdk = DataSDK()
    map_object = data_sdk.get_map_by_id(map_id)
    click.echo(map_object.json())


@click.command()
@click.option("--name", type=str, required=True, help="The map name")
@click.option("--description", type=str, required=False, help="The map description")
@click.option(
    "--map-state",
    type=click.File(),
    required=False,
    help="The map state as a json file",
)
@click.option(
    "--dataset-ids",
    type=str,
    required=False,
    help="Comma separated list of dataset ids to add to the map",
)
def create_map(name: str, description: str, map_state: IO, dataset_ids: str) -> None:
    """Create an Unfolded Studio map"""
    data_sdk = DataSDK()
    datasets = (
        [dataset_id.strip() for dataset_id in dataset_ids.split(",")]
        if dataset_ids
        else None
    )

    map_object = data_sdk.create_map(
        name=name,
        description=description,
        map_state=json.load(map_state) if map_state else None,
        datasets=datasets,
    )

    click.echo(map_object.json())


@click.command()
@click.argument("map_id", type=str)
@click.option(
    "--copy-datasets/--no-copy-datasets",
    required=True,
    help="If True, will copy the map and copy its underlying datasets.",
)
@click.option(
    "--name",
    type=str,
    required=False,
    help="The name for the new copied map. Default: 'Copy of {source_map_name}'",
)
def copy_map(map_id: str, copy_datasets: bool, name: str) -> None:
    """Copy an Unfolded map"""
    data_sdk = DataSDK()
    map_object = data_sdk.copy_map(map_id, copy_datasets=copy_datasets, name=name)
    click.echo(map_object.json())


@click.command()
@click.option("--map-id", type=str, required=True, help="The map id")
@click.option("--name", type=str, required=False, help="The map name")
@click.option("--description", type=str, required=False, help="The map description")
@click.option(
    "--map-state",
    type=click.File(),
    required=False,
    help="The map state as a json file",
)
@click.option(
    "--dataset-ids",
    type=str,
    required=False,
    help="Comma separated list of dataset ids to add to the map",
)
def update_map(
    map_id: str, name: str, description: str, map_state: IO, dataset_ids: str
) -> None:
    """Update an Unfolded Studio map"""
    data_sdk = DataSDK()
    datasets = (
        [dataset_id.strip() for dataset_id in dataset_ids.split(",")]
        if dataset_ids
        else None
    )
    map_object = data_sdk.update_map(
        map_id=map_id,
        name=name,
        description=description,
        map_state=json.load(map_state) if map_state else None,
        datasets=datasets,
    )
    click.echo(map_object.json())


@click.command()
@click.option(
    "--force",
    is_flag=True,
    callback=abort_if_false,
    expose_value=False,
    help="Delete map without prompting.",
    prompt="Are you sure you want to delete this map?",
)
@click.argument("map_id", type=str)
def delete_map(map_id: str) -> None:
    """Delete map from Unfolded Studio

    Warning: This operation cannot be undone.
    """
    data_sdk = DataSDK()
    data_sdk.delete_map(map_id)
    click.echo("Map deleted.", file=sys.stderr)


@click.command()
@click.option(
    "--refresh-token",
    type=str,
    help="Refresh Token. Retrieve from https://studio.unfolded.ai/tokens.html",
    # Use getpass for password input
    # Ref https://github.com/pallets/click/issues/300#issuecomment-606105993
    default=partial(getpass, "Refresh Token: "),
)
@click.option(
    "--credentials-dir",
    type=PathType(dir_okay=True, file_okay=False, writable=True),
    help="A directory on disk to use for storing credentials.",
    default=Path("~/.config/unfolded/").expanduser(),
    show_default=True,
)
def store_refresh_token(refresh_token: RefreshToken, credentials_dir: Path) -> None:
    """Store refresh token to enable seamless future authentication

    Retrieve token from https://studio.unfolded.ai/tokens.html
    """
    DataSDK(refresh_token=refresh_token, credentials_dir=credentials_dir)


main.add_command(list_datasets)
main.add_command(get_dataset)
main.add_command(download_dataset)
main.add_command(upload_file)
main.add_command(update_dataset)
main.add_command(delete_dataset)
main.add_command(list_maps)
main.add_command(get_map)
main.add_command(create_map)
main.add_command(copy_map)
main.add_command(update_map)
main.add_command(delete_map)
main.add_command(store_refresh_token)

if __name__ == "__main__":
    main()
