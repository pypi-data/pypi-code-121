import os
import re
import time
from configparser import ConfigParser
from pathlib import Path

import click
import yaml
from colorama import Fore, Style
from git import Repo
from github import (BadCredentialsException, Github, GithubException,
                    TwoFactorException)
from halo import Halo
from xdg import xdg_config_home

from sph.git import (CantCommitException, CantMergeException,
                     get_number_changed_file, print_index, sph_commit,
                     sph_merge, sph_push)
from sph.utils import delete_term_n_previous_line, Editable
from sph.editable import create_editable_from_workspace

github_client = None

def checking_workflow(editable):
    waiting_for_run = Halo('Waiting for workflow status', spinner='dots')
    waiting_for_run.start()
    current_run = None
    for i in range(10):
        runs_queued = editable.gh_repo_client.get_workflow_runs(
            branch=editable.repo.active_branch.name, status='queued'
        )
        runs_in_progress = editable.gh_repo_client.get_workflow_runs(
            branch=editable.repo.active_branch.name, status='in_progress'
        )
        runs_completed = editable.gh_repo_client.get_workflow_runs(
            branch=editable.repo.active_branch.name, status='completed'
        )
        if (
            runs_queued.totalCount > 0
            or runs_in_progress.totalCount > 0 or runs_completed.totalCount > 0
        ):
            for run in (
                    list(runs_queued)
                    + list(runs_in_progress) + list(runs_completed)
            ):
                if run.head_sha == editable.repo.head.commit.hexsha:
                    current_run = run
            if current_run:
                break
        time.sleep(2)

    waiting_for_run.stop()

    run_progress = Halo(f'Workflow {current_run.status}. Waiting for the end')
    run_progress.start()
    status = current_run.status
    if current_run:
        while current_run.status != 'completed':
            if current_run.status != status:
                run_progress.stop()
                run_progress = Halo(f'Workflow {current_run.status}.' +
                                    ' Waiting for the end')
                run_progress.start()

            status = current_run.status
            current_run = editable.gh_repo_client.get_workflow_run(
                current_run.id)
            time.sleep(2)

        if current_run.conclusion == 'success':
            run_progress.succeed('Workflow completed with success')
            click.echo()
        else:
            run_progress.fail('Workflow failed')
            raise click.Abort()
    else:
        Halo('Can\'t find a workflow run associated with this commit').fail()
        raise click.Abort()


def is_there_a_completed_run(gh_repo_client, repo):
    # We did not push look for a completed run
    runs_completed = gh_repo_client.get_workflow_runs(
        branch=repo.active_branch.name, status='completed'
    )

    runs_completed = gh_repo_client.get_workflow_runs(
        branch=repo.active_branch.name, status='completed'
    )

    run_is_completed = False
    if runs_completed.totalCount > 0:
        for run in runs_completed:
            if run.head_sha == repo.head.commit.hexsha:
                run_is_completed = True

    return run_is_completed


def check_state_of_repo_and_commit(editable):
    add_and_commit = False

    if editable.repo.is_dirty():
        click.echo('You have some file in your index')
        print_index(editable)
        add_and_commit = click.confirm(
            'Do you want to add and commit those changes ?'
        )
    else:
        Halo('Git repository is clean').succeed()
        click.echo()

    if add_and_commit:
        commit_msg = click.prompt(
            'Type in your commit message',
            default=f'Publishing {editable.name} new version'
        )
        number_deleted_lines = 3 + get_number_changed_file(editable)
        try:
            sph_commit(
                editable,
                '.',
                commit_msg,
            )
        except CantCommitException:
            Halo('Could not commit your repo changes').fail()
            raise click.Abort()

        delete_term_n_previous_line(number_deleted_lines)
        Halo(f'Change commited with message {commit_msg}').succeed()
        click.echo()
    elif editable.repo.is_dirty():
        delete_term_n_previous_line(2 + get_number_changed_file(editable))
        click.echo(click.style(f'{Fore.YELLOW}ℹ {Fore.RESET}',
                               bold=True), nl=False)
        click.echo('Skipping commit')
        return False
    return True


