import os
import shutil
from datetime import datetime
from pathlib import Path
from functools import partial
from typing import Optional, List

import click
from rich.console import Console
from rich.prompt import Confirm
from yaspin import yaspin

from grid.cli import rich_click
from grid.cli.observables import BaseObservable
from grid.cli.rich_click import deprecate_option
from grid.sdk import env
from grid.sdk.client import create_swagger_client
from grid.sdk.datastores import Datastore, list_datastores
from grid.openapi.models import V1DatastoreOptimizationStatus
from grid.sdk.rest import GridRestClient
from grid.sdk.user_messaging import info, questions
from grid.sdk.utils.datastore_uploads import (
    resume_datastore_upload,
    find_incomplete_datastore_upload,
    load_datastore_work_state,
    remove_datastore_work_state,
)

WARNING_STR = click.style('WARNING', fg='yellow')


@click.group(invoke_without_command=True)
@click.pass_context
@click.option(
    '--global',
    'is_global',
    type=bool,
    is_flag=True,
    default=False,
    show_default=True,
    help='Fetch sessions from everyone in the team when flag is passed'
)
@click.option(
    '--cluster',
    'cluster_id',
    type=str,
    required=False,
    default=env.CONTEXT,
    show_default=True,
    help='The cluster id to list datastores for.',
)
@click.option(
    '--show-incomplete',
    'show_incomplete',
    type=bool,
    is_flag=True,
    default=False,
    show_default=True,
    help=(
        'Show any datastore uploads which were started, but killed or errored before '
        'they finished uploading all data and became "viewable" on the grid datastore '
        'user interface.'
    )
)
def datastore(ctx, cluster_id: str, is_global: bool, show_incomplete: bool) -> None:
    """Manages Datastore workflows."""
    if ctx.invoked_subcommand is None:

        table_rows, table_cols = [], []
        if show_incomplete is True:
            # TODO: Why are we using yaspin when Rich already contains a spinner console instance?
            #       This is literally an additional dependency for no reason...
            spinner = yaspin(text=f"Loading Incomplete Datastores on Local Machine...", color="yellow")
            spinner.start()

            table_cols = ["Name", "Cluster ID", "Started At", "Source Path"]
            try:
                incomplete_id = find_incomplete_datastore_upload(grid_dir=Path(env.GRID_DIR))
                if incomplete_id is not None:
                    ds = load_datastore_work_state(grid_dir=Path(env.GRID_DIR), datastore_id=incomplete_id)
                    created = f"{datetime.fromtimestamp(ds.creation_timestamp):%Y-%m-%d %H:%M}"
                    table_rows.append([ds.datastore_name, ds.cluster_id, created, ds.source])
            except Exception as e:
                spinner.fail("✘")
                raise click.ClickException(e)
        else:
            spinner = yaspin(text=f"Loading Datastores in {env.CONTEXT}...", color="yellow")
            spinner.start()

            try:
                datastores: List[Datastore] = list_datastores(cluster_id=cluster_id, is_global=is_global)
            except Exception as e:
                spinner.fail("✘")
                raise click.ClickException(str(e))

            if is_global is True:
                table_cols = [
                    "Name", "Cluster ID", "Version", "Size", "Created At", "Created By", "Team Name", "Status"
                ]
                for ds in sorted(datastores, key=lambda k: (k.name, k.version)):
                    created = f'{ds.created_at:%Y-%m-%d %H:%M}'
                    size = ds.size
                    owner = ds.user.username
                    team = ds.user.team_name
                    status = ds.status
                    table_rows.append([ds.name, ds.cluster_id, str(ds.version), size, created, owner, team, status])
            else:
                table_cols = ["Name", "Cluster ID", "Version", "Size", "Created At", "Status"]
                for ds in sorted(datastores, key=lambda k: (k.name, k.version)):
                    created = f'{ds.created_at:%Y-%m-%d %H:%M}'
                    size = ds.size
                    status = ds.status
                    table_rows.append([ds.name, ds.cluster_id, str(ds.version), size, created, status])

        table = BaseObservable.create_table(columns=table_cols)
        for row in table_rows:
            table.add_row(*row)

        spinner.ok("✔")
        console = Console()
        console.print(table)

    elif is_global:
        click.echo(f"{WARNING_STR}: --global flag doesn't have any effect when invoked with a subcommand")


@datastore.command()
@click.pass_context
def resume(ctx):
    """Resume uploading an incomplete datastore upload session."""
    _resume()


def _resume():
    """Implementation of the resume_command function not requiring the context to be passed.
    """
    Console()  # THIS IS IMPORTANT! (otherwise console text overwrites eachother)
    with Console().status("[bold yellow]Indexing incomplete datastore uploads....", spinner_style="yellow") as status:
        incomplete_id = find_incomplete_datastore_upload(grid_dir=Path(env.GRID_DIR))
        if incomplete_id is not None:
            try:
                ds_work = load_datastore_work_state(grid_dir=Path(env.GRID_DIR), datastore_id=incomplete_id)
                status.update("[bold yellow]Checking for modified files on disk...")
                modified_files = ds_work.check_for_modified_files()
                status.stop()
                if len(modified_files) > 0:
                    should_resume = Confirm.ask(
                        questions.datastore_ask_if_should_resume_after_files_modified(modified_files),
                        default=True,
                    )
                    if not should_resume:
                        click.echo("Exiting!")
                        return
                c = GridRestClient(create_swagger_client())
                click.echo(f"creating datastore from {ds_work.source}")
                resume_datastore_upload(client=c, grid_dir=Path(env.GRID_DIR), work=ds_work)
            except Exception as e:
                raise click.ClickException(e)
        else:
            raise click.ClickException(f"no incomplete datastore upload sessions exist")


