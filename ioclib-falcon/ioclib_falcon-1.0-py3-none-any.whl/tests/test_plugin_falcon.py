from typing import Iterator
from falcon.testing import TestClient as Client
from falcon import App, Request, Response
from ioclib.falcon import get_falcon_injection, parameter, header
from ioclib.injector import Injector, inject


def test_parameter():
    injector = Injector([
        get_falcon_injection,
    ])

    class Entity:
        @injector.injectable
        def on_get(self, request: Request, response: Response, name: str = parameter()):
            response.text = name

    app = App()

    app.add_route('/entity', Entity)

    client = Client(app)

    result = client.simulate_get('/entity', params={
        'name': 'name'
    })

    assert result.text == 'name'


def test_parameter_with_injection():
    injector = Injector([
        get_falcon_injection,
    ])


    class SquareService:
        def execute(self, value):
            return value ** 2

    @injector.define('singleton')
    def injection() -> Iterator[SquareService]:
        yield SquareService()

    class Square:
        @injector.injectable
        def on_get(self, request: Request, response: Response, number: int = parameter(), square_service: SquareService = inject()):
            response.text = str(square_service.execute(number))

    app = App()

    app.add_route('/square', Square)

    client = Client(app)

    result = client.simulate_get('/square', params={
        'number': 2
    })

    assert result.text == '4'
