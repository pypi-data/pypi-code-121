from fastrestapi import utils


class Application:
    def __init__(self):
        self.router = Router()

    def get(self, path):
        def decorator(func):
            self.router.add_route("GET", path, func)

        return decorator

    def post(self, path):
        def decorator(func):
            self.router.add_route("POST", path, func)

        return decorator

    def before_route(self, func):
        self.router.add_before_route(func)

    def after_route(self, func):
        self.router.add_after_route(func)

    def run(self, host="127.0.0.1", port=3000):
        print(f"app run at {host}:{port}")
        from waitress import serve

        serve(self, host=host, port=port, ident="")

    def __call__(self, environ, start_response):
        return self.wsgi(environ, start_response)

    def wsgi(self, environ, start_response):
        request.bind(environ)
        response.bind()

        out = self.cast(self.handle())
        start_response(response.status_line, response.header_list)
        return out

    def handle(self):
        try:
            self.router.doBefore()
            out = self.router.doMatch()
            self.router.doAfter()
            return out
        except HttpError as e:
            return e

    def cast(self, out):
        if not out:
            return []
        if isinstance(out, str):
            return self.cast(out.encode("UTF-8"))
        if isinstance(out, bytes):
            return [out]
        if isinstance(out, HttpError):
            response.status_code = out.code
            return self.cast(out.msg)


class Router:
    def __init__(self):
        self.routes = {}
        self.before_routes = []
        self.after_routes = []

    def add_route(self, method, path, func):
        self.routes.setdefault(method, {})
        self.routes[method][path] = func

    def add_before_route(self, func):
        self.before_routes.append(func)

    def add_after_route(self, func):
        self.after_routes.append(func)

    def doBefore(self):
        for func in self.before_routes:
            func()

    def doAfter(self):
        for func in self.after_routes:
            func()

    def doMatch(self):
        method = request.method
        path = request.path
        if method in self.routes and path in self.routes[method]:
            func = self.routes[method][path]
            return func()
        raise HttpError(404)


class BaseRequest:
    def __init__(self, environ=None):
        self.environ = environ

    @property
    def method(self):
        return self.environ.get("REQUEST_METHOD").upper()

    @property
    def path(self):
        return self.environ.get("PATH_INFO")

    @property
    def query(self) -> dict:
        return utils.parse_qsl(self.environ.get("QUERY_STRING"))

    @property
    def body(self):
        bodyio = self.environ.get("wsgi.input")
        bodyio.seek(0)
        return bodyio.read().decode("UTF-8")

    @property
    def form(self) -> dict:
        return utils.parse_qsl(self.body)

    @property
    def json(self) -> dict:
        return utils.parseJsonObject(self.body)

    @property
    def headers(self) -> dict:
        pass

    @property
    def cookies(self) -> dict:
        pass


class LocalRequest(BaseRequest):
    bind = BaseRequest.__init__
    environ = utils.local_property()


class BaseResponse:
    def __init__(self):
        self.status_code = 200
        self.body = ""
        self.headers = {"Content-Type": "text/html; charset=UTF-8"}

    @property
    def status_line(self):
        return utils.status_line(self.status_code)

    @property
    def header_list(self):
        return list(self.headers.items())

    def set_header(self, key, value):
        self.headers[key] = value


class LocalResponse(BaseResponse):
    bind = BaseResponse.__init__
    status_code = utils.local_property()
    body = utils.local_property()
    headers = utils.local_property()


class HttpError(Exception):
    def __init__(self, code, msg=None):
        self.code = code
        self.msg = msg


request = LocalRequest()
response = LocalResponse()

app = Application()

Get = app.get
Post = app.post
BeforeRoute = app.before_route
AfterRoute = app.after_route

run = app.run
load = utils.load
