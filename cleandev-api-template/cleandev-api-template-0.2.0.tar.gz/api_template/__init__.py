import inspect
import pkgutil
import importlib

import flask
from flask import Flask
from flask import Response
from flask_cors import CORS
from flask_restful import Api
from api_template.config import _debug
from flask_jwt_extended import JWTManager
from api_template.config import _app_name
from api_template.inmutables import _Params
from api_template.inmutables import _ClassName
from api_template.inmutables import _Properties
from api_template.config import _jwt_secret_key
from properties_loader import PropertiesClassLoader
from api_template.config import _propagate_exceptions
from api_template.config import _jwt_access_token_expires
from api_template.config import _jwt_refresh_token_expires
from api_template.inmutables import _PropertiesGroups
from api_template.config import _path_resources_api


class ResourceBuilder(PropertiesClassLoader):

    def __init__(self, **kwargs):
        super(ResourceBuilder, self).__init__(groups=kwargs.get(_Params.GROUPS))
        self.__load_resources(kwargs.get(_Params.API))

    def __load_resources(self, api: Api):
        list_modules: list = self.__list_modules()
        for module_path in list_modules:
            module = importlib.import_module(module_path)
            for name, obj in inspect.getmembers(module):
                if inspect.isclass(obj) and obj.__base__.__name__ == _ClassName.RESOURCE_CLASS_NAME:
                    api.add_resource(obj, *obj.endpoint())

    def __list_modules(self):
        list_modules: list = []
        module_base: str = f"{_path_resources_api}"
        list_modules.append(module_base)
        module = importlib.import_module(module_base)
        for modname in pkgutil.iter_modules(module.__path__):
            list_modules.append(f"{module_base}.{modname.name}")
        return list_modules


class ApiFactory(PropertiesClassLoader):

    def __init__(self):
        super(ApiFactory, self).__init__(groups=[_PropertiesGroups.API_TEMPLATE])
        self._app: Flask = self.__build_app
        self.__build_jwt_manager(self._app)
        self.__build_api()

    def __build_jwt_manager(self, app):
        jwt_manager: JWTManager = JWTManager(app)

        # Overwirte Callback -----
        @jwt_manager.expired_token_loader
        def expired_token_callback(jwt_header, jwt_payload):
            data: dict = {}
            return Response(data, status=401, mimetype='application/json')

        # Overwirte Callback -----
        return jwt_manager

    @property
    def __build_app(self):
        api_flask = Flask(_app_name)
        api_flask.config['JWT_SECRET_KEY'] = _jwt_secret_key
        api_flask.config['PROPAGATE_EXCEPTIONS'] = _propagate_exceptions
        api_flask.config['JWT_ACCESS_TOKEN_EXPIRES'] = _jwt_access_token_expires
        api_flask.config['JWT_REFRESH_TOKEN_EXPIRES'] = _jwt_refresh_token_expires
        api_flask.debug = _debug
        CORS(api_flask)
        return api_flask

    def __build_api(self):
        api: Api = Api(self._app)
        ResourceBuilder(api=api, groups=[_PropertiesGroups.API_TEMPLATE])
        return api

    @property
    def app(self):
        return self._app
