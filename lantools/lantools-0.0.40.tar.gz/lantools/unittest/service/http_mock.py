
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import functools
import requests

store = []
routers = {}

def route(path):
    def decorator(function):
        routers[path] = function

        @functools.wraps(function)
        def wrapper(*args, **kwargs):
            #print(function)
            return function(*args, **kwargs)

        return wrapper

    return decorator   

class BaseMock(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(bytes(json.dumps(store), encoding='utf-8'))

        while len(store)>0:
            store.pop()

    def do_POST(self):
        path = self.path
        body = self.rfile.read(int(self.headers['content-length']))
        body = json.loads(str(body, encoding='utf-8'))

        store.append({
            "path": path,
            "body": body,
        })
        #print(path, body)

        if path in routers:
            text = routers.get(path)(self, body)

            self.send_response(200)
            self.end_headers()
            self.wfile.write(bytes(json.dumps(text), encoding='utf-8'))
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'404')


class HTTP:
    def __init__(self, host='127.0.0.1', port=80):
        self.host = host
        self.port = port

    def run(self, handler):
        server = HTTPServer((self.host,self.port), handler)
        server.serve_forever()  


class Result:
    def __init__(self, path, body):
        self.path = path
        self.body = body

class HttpMock:
    def __init__(self, *, host="127.0.0.1", port=80, path="/"):
        self.host = host
        self.port = port
        self.path = path

    def get_result(self) -> Result:
        return self._do_request()

    def clear(self):
        self._do_request()

    def _do_request(self):
        url = "http://{}:{}{}".format(self.host, self.port, self.path)
        response = requests.get(url)
        #print(response.content)
        data = json.loads(response.content)

        return [Result(item.get('path'), item.get('body')) for item in data]
