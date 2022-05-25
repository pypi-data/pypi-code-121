import click
import sys
import yaml
import subprocess
from pkg_resources import resource_filename
from pathlib import Path
from django.core import management
from django.core.management.base import CommandError
from . import __version__


# click entrypoint
@click.group()
@click.version_option(__version__)
def main():

    """DjangoLDP CLI"""


@main.command()
@click.argument('name', nargs=1, required=False)
def initserver(name):

    """Start a DjangoLDP server."""

    try:
        # use directly pwd
        directory = Path.cwd()

        if name:
            # create a directory from project name in pwd
            directory = Path.cwd() / name
            directory.mkdir(parents=False, exist_ok=False)

        # get the template path
        template = resource_filename(__name__, 'conf/server_template')

        # wrap the default django-admin startproject command
        # this call import django settings and configure it
        # see: https://docs.djangoproject.com/fr/2.2/topics/settings/#calling-django-setup-is-required-for-standalone-django-usage
        # see: https://github.com/django/django/blob/stable/2.2.x/django/core/management/templates.py#L108
        # fix: in 2.2 gabarit files options has been renamed: https://github.com/django/django/blob/stable/2.2.x/django/core/management/templates.py#L53
        management.call_command('startproject', name, directory, template=template, files=['settings.yml'])

    except FileExistsError:
        click.echo(f'Error: the folder {directory} already exists')
        sys.exit(1)

    except CommandError as e:
        click.echo(f'Error: {e}')
        directory.rmdir()
        sys.exit(1)

@main.command()
@click.argument('name', nargs=1)
def startpackage(name):

    """Start a DjangoLDP package."""

    try:
        # set directory
        directory = Path.cwd() / name

        # get the template path
        template = resource_filename(__name__, 'conf/package_template')

        # create dir
        directory.mkdir(parents=False, exist_ok=False)

        # wrap the default startapp command
        management.call_command('startapp', name, directory, template=template)

    except FileExistsError:
        click.echo(f'Error: the folder {directory} already exists')
        sys.exit(1)

    except CommandError as e:
        click.echo(f'Error: {e}')
        sys.exit(1)

@main.command()
def install():

    """Install project dependencies."""

    try:
        # load dependencies from config file
        path = Path.cwd() / 'settings.yml'
        with open(path, 'r') as f:
            dependencies = yaml.safe_load(f).get('dependencies', [])

        # install them by calling pip command
        cmd = [sys.executable, "-m", "pip", "install", "--upgrade"]
        try:
            cmd.extend(dependencies)
            subprocess.run(cmd).check_returncode()
            click.echo('Installation done!')
        except TypeError:
            click.echo('No dependency to install')

    except FileNotFoundError:
        click.echo('Config error: no settings.yml file in this directory')
        sys.exit(1)

    except subprocess.CalledProcessError as e:
        click.echo(f'Installation error: {e}')
        sys.exit(1)


@main.command()
@click.option('--with-admin', 'admin', help='Create an administrator user with email.')
@click.option('--email', help='Provide an email for administrator.')
@click.option('--with-dummy-admin', 'dummy_admin', is_flag=True, help='Create a default "admin" user.')
def configure(admin, dummy_admin, email):

    """Configure the project."""

    try:
        # shortcut to the djangoldp.management command
        path = str(Path.cwd() / 'manage.py')
        cmd = [sys.executable, path, 'configure']
        if admin:
            if not email:
                click.echo('Error: missing email for admin user')
                return
            cmd.extend(['--with-admin', admin, '--email', email])
        elif dummy_admin:
            cmd.append('--with-dummy-admin')
        subprocess.run(cmd).check_returncode()

        click.echo('Confguration done!')

    except subprocess.CalledProcessError as e:
        click.echo(f'Configuration error: {e}')
        sys.exit(1)


@main.command()
def runserver():

    """Run the Django embeded webserver."""

    try:
        # shortcut to the djangoldp.management command
        path = str(Path.cwd() / 'manage.py')
        cmd = [sys.executable, path, 'runserver', '0.0.0.0:8000']
        subprocess.run(cmd).check_returncode()

    except subprocess.CalledProcessError as e:
        click.echo(f'Execution error: {e}')
        sys.exit(1)
