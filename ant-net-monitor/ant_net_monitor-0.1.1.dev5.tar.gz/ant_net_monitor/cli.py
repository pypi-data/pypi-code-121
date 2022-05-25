import os
import click
from flask.cli import with_appcontext
from .extensions import db

@click.command("init")
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Application inited.')

def init_db():
    # if database file folder doesn't exists
    if not os.path.exists(os.path.dirname(db.engine.url.database)):
        os.makedirs(os.path.dirname(db.engine.url.database))
    db.create_all()
