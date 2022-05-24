import typing as t

from werkzeug import Request, Response

from .simulator import WebApiSimulator


class Mockerinho:
    """A WSGI application that can serve requests and return stub responses."""
    simulator: WebApiSimulator

    def __init__(self, config: dict) -> None:
        self.simulator = WebApiSimulator.from_simulations_directory(
            config['simulations_directory']
        )

    def __call__(self, environ: dict, start_response: t.Callable) -> t.Iterable[bytes]:
        return self.wsgi_app(environ, start_response)

    def wsgi_app(self, environ: dict, start_response: t.Callable) -> t.Iterable[bytes]:
        request = Request(environ)
        response = self.dispatch_request(request)
        return response(environ, start_response)

    def dispatch_request(self, request: Request) -> Response:
        status, headers, body = self.simulator.request(
            method=request.method,
            path=request.path,
            url_params=request.args,
            headers=request.headers,
            body=request.get_data(as_text=True),
        )
        return Response(body, status, headers)


def create_app(simulations_directory: str) -> Mockerinho:
    app = Mockerinho({
        'simulations_directory': simulations_directory,
    })
    return app
