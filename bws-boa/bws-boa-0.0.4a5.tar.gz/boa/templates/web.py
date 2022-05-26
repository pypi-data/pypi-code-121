template = """

from app import create_app
from boa.admin.bootstrap import bootstrap

config_file = os.getenv('APP_CONFIG_FILE', "app.config.py")


bootstrap(app, admin, ["config", "api"])
admin = create_app(app)


from app import create_app, admin
from boa.admin.bootstrap import bootstrap


config_file = os.getenv('APP_CONFIG_FILE', "app.config.py")
app = create_app()
bootstrap(app, admin, ["config", "view", "routes"])

if __name__ == '__main__':    
    app.run(host=app.config["HOST"], port=app.config["PORT"])

"""
