import click
from colorama import Fore
from github import GithubException
from halo import Halo


class CantCommitException(Exception):
    pass


class CantMergeException(Exception):
    pass


class CantPushException(Exception):
    pass


change_type_to_str = {
    "A": "New file",
    "D": "Deleted file",
    "R": "Renamed file",
    "M": "Modified file",
    "T": "Type of file changed (e.g. symbolic link became a file)"
}


def print_index(editable):
    staged_files = []
    unstaged_files = []
    untracked_files = []

    files_in_status = editable.repo.git.status('--porcelain').splitlines()

    for file in files_in_status:
        if file[0] == ' ':
            unstaged_files.append((file[1:2], file[3:]))
        if file[1] == ' ':
            staged_files.append((file[0:1], file[3:]))
        if file[0:2] == '??':
            untracked_files.append(file[3:])

    for change_type, path in staged_files:
        click.echo(f'{Fore.GREEN}{change_type_to_str[change_type]}:' +
                   f' {path}', color=True)
    for change_type, path in unstaged_files:
        click.echo(f'{Fore.RED}{change_type_to_str[change_type]}:' +
                   f' {path}', color=True)
    for path in untracked_files:
        click.echo(f'{Fore.RED}Untracked files: {path}', color=True)

    click.echo(Fore.RESET, nl=False)


def get_number_changed_file(editable):
    status_text = editable.repo.git.status('--porcelain')
    return len(status_text.splitlines())


def sph_commit(
        editable,
        add_query,
        commit_msg,
):
    try:
        editable.repo.git.add(add_query)
        editable.repo.git.commit(f'-m {commit_msg}')
    except Exception:
        raise CantCommitException()


def sph_merge(
        editable,
        source_branch,
        dest_branch,
        message
):
    try:
        editable.repo.git.checkout(dest_branch)
        editable.repo.git.merge(
            f'-m "{message}"', '--no-ff', source_branch
        )
    except Exception:
        raise CantMergeException()


def sph_push(
    editable
):
    try:
        commit = None
        try:
            commit = editable.gh_repo_client.get_commit(
                editable.repo.active_branch.name
            )
        except GithubException as e:
            if 'No commit' not in e.data.get('message'):
                raise e

        need_to_push = (
            not commit or commit.sha != editable.repo.head.commit.hexsha
        )
        if need_to_push:
            we_need_to_push = Halo('Pushing to github', spinner='dots')
            we_need_to_push.start()
            branch_name = editable.repo.active_branch.name
            res = editable.repo.remote('origin').push(
                f'refs/heads/{branch_name}:refs/heads/{branch_name}'
            )
            if len(res) == 0:
                we_need_to_push.fail('Cannot push to github. Aborting')
                raise click.Abort()
            else:
                we_need_to_push.succeed('Pushed to github')
                click.echo()
    except Exception:
        raise CantPushException()
