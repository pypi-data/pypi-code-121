#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tornado.web
from .asynchttphandler import routes

class WebApplication(tornado.web.Application):
    """
    """
    
    def __init__(self, handlers=None, default_host=None, transforms=None, **settings):
        if not handlers:
            handlers = routes.routes
        return super().__init__(handlers=handlers, default_host=default_host, transforms=transforms, **settings)
