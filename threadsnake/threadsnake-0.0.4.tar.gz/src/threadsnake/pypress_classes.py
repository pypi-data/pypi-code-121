##    threadsnake. A tiny experimental server-side express-like library.
##    Copyright (C) 2022  Erick Fernando Mora Ramirez
##
##    This program is free software: you can redistribute it and/or modify
##    it under the terms of the GNU General Public License as published by
##    the Free Software Foundation, either version 3 of the License, or
##    (at your option) any later version.
##
##    This program is distributed in the hope that it will be useful,
##    but WITHOUT ANY WARRANTY; without even the implied warranty of
##    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##    GNU General Public License for more details.
##
##    You should have received a copy of the GNU General Public License
##    along with this program.  If not, see <https://www.gnu.org/licenses/>.
##
##    mailto:erickfernandomoraramirez@gmail.com

from cgitb import reset
from dataclasses import replace
from functools import reduce
import json
from sys import path
from types import FunctionType
from typing import Any, Callable, Dict, List, Union

from .myhttp import Server, HttpRequest, HttpResponse, Session, RequestSession
from base64 import b64decode
from uuid import uuid4
import os
import re
import time
from importlib import __import__ as importpy
import importlib.util



'''
Loads a library from specified path.
Thanks to 
[[https://stackoverflow.com/users/7779/sebastian-rittau|Sebastian Rittau|target="_blank"]] and 
[[https://stackoverflow.com/users/3907364/raven|Raven|target="_blank"]]
'''
def import_library(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

class RouterTemplate:
    def __init__(self) -> None:
        self.R:Router = None 

def load_router(name, path) -> RouterTemplate:
    return import_library(name, path)

def routes_to(name:str):
    path = name if name.endswith('.py') else name + '.py'
    libName = 'lib'+str(uuid4()).replace('-', '')
    return load_router(libName, path).R

def load_routers(folder:str = 'routers', onExcept:Callable = None):
    result = {}
    for f in [(i[:-3], os.sep.join(folder, i)) for i in os.listdir(folder) if i.endswith('.py')]:
        try:
            result = result[f[0]] = load_router(f[0], f[1]).R
        except Exception as e:
            if onExcept is not None:
                onExcept(e)
    return result

class Router:
    def __init__(self):
        #print('router created')
        self.routes = {}
        self.callbackMutator:CallbackMutator = lambda a: a

    def register_function(self, httpMethod:str, route:str):
        ref:Router = self
        def inner(function:Callback) -> Callback:
            function = self.callbackMutator(function)
            if httpMethod.upper() not in ref.routes:
                ref.routes[httpMethod.upper()] = {route: function}
            else:
                ref.routes[httpMethod.upper()][route] = function
            return function
        return inner
    
    def use_globally(self, mutator):
        callbackMutator = self.callbackMutator
        def innerMutator(c):
            return mutator(callbackMutator(c))
        self.callbackMutator = innerMutator
        return self

    def get(self, route):
        return self.register_function('GET', route)

    def post(self, route):
        return self.register_function('POST', route)
    
    def put(self, route):
        return self.register_function('PUT', route)
    
    def delete(self, route):
        return self.register_function('DELETE', route)

    def configure(self, handler):
        self.stack.append(handler)
        return self

    def use_router(self, router, root):
        for method in router.routes:
            for action in router.routes[method]:
                self.register_function(method,f'{root}{action}')(router.routes[method][action])
                #if method not in self.routes:
                #    self.routes[method] = {}
                #self.routes[method][f'{root}{action}'] = router.routes[method][action]
        return self

    def serve_statically(self, route:str, content:Union[str, Callable[[Any, HttpRequest, HttpResponse],str]], encoding:str=None):
        def sub(s:str, ss:str)->str:
            return s if ss not in s else s[s.index(ss)+1:]
        fileName = sub(sub(route, '/'), '\\')
        def callback(app:Application, req:HttpRequest, res:HttpResponse):
            data = content if isinstance(content, str) else content(app, req, res)
            res.transmit_as_file(fileName, data, encoding=encoding)
        self.get(route)(callback)
        return self

    def __getattr__(self, method):
        def inner(route):
            return self.register_function(method.upper(), route)
        return inner


class Application(Server, Router):
    def __init__(self, port, connectionTimeout=None):
        Server.__init__(self, port, connectionTimeout)
        Router.__init__(self)
        self.stack = []
        self.session:RequestSession = None
        
    def cli_loop(self, main_event: Callable):
        self.start()
        continueLoop = True
        while(continueLoop):
            try:
                continueLoop = main_event()
            except KeyboardInterrupt as e:
                print('[CLI EXIT]')
                break
            finally:
                self.stop()
                
    def wait_exit(self, message:str = 'press [Enter] to exit...'):
        try:
            self.start()
            input(message)
        except:
            pass
        finally:
            self.stop()

    def onReceive(self, clientPort, data, clientAddress):
        if(len(data) == 0): return
        req = None
        res = HttpResponse()
        try:
            req = HttpRequest(data, clientAddress)
        except Exception as e:
            print(e)
            print(data)
            res.status(403, "BadRequest")
            clientPort.send(str(res).encode())
            return

        stack = self.stack.copy()

        def next():
            if len(stack) > 0 and not res.ended:
                stack.pop()(self, req, res, next)
        
        if ':' in req.path:
            pathParts = req.path.split('/')
            newPath = []
            for i in pathParts:
                queryPassParam = i.split(':')
                if len(queryPassParam) == 2:
                    req.params[queryPassParam[0]] = queryPassParam[1]
                else:
                    newPath.append(i)
            req.path = '/'.join(newPath)

        if req.method in self.routes:
            regularPaths = [i for i in self.routes[req.method]]
            for route in regularPaths:
                pattern = re.sub(r"\{([\w]+)\:int\}", r"(?P<\1>[-]?[\\d]+)", route)
                pattern = re.sub(r":([\w]+)", r"(?P<\1>[\\w]+)", pattern)
                pattern = "^" + pattern + "$"
                match = re.match(pattern, req.path)
                if match:
                    handler = self.routes[req.method][route]
                    queryParams = match.groupdict()
                    for i in queryParams:
                        req.params[i] = queryParams[i]
                    def middleware(app, req, res, next):
                        res.status(200)
                        handler(app, req, res)
                        next()
                    stack.append(middleware)
                    break

        stack.reverse()
        next()
        data = str(res).encode(res.encoding or 'latin1') #str(res).encode() if res.encoding is None else str(res).encode(res.encoding)
        clientPort.send(data)

Middleware = Callable[[Application, HttpRequest, HttpResponse, Callable[[], None]], None]
Callback = Callable[[Application, HttpRequest, HttpResponse], None]
ServerCallback = Callable[[HttpRequest, HttpResponse], None]
DictProvider = Callable[[], Dict[str, Any]]
CallbackMutator = Callable[[Callback], Callback]

def build_application(port: int, middlewares: List[Middleware], routers: Dict[str, Router]):
    app = Application(port)
    for m in middlewares:
        app.configure(m)
    for r in routers:
        app.use_router(routers[r], r)
    return app

def create_server(port:int, callback:ServerCallback) -> Application:
    app = Application(port)
    def innerMiddleware(application:Application, req:HttpRequest, res:HttpResponse, next):
        callback(req, res)
        next()
    app.configure(innerMiddleware)
    return app