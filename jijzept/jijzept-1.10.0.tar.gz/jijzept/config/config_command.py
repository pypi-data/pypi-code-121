import click

from jijzept.config.handle_config import (
    CONFIG_PATH,
    DEFAULT_CONFIG_FILE,
    HOST_URL,
    create_config,
)


@click.group()
def main():
    pass


@main.command()
def create():
    click.echo("--- Welcome to JijZept ---")
    config_path = click.prompt(
        "Please enter the configuration path", default=CONFIG_PATH
    )
    host_url = click.prompt("Please enter the your API's URL", default=HOST_URL)
    token = click.prompt("Please eneter the your token (subscription key)")
    config_file_name = create_config(token, host_url, config_path)
    click.echo("Config file path {}".format(config_file_name))
    click.echo("----- Thank you -----")


@main.command()
def show():
    click.echo(
        "JijZept's default configuration path: {}".format(
            CONFIG_PATH + DEFAULT_CONFIG_FILE
        )
    )

    with open(CONFIG_PATH + DEFAULT_CONFIG_FILE, "r") as f:
        config_str = f.read()

    click.echo("-------------------")
    click.echo(config_str)
    click.echo("-------------------")


if __name__ == "__main__":
    main()
