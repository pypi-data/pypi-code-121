import os
import time
import uuid
import platform
import socket

import magic_import

class _None(object):
    pass
_None = _None()


class ServiceBase(object):

    def __init__(self, config=None, namespace=None):
        self.config = config or {}
        if namespace:
            self.namespace = namespace

    def get_config(self, path, default=None):
        return magic_import.select(self.config, path, default)

    def get_ignore_methods(self):
        return [
            "get_config",
            "get_ignore_methods",
            "register_to",
            "get_server_service",
            "get_namespace",
            "get_methods",
        ]

    def register_to(self, server):
        # service instance can only be registered once
        if hasattr(self, "_server"):
            raise Exception("service is already registered...")
        self._server = server
        # register all methods to the server
        for name, method in self.get_methods():
            server.register_function(method, name)
        # keep service instance in server._services
        # service._services[""] will holds all non-namespace services
        if not hasattr(server, "_services"):
            setattr(server, "_services", {})
        services = getattr(server, "_services")
        namespace = self.get_namespace()
        if namespace:
            services[namespace] = self
        else:
            if not "" in services:
                services[""] = []
            services[""].append(self)
        # register done
    
    def get_server_service(self, name):
        if not self._server:
            raise Exception("service is not register to any server...")
        if not hasattr(self._server, "_services"):
            setattr(self._server, "_services", {})
        return self._server._services.get(name, None)

    def get_namespace(self):
        namespace = getattr(self, "namespace", _None)
        if namespace is _None:
            namespace = str(self.__class__.__name__).lower()
            if namespace.endswith("service"):
                namespace = namespace[:-7]
        return namespace

    def get_methods(self):
        methods = []
        ignore_names = self.get_ignore_methods()
        namespace = self.get_namespace()
        for name in dir(self):
            if name in ignore_names:
                continue
            method = getattr(self, name)
            if not name.startswith("_") and callable(method):
                if namespace:
                    name = self.get_namespace() + "." + name
                methods.append((name, method))
        return methods

class DebugService(ServiceBase):

    namespace = "debug"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._counter = 0

    def ping(self):
        return "pong"
    
    def echo(self, msg):
        return msg
    
    def timestamp(self):
        return time.time()
    
    def hostname(self):
        return socket.gethostname()

    def uuid4(self):
        return str(uuid.uuid4())

    def urandom(self, length=32):
        return os.urandom(length)

    def uname(self):
        info = platform.uname()
        uname = {}
        for name in dir(info):
            if name.startswith("_"):
                continue
            value = getattr(info, name)
            if callable(value):
                continue
            uname[name] = value
        return uname

    def true(self):
        return True
    
    def false(self):
        return False

    def null(self):
        return None
    
    def sum(self, *args):
        return sum(args)

    def counter(self):
        self._counter += 1
        return self._counter

    def sleep(self, seconds=30):
        time.sleep(seconds)
        return True

    def raise_error(self):
        """Always raise ZeroDivisionError.
        """
        a = 0
        b = 0
        c = a / b
        return c