def merge_into_develop(editable):
    click.echo(f'We are on {editable.repo.active_branch.name}.')
    click.echo('We need to be on the develop branch to update dependency')
    merge_branch = click.confirm('Do you want to merge the branch')
    click.echo()

    if merge_branch:
        try:
            # merging into develop
            sph_merge(
                editable,
                editable.repo.active_branch.name,
                'develop',
                f'Merging {editable.repo.active_branch.name} into' +
                ' develop')
        except CantMergeException as e:
            Halo('Could not merge your branch.' +
                 ' Please do it manually').fail()
            click.echo(e)
            raise click.Abort()

        Halo(text="Merge repo").succeed()
        click.echo()
    else:
        Halo(text='Aborting because we need the merge to happen.').fail()
        raise click.Abort()


def commit_conanfile_changes(editable, conanfile_update_names):

    if editable.repo.is_dirty():
        try:
            version_update_str = [
                f'{name}'
                for name, version in conanfile_update_names
            ]
            commit_msg = f'Updating {", ".join(version_update_str)}'
            try:
                sph_commit(
                    editable,
                    'conan/conanfile.py',
                    commit_msg
                )
            except CantCommitException:
                Halo('Could not commit conanfile automatically').fail()
                raise click.Abort()

            Halo('Conanfile version update commited automatically').succeed()
            click.echo()
        except Exception:
            Halo('Could not auto commit version update in conanfile').fail()
            raise click.Abort()


def find_updatable_editable(editables):
    updatables = list()
    for ed in [ed for ed in editables if not ed.updated]:
        updatable = True
        for lib in ed.required_lib:
            if not lib.updated:
                updatable = False

        if updatable:
            updatables.append(ed)

    return updatables


def update_conan_file(updatable, updated_editables):
    conanfile_update_names = list()
    file_lines = list()
    file_lines_update = False
    with open(updatable.conan_path, 'r') as conanfile:
        file_lines = conanfile.readlines()

    for updated_editable in updated_editables:
        for i, line in enumerate(file_lines):
            name_regex = re.compile(
                rf'(.*)(({updated_editable.name})/(\w+)\@(.*))"\)(,?)'
            )
            match = name_regex.search(line)
            if match:
                lib_version = match.group(4)

                if (
                    lib_version !=
                    updated_editable.repo.head.commit.hexsha[0:10]
                ):
                    file_lines_update = True
                    replacement = (
                        f'{match.group(1)}{match.group(3)}/' +
                        f'{updated_editable.repo.head.commit.hexsha[0:10]}' +
                        f'@{match.group(5)}"){match.group(6)}\n'
                    )
                    conanfile_update_names.append(
                        (
                            updated_editable.name,
                            updated_editable.repo.head.commit.hexsha[0:10]
                        )
                    )
                    file_lines[i] = replacement
                    click.echo(
                        f'{Fore.YELLOW}{match.group(3)}/{match.group(4)}@' +
                        f'{match.group(5)} {Fore.RESET}-> ' +
                        f'{Fore.CYAN}{match.group(3)}/' +
                        f'{updated_editable.repo.head.commit.hexsha[0:10]}@' +
                        f'{match.group(5)}{Fore.RESET}'
                    )

    if file_lines_update:
        click.echo()

    with open(updatable.conan_path, 'w') as conanfile:
        conanfile.writelines(file_lines)

    return conanfile_update_names


