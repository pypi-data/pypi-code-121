#!/usr/bin/env python
# -*- coding: utf-8 -*-

import gunicorn.app.wsgiapp

class StandaloneApplication(gunicorn.app.wsgiapp.WSGIApplication):
    """
    Custom application
    """

    def init(self, parser, opts, args):
        self.cfg.set("default_proc_name", self.app_uri)
        # self.app_uri = args[0]
        pass

    def __init__(self, appuri, options=None):
        self.options = options or {}
        self.app_uri = appuri
        super(StandaloneApplication, self).__init__()

    def load_config(self):
        config = dict([(key, value) for key, value in self.options.items()
                       if key in self.cfg.settings and value is not None])
        for key, value in config.items():
            self.cfg.set(key.lower(), value)

def start_main_loop(appuri, name='app', workers=1, port=8080, **kwargs):
    default_options = {
        'bind': '0.0.0.0:%d' % port,
        'workers': workers,
        'backlog': 2048,
        'worker_class': "tornado",
        'worker_connections': 1000,
        'daemon': False,
        'debug': False,
        'preload': True,
        'proc_name': name,
        'errorlog': './log/%s-error.log' % name,
        'accesslog': './log/%s-access.log' % name,
    }
    options = dict([(key, value) for key, value in kwargs.items()
                    if key in default_options and value is not None])
    sl_app = StandaloneApplication(appuri, options=options)
    sl_app.run()
