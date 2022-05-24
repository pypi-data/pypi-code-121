import click

from .service.github_service import GithubService
from .service.markdown_service import MarkdownService
from .errors.github_errors import RepositoryNotFoundError


@click.group()
def cli() -> None:
    ...


@click.option("--owner", help="The repository owner", prompt="Owner")
@click.option("--repo", help="The reposiotry name", prompt="Repo")
@click.option(
    "--filename", help="The markdown filename", prompt="Filename", default="table.md"
)
@cli.command()
def table(owner: str, repo: str, filename: str) -> None:
    github_service = GithubService()
    markdown_service = MarkdownService()

    try:
        repository = github_service.get_repository(repo, owner)
        markdown_service.create_repository_commmits_table(repository, filename)
    except RepositoryNotFoundError:
        click.echo("Repo not found")


if __name__ == "__main__":
    cli()