def update_workspace(
        editables: [Editable], workspace_path: Path, workspace_data
):
    updated_workspace = False
    for name, path in workspace_data['editables'].copy().items():
        for editable in editables:
            match = re.search(rf'(.*)(({editable.name})/(\w+)\@(.*))', name)
            if match:
                lib_version = match.group(4)
                if lib_version != editable.repo.head.commit.hexsha[0:10]:
                    updated_workspace = True
                    new_version = (
                        f'{match.group(3)}/' +
                        f'{editable.repo.head.commit.hexsha[0:10]}' +
                        f'@{match.group(5)}'
                    )
                    old_version = (
                        f'{match.group(3)}/' +
                        f'{match.group(4)}@{match.group(5)}'
                    )

                    click.echo(
                        f'{Style.DIM}' +
                        f'Switching {Fore.LIGHTCYAN_EX}{editable.name}' +
                        f'{Fore.RESET} version in workspace.yml:' +
                        f'{Style.RESET_ALL} {Fore.YELLOW}{match.group(3)}/' +
                        f'{match.group(4)}@{match.group(5)} {Fore.RESET}->' +
                        f' {Fore.CYAN}{match.group(3)}/' +
                        f'{editable.repo.head.commit.hexsha[0:10]}' +
                        f'@{match.group(5)}{Fore.RESET}'
                    )
                    workspace_data['editables'][new_version] = path
                    del workspace_data['editables'][old_version]

    if updated_workspace:
        click.echo()

    with open(workspace_path, 'w') as file:
        file.write(yaml.dump(workspace_data))

    repo = Repo(workspace_path.parents[0])

    if repo.is_dirty():
        repo.git.add('.')
        repo.git.commit('-m updating workspace')

    we_need_to_push = Halo('Pushing workspace to github', spinner='dots')
    we_need_to_push.start()
    res = repo.remote('origin').push()
    we_need_to_push.stop()
    if len(res) == 0:
        we_need_to_push.fail('Cannot push to github. Aborting')
        raise click.Abort()
    else:
        we_need_to_push.succeed('Pushed workspace to github')


def update_editable(
        updatable: Editable,
        updated_editables: [Editable],
        workspace_path: Path):
    updated = False

    while not updated:
        clean = check_state_of_repo_and_commit(updatable)
        conanfile_update_names = update_conan_file(
            updatable, updated_editables)
        if clean:
            commit_conanfile_changes(updatable, conanfile_update_names)
        else:
            Halo('Can\'t auto update conan file without a clean repo').warn()

        sph_push(updatable)
        checking_workflow(updatable)

        if updatable.repo.active_branch.name == 'develop':
            updated = True
        else:
            merge_into_develop(updatable)

    updatable.updated = True
    return updatable


@click.command()
@click.option("--github-token", "-gt")
@click.argument("workspace")
def publish(github_token, workspace):
    global github_client
    # Setting up github
    config_path = xdg_config_home() / 'shred-project-helper/sph.ini'
    config = ConfigParser()

    if not os.path.exists(config_path):
        click.echo('⚙ Creating config')
        click.echo()
        config['github'] = {'access_token': ''}
        os.mkdir(xdg_config_home() / 'shred-project-helper')
        with open(config_path, 'w+') as config_file:
            config.write(config_file)
    else:
        config.read(config_path)

        if not github_token:
            github_token = config['github']['access_token']

    if github_token and 'access_token' not in config['github']:
        save_token = click.confirm('Save access token to config?')
        if save_token:
            config['github']['access_token'] = github_token
            with open(config_path, 'w+') as config_file:
                config.write(config_file)

    click.echo('Updating all library in workspace')
    click.echo()

    try:
        if not github_token:
            github_username = click.prompt('Github username')
            github_password = click.prompt('Github password')
            github_client = Github(github_username, github_password)
        else:
            github_client = Github(github_token)

        user = github_client.get_user()
        Halo(f'Logged in github as {user.login}').succeed()
        click.echo()

    except BadCredentialsException as e:
        click.echo('Wrong github credentials')
        click.echo(e)
        raise click.Abort()
    except TwoFactorException as e:
        click.echo(
            'Can\'t use credentials for account with 2FA. Please use an' +
            ' access token.'
        )
        click.echo(e)
        raise click.Abort()
    except GithubException as e:
        click.echo('Github issue')
        click.echo(e)
        raise click.Abort()

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
        workspace_path, workspace_data, github_client
    )

    loading_editables_spinner.succeed()
    click.echo()

    Halo(
        text='Updating editables'
    ).stop_and_persist('⟳')
    click.echo()

    updated_editables = list()

    while not all([e.updated for e in editables]):
        updatables = find_updatable_editable(editables)

        for updatable in updatables:
            click.echo(
                f'{Style.DIM}Updating editable: ' +
                f'{updatable.name}{Style.RESET_ALL}'
            )
            click.echo()
            updated_editables.append(
                update_editable(updatable, updated_editables, workspace_path))

    updating_workspace_spinner = Halo(
        text='Updating workspace',
        spinner='dots'
    )
    updating_workspace_spinner.stop_and_persist('⟳')
    click.echo()

    update_workspace(editables, Path(workspace_path), workspace_data)
