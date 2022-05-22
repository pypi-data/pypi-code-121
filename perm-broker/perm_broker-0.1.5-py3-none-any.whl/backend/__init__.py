class DbBridge(object):
    models = None
    helper = None

    def __getattr__(self, name):
        if hasattr(self.models, name):
            return getattr(self.models, name)
        else:
            return getattr(self.helper, name)

db = DbBridge()


def init_db(**config):
    backend_type = config.get('BACKEND_TYPE')
    if backend_type == 'mongodb':
        import mongoengine
        mongoengine.register_connection(config['MONGO_ALIAS'],
                                        **config['MONGO'])
        from .mongodb import models
        from .mongodb import helper
        db.models = models
        db.helper = helper
        return db
    elif backend_type == 'mssql':
        from sqlalchemy import create_engine
        from sqlalchemy.orm import scoped_session, sessionmaker
        engine = create_engine(config['CONNECTION_STRING'], **config['SA_ENGINE_ARGS'])
        session = scoped_session(sessionmaker(bind=engine))
        from .mssql import models
        from .mssql import helper
        models.engine = helper.engine = engine
        models.session = helper.session = session
        db.models = models
        db.helper = helper
        return db
    elif backend_type == 'mysql':
        from sqlalchemy import create_engine
        from sqlalchemy.orm import scoped_session, sessionmaker
        engine = create_engine(config['CONNECTION_STRING'], **config['SA_ENGINE_ARGS'])
        session = scoped_session(sessionmaker(bind=engine))
        from .mysql import models
        from .mysql import helper
        models.engine = helper.engine = engine
        models.session = helper.session = session
        db.models = models
        db.helper = helper
        return db
    else:
        pass
