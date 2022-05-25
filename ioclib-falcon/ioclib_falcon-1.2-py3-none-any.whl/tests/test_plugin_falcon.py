from typing import Iterator
from falcon.testing import TestClient as Client
from falcon import App, Request, Response
from ioclib.falcon import falcon_request_injector, parameter, header, context
from ioclib.injector import Injector, inject


def test_parameter():
    injector = Injector([
        falcon_request_injector,
    ])

    class Entity:
        @injector.injectable
        def on_get(self, request: Request, response: Response, value: str = parameter()):
            response.text = value

    app = App()

    app.add_route('/entity', Entity())

    client = Client(app)

    result = client.simulate_get('/entity', params={
        'value': 'value'
    })

    assert result.text == 'value'


def test_parameter_default_value():
    injector = Injector([
        falcon_request_injector,
    ])

    class Entity:
        @injector.injectable
        def on_get(self, request: Request, response: Response, default: str = parameter('default')):
            response.text = default

    app = App()

    app.add_route('/entity', Entity())

    client = Client(app)

    result = client.simulate_get('/entity')

    assert result.text == 'default'


def test_context():
    injector = Injector([
        falcon_request_injector,
    ])

    class ContextMiddleware:
        def __init__(self, value):
            self.value = value

        def process_request(self, request, response):
            request.context.value = self.value

    class Entity:
        @injector.injectable
        def on_get(self, request: Request, response: Response, value: str = context()):
            response.text = value

    app = App(middleware=[
        ContextMiddleware('value')
    ])

    app.add_route('/entity', Entity())

    client = Client(app)

    result = client.simulate_get('/entity')

    assert result.text == 'value'


def test_parameter_with_injection():
    injector = Injector([
        falcon_request_injector,
    ])


    class PowerService:
        def power(self, value, power):
            return value ** power

    @injector.define('singleton')
    def power_service() -> Iterator[PowerService]:
        yield PowerService()

    class Entity:
        @injector.injectable
        def on_get(self,
                   request: Request,
                   response: Response,
                   number: int = parameter(),
                   power: int = parameter(),
                   power_service: PowerService = inject()):

            response.text = str(power_service.power(number, power))

    app = App()

    app.add_route('/square', Entity())

    client = Client(app)

    result = client.simulate_get('/square', params={
        'number': 2,
        'power': 3,
    })

    assert result.text == '8'
