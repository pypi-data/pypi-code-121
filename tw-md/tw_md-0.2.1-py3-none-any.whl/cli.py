from email.policy import default
import click

from .service.github_service import GithubService
from .service.markdown_service import MarkdownService
from .errors.github_errors import RepositoryNotFoundError


@click.group()
def cli() -> None:
    ...


@click.option("-o", "--owner", help="The repository owner", prompt="Owner")
@click.option("-r", "--repo", help="The reposiotry name", prompt="Repo")
@click.option(
    "-f",
    "--filename",
    help="The markdown filename",
    prompt="Filename",
    default="table.md",
)
@click.option(
    "-p",
    "--pattern",
    help="Define if must be use a pattern in the commit messages",
    is_flag=True,
    default=False,
    type=bool,
)
@cli.command()
def table(owner: str, repo: str, filename: str, pattern: bool) -> None:
    github_service = GithubService()
    markdown_service = MarkdownService()

    try:
        repository = github_service.get_repository(repo, owner)
        markdown_service.create_repository_commmits_table(repository, filename, pattern)
    except RepositoryNotFoundError:
        click.echo("Repo not found")


if __name__ == "__main__":
    cli()
