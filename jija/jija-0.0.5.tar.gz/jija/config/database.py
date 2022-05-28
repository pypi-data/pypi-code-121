from jija.config.base import Base


class DatabaseConfig(Base):
    DATABASE = None
    PASSWORD = None
    USER = None
    PORT = None
    HOST = None

    APPS = None
    CONNECTION_LINK = None

    def __init__(self, *, database, password, host='localhost', user='postgres', port=5432, **kwargs):
        DatabaseConfig.DATABASE = database
        DatabaseConfig.PASSWORD = password
        DatabaseConfig.USER = user
        DatabaseConfig.PORT = port
        DatabaseConfig.HOST = host

        DatabaseConfig.CONNECTION_LINK = f'postgres://{user}:{password}@{host}:{port}/{database}'
        super().__init__(**kwargs)

    @classmethod
    def load(cls):
        from jija.apps import Apps
        cls.APPS = {}
        for app in Apps.apps.values():
            if app.database:
                cls.APPS[app.name] = {
                    "models": app.database_config,
                    "default_connection": "default",
                }

    @classmethod
    def get_config(cls):
        return {
            "connections": {
                "default": cls.CONNECTION_LINK
            },

            "apps": cls.APPS,

            'use_tz': False,
            'timezone': 'Asia/Yekaterinburg'
        }
