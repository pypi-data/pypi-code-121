from flask import jsonify, request, make_response, current_app
from flask_admin.base import BaseView
from .urls import expose
import requests as http
import os
import re
import json
from urllib.parse import urljoin
import zlib
import logging


logger = logging.getLogger(__name__)

'''
    admin.add_view(MyView(name='My View', menu_icon_type='glyph', menu_icon_value='glyphicon-home'))

'''

STATIC_PATH = current_app.config["STATIC_PATH"]


to_dict = lambda obj: {k: v for k, v in (obj or {}).items()}


class FacadeView(BaseView):
    '''
        setup = {
            host: microservice return,
            endpoint: {
                frontend: path module or FacadeView.endpoint,
                api: path api,
                js: path js,
                css: path js,
                ctx: path ctx,
            },
            name: name view,
            ico: ico class
        }
    '''

    def __init__(self, setup, *args, **kargs):
        self.setup = setup
        self.template = kargs.pop("template", "admin/template_ctx.html")
        BaseView.__init__(self, *args, **kargs)
    
    def current_user(self):
        """
        docstring
        """
        raise NotImplementedError
    
    def user_dict(self):
        """
        docstring
        """
        raise NotImplementedError
    
    def is_accessible(self):
        raise NotImplementedError

    def _get_dependences(self, type="js"):
        module = re.sub(r"[^\d\w]", "", self.setup["endpoint"]["frontend"].replace("/", "_"))
        path_js = self.setup["endpoint"].get(type, "")
        if not path_js:
            return []
        url = urljoin(self.setup["host"], path_js)
        res_api = http.get(url)
        array_js = res_api.json()
        path_module = os.path.join(STATIC_PATH, os.path.join("dist", module))
        path_module_relative = os.path.join("/static/dist/", module)
        path_manifest = os.path.join(path_module, "manifest.json")
        
        if not os.path.exists(path_module):
            print(":::::USER::", os.getenv("USER"))
            os.mkdir(path_module)

        if os.path.exists(path_manifest):
            manifest = json.load(open(path_manifest, "r"))
        else:
            manifest = {}

        array_js_final = []
        manifest_update = False
        for js in array_js:
            url_js = urljoin(self.setup["host"], js)
            res = http.head(url_js)
            basename = os.path.basename(js)
            path_js = os.path.join(path_module, basename)
            if manifest.get(basename, "") != res.headers["ETag"]:
                manifest_update = True
                manifest[basename] = res.headers["ETag"]
                with open(path_js, "wb+") as f:
                    url_js_tar = urljoin(self.setup["host"], f"z/{js}")
                    res_targz = http.get(url_js_tar)
                    f.write(zlib.decompress(res_targz.content))
                
            array_js_final += ["{}/{}?v={}".format(path_module_relative, basename, str(manifest[basename]))]
        
        if manifest_update:
            json.dump(manifest, open(path_manifest, "w"))

        return array_js_final

    @property
    def extra_js(self):
        return self._get_dependences("js")
    
    @property
    def extra_css(self):
        return self._get_dependences("css")

    @expose('/<path:url>', methods=["GET", "POST", "PUT", "DELETE", "HEAD"])
    def mirror_api(self, url):
        user = self.current_user()
        path_api = self.setup["endpoint"]["api"]
        host = urljoin(self.setup["host"], path_api)
        # logger.info("ms.api: %s" % url)
        url = urljoin(host, url)
        # logger.info("ms.api.join: %s" % url)
        # logger.info("ms.api.method: %s" % request.method)
        try:
            headers = to_dict(request.headers)

            if request.method.lower() in ["post", "put", "delete"]:
                http_action = getattr(http, request.method.lower(), None)

                try:
                    params_args = to_dict(request.args)
                except:
                    params_args = {}
                try:
                    params_json = to_dict(request.json)
                except:
                    params_json = {}
                
                try:
                    params_files = request.files
                except:
                    params_files = None

                res_api = http_action(
                    url=url,
                    params=params_args,
                    json=params_json,
                    files=params_files,
                    # data=request.form,
                    headers=headers)
            else:
                res_api = http.get(url, params=request.args, headers=headers)
                res_api.content
        
            response = make_response(res_api.content, res_api.status_code)
            for k, v in res_api.headers.items():
                response.headers[k] = v
            return response
        except Exception as e:
            logger.exception(e)
            return jsonify({"success": True, "message": str(e)})
    
    def _get_context(self):
        """
            Obtener el contexto
        """
        path_ctx = self.setup["endpoint"].get("ctx", "")

        url = urljoin(self.setup["host"], path_ctx)
        headers = to_dict(request.headers)
        res = http.get(url, headers=headers)
        if res.status_code == 200:
            return res.json()
        return {}
    
    @expose('/')
    def index(self):
        user = self.current_user()
        res = self.render(self.template, i18n=dict(), ctx=self._get_context())
        res = make_response(res)
        ''' Registramos el user de la sesion para el WS ''' 
        res.set_cookie('user_id', str(user.get_id()))
        return res 
    
    @expose('/setup')
    def get_setup(self):
        return jsonify(self.setup)
