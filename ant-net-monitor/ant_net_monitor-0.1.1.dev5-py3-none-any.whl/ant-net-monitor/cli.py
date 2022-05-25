import click
from flask.cli import with_appcontext
from .extensions import db

@click.command("init")
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    db.drop_all()
    db.create_all()
    click.echo('Application inited.')
