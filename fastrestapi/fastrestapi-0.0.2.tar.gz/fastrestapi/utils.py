import importlib
import json
import os
import threading
import urllib.parse
from http import HTTPStatus

_HTTP_STATUS_LINES = {s.value: f"{s.value} {s.phrase}" for s in HTTPStatus}


def status_line(status_code):
    return _HTTP_STATUS_LINES.get(status_code)


def parse_qsl(qs):
    data = {}
    for pair in qs.split("&"):
        if not pair:
            continue
        nv = pair.split("=", 1)
        if len(nv) != 2:
            nv.append("")
        key = urllib.parse.unquote(nv[0].replace("+", " "))
        value = urllib.parse.unquote(nv[1].replace("+", " "))
        data[key] = value
    return data


def local_property():
    ls = threading.local()

    def fget(_):
        try:
            return ls.var
        except AttributeError:
            raise RuntimeError("Request context not initialized.")

    def fset(_, value):
        ls.var = value

    def fdel(_):
        del ls.var

    return property(fget, fset, fdel)


def load(package):
    module_dir = os.getcwd() + "/" + package.replace(".", "/")
    for module_file in os.listdir(os.path.abspath(module_dir)):
        if module_file[-3:] == ".py" and module_file != "__init__.py":
            module_name = package + "." + module_file[:-3]
            importlib.import_module(module_name)


def toJsonString(data):
    json.dumps(data, ensure_ascii=False)


def parseJsonObject(s):
    return json.loads(s)
