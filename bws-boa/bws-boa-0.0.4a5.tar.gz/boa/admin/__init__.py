from flask import current_app, send_file, abort
from flask_admin import expose, AdminIndexView
import flask_admin
import logging
import requests as http
from .urls import *
from .view import *
# import importlib
import tarfile
import os
import io
import inspect
import zlib
from .view import BaseFrontendView, BaseView


logger = logging.getLogger("Boot Admin")


# Create customized index view class that handles login & registration
class IndexView(AdminIndexView):
    def __init__(self, ctx, *args, **kwargs):
        self.ctx = ctx
        AdminIndexView.__init__(self, *args, **kwargs)

    @expose_json('/')
    def index(self):
        # app = importlib.import_module("app").app
        return {
            "success": True,
            "message": current_app.config["NAME"]
        }
    
    @expose('/dev')
    def get_dev(self):
        return """<pre>Jose Angel Delgado.
       _           _____  ___
      (_)___ _____/ /__ \<  /
     / / __ `/ __  /__/ // / 
    / / /_/ / /_/ // __// /  
 __/ /\__,_/\__,_//____/_/   
/___/                        </pre>      
<style>body{ text-align: center; margin-top: 20% }</style>   
"""

    @expose('/tar/static/dist/<path:url>')
    def get_tar(self, url):
        filename = f"static/dist/{url}"
        buffer = io.BytesIO()
        with tarfile.open(fileobj=buffer, mode="w:gz") as tar:
            tar.add(filename, arcname=os.path.basename(filename))
        buffer.seek(0)
        return send_file(buffer,  mimetype="application/tar+gzip")
    
    @expose('/z/static/dist/<path:url>')
    def get_zlib(self, url):
        filename = f"static/dist/{url}"
        if os.path.exists(filename):
            with open(filename, "rb") as fb:
                return zlib.compress(fb.read(), level=9)
        else:
            return abort(404)

    @expose('/wiki.md')
    def get_wiki(self):
        return """Metodo reservado para responder la wiki. de los servicios """
    
    @expose('/reload')
    def get_reload(self):
        try:
            app = current_app
            # print(self.ctx["frontviews"])
            res = http.post(app.config["REGISTER"], json=self.ctx["frontviews"], verify=False)
            logger.debug(res.content)
            return res.content
        except Exception as e:
            logger.exception(e)
            return "No se pudo registrar"
    
    @expose_json('/__egg__')
    @expose_json('/🥚')
    def get_egg(self):
        return self.ctx.get("frontviews", {})
        
    # @expose_json('/config')
    # def get_config(self):
    #     app = current_app
    #     return app.config
        

class Admin(flask_admin.Admin):
    def __init__(self, ctx={}, *args, **kwargs):
        self.ctx = ctx
        flask_admin.Admin.__init__(self, *args, **kwargs)

    def bootstrap_frontends(self, app=None):
        try:
            if not app:
                app = current_app
            
            logger.debug("register: %s" % app.config.get("REGISTER"))
            logger.debug("ctx: %s" % self.ctx)
            for setup in self.ctx.get("frontviews", []):
                setup["host"] = app.config["MS_HOST"]
            if self.ctx.get("frontviews") and app.config.get("REGISTER"):
                res = http.post(app.config["REGISTER"], json=self.ctx["frontviews"], verify=False)
                logger.debug(res.content)
                return res.content

        except Exception as e:
            logger.exception(e)
            return "No se pudo registrar"

    def register_frontend(self, view, endpoint=""):
        # app = self.app
        try:

            frontviews = self.ctx.get("frontviews", [])
            if inspect.isclass(view):
                view = view(endpoint=endpoint, name=endpoint)

            endpoint = view.endpoint or endpoint or endpoint.__class__.__name__.lower()
            
            if endpoint.endswith("/"):
                endpoint = endpoint[:-1]
            
            logger.debug("endpoint: %s" % endpoint)
            self.add_view(view)
            setup = {
                # "host": app.config["MS_HOST"],
                "name": view.name,
                "ico": view.ico,
                "kwargs": getattr(view, "kwargs", {}),
                "endpoint": {
                    "frontend": view.endpoint_frontend,
                    "api": view.endpoint_api or '/',
                    "js": f"{endpoint}/js",
                    "css": f"{endpoint}/css",
                    "ctx": f"{endpoint}/ctx",

                }
            }
            frontviews += [setup]
            self.ctx["frontviews"] = frontviews 
            # print(self.ctx["frontviews"])
        except Exception as e:
            logger.exception(e)

    def register_api(self, view, endpoint="", *args, **kargs):
        endpoint = endpoint or endpoint.__class__.__name__.lower()
        if inspect.isclass(view):
            view = view(endpoint=endpoint, *args, **kargs)
        self.add_view(view)

    def expose(self, url):
        def decorator(klass):
            
            if issubclass(klass, BaseFrontendView):
                self.register_frontend(klass, url)
            elif issubclass(klass, BaseView):
                self.register_api(klass, url)
                 
            return klass
        return decorator 


def create_admin(app=None, **kwargs):
    # Create admin
    ctx = {}
    return Admin(ctx, app, 'MS',
        url="/",
        endpoint="index",
        index_view=IndexView(ctx, url="/", endpoint="index"),
        **kwargs
    )
