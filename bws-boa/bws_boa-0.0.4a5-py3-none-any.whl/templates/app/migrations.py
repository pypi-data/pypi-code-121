template="""
from app import db, migrate
from .models import ExampleModel

'''
    boa migrate %(app)s__create_table
'''

@migrate.command
def %(app)s__create_table():
    return ExampleModel.__table__.create(db.get_engine())

"""