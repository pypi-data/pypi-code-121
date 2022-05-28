import importlib
import os

from aiohttp import web

from jija.middleware import Middleware
from jija.utils.collector import collect_subclasses
from jija.command import Command


class App:
    def __init__(self, *, name, path, aiohttp_app=None, parent=None):
        self.__parent = parent
        if parent:
            parent.add_child(self)

        self.__path = path
        self.__name = name
        self.__is_core = aiohttp_app is not None

        self.__routes = None
        self.__database = None
        self.__middlewares = None
        self.__commands = None

        self.__aiohttp_app = None

        self.__childes = []
        self.__load(aiohttp_app)

    @property
    def parent(self):
        return self.__parent

    @property
    def name(self):
        return self.__name

    @property
    def routes(self):
        return self.__routes

    @property
    def database(self):
        return self.__database

    @property
    def middlewares(self):
        return self.__middlewares

    @property
    def aiohttp_app(self):
        return self.__aiohttp_app

    @property
    def childes(self):
        return self.__childes

    @property
    def path(self):
        return self.__path

    @property
    def commands(self):
        return self.__commands

    @property
    def database_config(self):
        database_modules = ['aerich.models'] if self.__is_core else []

        if self.__database:
            database_modules.append((self.__path + 'database').python)

        return database_modules

    def __load(self, aiohttp_app=None):
        self.__routes = self.__get_routes(self.__path)
        self.__database = self.__get_database(self.__path)
        self.__middlewares = self.__get_middlewares(self.__path)
        self.__commands = self.__get_commands(self.__path)

        self.__aiohttp_app = self.get_aiohttp_app(aiohttp_app)

    @staticmethod
    def __get_routes(path):
        try:
            routes_module = importlib.import_module((path + 'routes').python)
            if not hasattr(routes_module, 'routes'):
                return []
            return getattr(routes_module, 'routes')

        except ImportError or AttributeError:
            return []

    @staticmethod
    def __get_database(path):
        try:
            return importlib.import_module((path + 'database').python)

        except ImportError:
            return None

    @staticmethod
    def __get_middlewares(path):
        try:
            raw_middlewares = importlib.import_module((path + 'middlewares').python)
            middlewares = collect_subclasses(raw_middlewares, Middleware)
            return list(map(lambda item: item(), middlewares))

        except ImportError or AttributeError:
            return []

    @staticmethod
    def __get_commands(path):
        commands = {}
        commands_path = path + 'commands'
        if os.path.exists(commands_path.system):
            for file in os.listdir(commands_path.system):
                if file.endswith('.py') and not file.startswith('_'):
                    command_path = commands_path + file.replace('.py', '')
                    command_module = importlib.import_module(command_path.python)

                    command = list(collect_subclasses(command_module, Command))
                    if command:
                        commands[file.replace('.py', '')] = command[0]

        return commands

    @staticmethod
    def is_app(path):
        return os.path.isdir(path.system) and \
               os.path.exists((path + 'app.py').system) and \
               not path.has_protected_nodes()

    def get_aiohttp_app(self, aiohttp_app=None):
        aiohttp_app = aiohttp_app or web.Application()

        aiohttp_app.middlewares.extend(self.__middlewares)
        aiohttp_app.add_routes(self.__routes)

        return aiohttp_app

    def add_child(self, child):
        self.__childes.append(child)
