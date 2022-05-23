import click
from dotpyle.services.repo_handler import RepoHandler
from dotpyle.decorators.pass_repo_handler import pass_repo_handler


@click.command()
@pass_repo_handler
def pull(repo_handler: RepoHandler):
    repo_handler.pull()
