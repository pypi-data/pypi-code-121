# -*- coding:utf-8 -*-
'''
Basic root blueprint entry point.
'''
from .common import conf, pb_root
from .backend import init_db


def setup_conf(**config):
    '''
    write config to conf module
    '''
    for k, v in config.items():
        setattr(conf, k, v)


def setup_flask(flask_app, url_prefix="/pb"):
    '''
    Setup flask, register perm_broker as a blueprint.
    '''
    # import sub level path routings
    from .user.views import api as user_api
    from .auth.views import api as auth_api
    from .auth.views import web as auth_web
    from .perm.views import api as perm_api

    # enable debug login
    if conf.DEBUG and getattr(conf, 'ENABLE_DEBUG_LOGIN', False):
        from .auth.views import debug_api

    # bind perm broker blueprint
    flask_app.register_blueprint(pb_root, url_prefix=url_prefix)


def setup_perm_broker(flask_app, url_prefix="/pb", **config):
    '''
    Setup perm broker.
    '''
    setup_conf(**config)
    init_db(**config)
    setup_flask(flask_app, url_prefix=url_prefix)


__ALL__ = ['pb_root', 'conf', 'init_db', 'setup_perm_broker']
