template="""
from app import cmd, app
import click

'''
    boa cmd %(app)s__create abc
'''
@cmd.command("%(app)s__create")
@click.argument('arg')
def %(app)s__create(arg):
    app.logger.info(arg)

"""