@datastore.command()
@click.pass_context
def clearcache(ctx) -> None:
    """Clears datastore cache which is saved on the local machine when uploading a datastore to grid.

    This removes all the cached files from the local machine, meaning that resuming an incomplete
    upload is not possible after running this command.
    """
    grid_dstore_path = Path(env.GRID_DIR).joinpath("datastores")
    grid_dstore_path.mkdir(parents=True, exist_ok=True)
    for f in grid_dstore_path.iterdir():
        if f.is_file():
            os.remove(str(f.absolute()))
        if f.is_dir():
            shutil.rmtree(str(f.absolute()))
    click.echo("Datastore cache cleared")


@datastore.command(cls=rich_click.deprecate_grid_options())
@click.option('--name', type=str, required=True, help='Name of the datastore')
@click.option('--version', type=int, required=True, help='Version of the datastore')
@click.option(
    '--cluster',
    type=str,
    required=False,
    default=env.CONTEXT,
    show_default=True,
    help='cluster id to delete the datastore from. (Bring Your Own Cloud Customers Only).'
)
@click.pass_context
def delete(ctx, name: str, version: int, cluster: str) -> None:
    """Deletes a datastore with the given name and version tag.

    For bring-your-own-cloud customers, the cluster id of the associated
    resource is required as well.
    """
    try:
        dstore = Datastore(name=name, version=version, cluster_id=cluster)
        dstore.delete()
    except Exception as e:
        raise click.ClickException(str(e))
    click.echo("Done!")


@datastore.command()
@rich_click.argument(
    'source',
    type=str,
    default=None,
    required=False,
    help=(
        "Source to create datastore from. This could either be a local "
        "directory (e.g: /opt/local_folder) a remote http URL pointing "
        "to a TAR or ZIP file (e.g. http://some_domain/data.tar.gz), or "
        "an s3 bucket to copy data from (e.g. s3://ryft-public-sample-data/esRedditJson/)"
    )
)
@click.option(
    '--source',
    'source_',
    type=str,
    show_default=False,
    default=None,
    required=False,
    hidden=True,
    callback=partial(deprecate_option, "the argument form (grid datastore create SOURCE) of this command"),
)
@click.option(
    "--no-copy",
    "_no_copy_data_source",
    is_flag=True,
    default=False,
    help=(
        "(beta) Use this flag when you intend to incrementally add data to the source bucket. "
        "Using this flag can also speed up datastore creation when working with large buckets. "
        "When using this flag, you cannot remove files from your bucket. If you'd like to add "
        "files, please create a new version of the datastore after you've added files to your "
        "bucket. Please note that Grid does not currently support private S3 buckets."
    ),
)
@click.option('--name', type=str, required=False, help='Name of the datastore')
@click.option(
    '--cluster',
    type=str,
    default=env.CONTEXT,
    show_default=True,
    required=False,
    help='cluster id to create the datastore on. (Bring Your Own Cloud Customers Only).'
)
@click.pass_context
def create(
    ctx, source: str, source_: str, cluster: str, _no_copy_data_source: bool, name: Optional[str] = None
) -> None:
    """Creates a datastore from SOURCE.

    If you want to check the status of your datastore creation, please use the
    `grid datastore` command.

    Here are some examples of this command in use:

    To create a datastore from a directory (or file) on the local machine
    (optionally specifying a name):

        grid datastore create ./my_cool_file.txt

        grid datastore create ./some-directory/

        grid datastore create ./some-directory/ --name my-awesome-datastore

    To create a datastore from an S3 bucket (private buckets are not currently
    supported):

        grid datastore create s3://ryft-public-sample-data/esRedditJson/

    If you'd like to create a datastore from an S3 bucket that will be
    incrementally updated, or for very large datasets:

        grid datastore create s3://ryft-public-sample-data/ --no-copy

    To create a datastore from a zip or tar.gz file hosted at a URL:

        grid datastore create https://cs.nyu.edu/~roweis/data/EachMovieData.tar.gz
    """
    if source_ is not None:
        source = source_
    try:
        Console()  # THIS IS IMPORTANT! (otherwise console text overwrites eachother)
        incomplete_id = find_incomplete_datastore_upload(Path(env.GRID_DIR))
        if incomplete_id is not None:
            should_resume = Confirm.ask(
                questions.datastore_ask_if_should_resume_upload(source),
                default=True,
            )
            if should_resume is True:
                _resume()
            else:
                remove_datastore_work_state(grid_dir=Path(env.GRID_DIR), datastore_id=incomplete_id)
                dstore = Datastore(name=name, source=source, cluster_id=cluster, s3_no_copy=_no_copy_data_source)
                click.echo(
                    f"\n{info.datastore_currently_creating_datastore(name=dstore.name, version=str(dstore.version), cluster=cluster)}"
                )
                dstore.upload()
        else:
            with Console().status("[bold yellow]Indexing datastore uploads....", spinner_style="yellow") as status:
                dstore = Datastore(name=name, source=source, cluster_id=cluster, s3_no_copy=_no_copy_data_source)
                click.echo(
                    f"\n{info.datastore_currently_creating_datastore(name=dstore.name, version=str(dstore.version), cluster=cluster)}"
                )
                status.stop()
                dstore.upload()
    except Exception as e:
        raise click.ClickException(e)

    click.echo(info.datastore_uploaded_successfully(name=name, version=str(dstore.version), cluster=cluster))
