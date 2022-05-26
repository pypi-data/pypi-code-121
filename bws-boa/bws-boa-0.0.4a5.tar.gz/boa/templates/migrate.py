template="""
from app import app, migrate
from boa.admin.bootstrap import bootstrap


bootstrap(app, None, ["migrations"])


if __name__== '__main__':
    migrate.run()

"""
    