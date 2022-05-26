import os
import re
import subprocess
import shutil
import fileinput

from configparser import ConfigParser
from pathlib import Path

import click
from colorama import Fore
import yaml
from halo import Halo

from sph.publish import publish
from sph.editable import create_editable_from_workspace

def rmtree_on_error(function, path, excinfo):
    Halo(f'Could not delete {path}').fail()


@click.command()
@click.option(
    "--force",
    "-f",
    default=False,
    is_flag=True,
    help="Doesn't ask for deletion confirmation"
)
@click.option(
    "--clean-cwd",
    "-c",
    default=False,
    is_flag=True,
    help="Clean current directory"
)
@click.argument("workspace")
def cleanup(force, workspace, clean_cwd):
    workspace_path = Path(workspace)
    if not workspace_path.is_file():
        workspace_path = workspace_path / 'workspace.yml'

    workspace_data = None
    try:
        with open(workspace_path.resolve(), 'r') as workspace_file:
            try:
                workspace_data = yaml.full_load(workspace_file)
            except yaml.YAMLError as exc:
                click.echo(f'Can\'t parse file {workspace_path}')
                click.echo(exc)
                raise click.Abort()

    except OSError as exc:
        click.echo(f'Can\'t open file {workspace_path}')
        click.echo(exc)
        raise click.Abort()

    layout_file = workspace_data['layout']
    build_location = None

    with fileinput.input(
        (workspace_path.parents[0] / layout_file).resolve()
    ) as f:
        for line in f:
            if line == '[build_folder]\n':
                build_folder = Path(f.readline())
                build_location = build_folder.parents[1]

    for path in [
            e['path'] for name, e in workspace_data['editables'].items()
    ]:
        path_to_delete = (
            workspace_path.parents[0] / path / build_location
        ).resolve()

        if not os.path.isdir(path_to_delete):
            click.echo(click.style(f'{Fore.YELLOW}ℹ {Fore.RESET}',
                                   bold=True), nl=False)
            click.echo(f'Skipping {path_to_delete} directory does not exists')
            continue

        delete_spinner = None
        if force:
            delete_confirm = force
            delete_spinner = Halo(f'Deleting {path_to_delete}')
            delete_spinner.start()
        else:
            delete_confirm = click.confirm(f'Delete {path_to_delete}')
            delete_spinner = Halo(f'Deleting {path_to_delete}')
            delete_spinner.start()

        if delete_confirm:
            shutil.rmtree(path_to_delete, onerror=rmtree_on_error)

            delete_spinner.stop()
            Halo(f'Deleted {path_to_delete}').succeed()

    if clean_cwd:
        click.echo()
        clean_cwd = click.confirm('Do you want to clean the current directory (beware this will clean the cwd!!!!)')
        click.echo()

    if clean_cwd:
        ls = subprocess.Popen(["ls", "-p", "."], stdout=subprocess.PIPE)
        list_of_content = list(ls.stdout)

        if len(list_of_content) > 0:
            click.echo(click.style(f'{Fore.YELLOW}ℹ {Fore.RESET}',
                                   bold=True), nl=False)

            click.echo('List of files and directory that will be deleted')
            click.echo()

            files = []
            directories = []

            for file in list_of_content:
                file_path = Path(Path(os.getcwd()) / file.decode("utf-8").strip())
                if file_path.is_file():
                    files.append(file_path)
                if file_path.is_dir():
                    directories.append(file_path)

            for directory in directories:
                click.echo(f' 📁{Fore.CYAN} {directory.name}{Fore.RESET}')
            for file in files:
                click.echo(f' 📄{Fore.YELLOW} {file.name}{Fore.RESET}')

            if len(files) > 0 or len(directories) > 0:
                click.echo()
                confirm_deletion = click.confirm('Clean directory')
                click.echo()

                if confirm_deletion:
                    for directory in directories:
                        delete_spinner = Halo(f'Deleting {directory.name}')
                        delete_spinner.start();
                        shutil.rmtree(directory)
                        delete_spinner.succeed(f'Deleted {directory.name}')
                    for file in files:
                        delete_spinner = Halo(f'Deleting {file.name}')
                        delete_spinner.start();
                        os.remove(file)
                        delete_spinner.succeed(f'Deleted {file.name}')


@click.command()
@click.argument("workspace")
def setup(workspace):
    workspace_path = Path(workspace)
    if not workspace_path.is_file():
        workspace_path = workspace_path / 'workspace.yml'

    workspace_data = None
    try:
        with open(workspace_path.resolve(), 'r') as workspace_file:
            try:
                workspace_data = yaml.full_load(workspace_file)
            except yaml.YAMLError as exc:
                click.echo(f'Can\'t parse file {workspace_path}')
                click.echo(exc)
                raise click.Abort()

    except OSError as exc:
        click.echo(f'Can\'t open file {workspace_path}')
        click.echo(exc)
        raise click.Abort()

    loading_editables_spinner = Halo(
        text='Retrieving editables', spinner='dots'
    )
    loading_editables_spinner.start()

    editables = create_editable_from_workspace(
        workspace_path, workspace_data
    )

    loading_editables_spinner.succeed()
    click.echo()

    for ed in editables:
        match = re.search(rf'(.*)(({ed.name})/(\w+)\@(.*))', ed.full_name)
        if match:
            sha = match.group(4)
            if not ed.repo.is_dirty():
                click.echo()
                click.echo(click.style(f'{Fore.YELLOW}ℹ {Fore.RESET}',
                                       bold=True), nl=False)
                click.echo(f'Checking out {ed.name} at {sha}')
                try:
                    ed.repo.git.checkout(sha)
                    Halo(
                        f'Successfuly checked out {ed.name} at {sha}'
                    ).succeed()
                except Exception:
                    Halo(f'Couldn\'t checkout {ed.name} at {sha}').fail()
            else:
                Halo(f'Can\'t checkout {ed.name} at {sha}. It is dirty.').fail()


@click.group()
def be_helpful():
    pass


be_helpful.add_command(publish)
be_helpful.add_command(setup)
be_helpful.add_command(cleanup)
