import logging
from json import load
from os import environ
from typing import Optional

import click
from click import Context

from ..const import ACCESS_TOKEN_KEY, NO_TOKEN_TEXT
from ..menu import LineRichMenu

logger = logging.getLogger("LineRichMenu")


@click.group(context_settings={"show_default": True})
@click.option(
    "-t",
    "--token",
    required=False,
    type=str,
    envvar=ACCESS_TOKEN_KEY,
    help=f"Channel access token, can be set via {ACCESS_TOKEN_KEY} environment variable",
    default=lambda: environ.get(ACCESS_TOKEN_KEY, ""),
)
@click.pass_context
def main_cli(ctx: Context, token: Optional[str]):
    if token is None:
        logger.error(NO_TOKEN_TEXT)
        exit(1)
    ctx.ensure_object(dict)
    ctx.obj[ACCESS_TOKEN_KEY] = token


@main_cli.command()
@click.option(
    "-d",
    "--data",
    type=click.Path(exists=True),
    help="Rich menu object in json format, see https://developers.line.biz/en/reference/messaging-api/#rich-menu-object",
)  # noqa
@click.option("-i", "--image", type=click.Path(exists=True))
@click.option("--default", type=bool, default=False, help="Set menu as default")
@click.option(
    "-t",
    "--token",
    required=False,
    type=str,
    envvar=ACCESS_TOKEN_KEY,
    help=f"Channel access token, can be set via {ACCESS_TOKEN_KEY} environment variable",
    default=lambda: environ.get(ACCESS_TOKEN_KEY, ""),
)
@click.pass_context
def create(ctx: Context, data: str, image: str, default: bool):
    token = ctx.obj.get(ACCESS_TOKEN_KEY)
    with open(data, "r") as f:
        data_dict = load(f)
    tool = LineRichMenu(token=token)
    menu_id = tool.create_menu(data=data_dict, image_path=image, set_default=default)
    click.echo(menu_id)


if __name__ == "__main__":
    main_cli(obj={})
