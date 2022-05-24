"""Commandline interface for the library."""
import textwrap
from random import randint
from typing import List

import click
from arkhamdb import __version__
from arkhamdb.utils import async_command
from httpx import AsyncClient, Response

API_URL = "https://arkhamdb.com/api"


@click.command()
@click.version_option(version=__version__)
@async_command
async def main():
    """Commandline interface for a utility tool that provides a pythonic interface for the excellent ArkhamDB.com."""  # noqa: E501
    click.echo("Obtaining latest cards list from ArkhamDB.com ...")

    async with AsyncClient(
        base_url=API_URL,
        headers={"Content-Type": "application/json"},
        follow_redirects=True,
    ) as client:
        try:
            res: Response = await client.get("public/cards")
            cards: List[dict] = res.json()
            click.secho(f"Remote database contains {len(cards)} cards.", fg="green")
            click.echo(textwrap.fill("========================================"))
            i = randint(0, len(cards) - 1)  # nosec # noqa
            example = cards[i]
            click.echo(f"{example['name']} | {example['faction_name']}")
            click.echo(textwrap.fill("========================================"))
            click.echo(f"Description: {textwrap.fill(example['text'])}")
        except Exception as e:
            msg = str(e)
            raise click.ClickException(msg) from e
