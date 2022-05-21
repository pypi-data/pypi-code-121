import click
from modelify import run_server
from modelify import pull as pull_model
from modelify.version import VERSION

@click.group()
@click.version_option(VERSION)
def cli():
    pass

@click.command()
@click.option('--port',  help='Port Number')
@click.option('--host', help='Host Name')
def runserver(port, host):
    """To run your modelify app"""
    if port:
         run_server(port=int(port), tunnel=False)
    else:
        run_server(tunnel=False)

@click.command()
@click.argument("app_uid", required=True )
@click.option('--version',  help='Port Number')
def pull(app_uid, version):
    """Pull your modelify app from Modelify Cloud"""
    pull_model(app_uid=app_uid, version=version)


cli.add_command(runserver)
cli.add_command(pull)

if __name__ == '__main__':
    cli()