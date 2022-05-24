import pytest
from contextvars import Context
from ioclib.injector import Injector, Requirement, inject
from typing import Iterator


class ClosableService:
    def __init__(self):
        self.closed = False

    def close(self):
        self.closed = True


class UndefinedService:
    pass


class BreezeService:
    def __init__(self, breeze):
        self.breeze = breeze


class TemperatureService:
    def __init__(self, temperature):
        self.temperature = temperature


class WeatherService:
    def __init__(self, temperature_service: TemperatureService, breeze_service: BreezeService):
        self.temperature_service = temperature_service
        self.breeze_service = breeze_service


def test_singleton_inject():
    injector = Injector()

    @injector.define('singleton')
    def temperature_service_def() -> Iterator[TemperatureService]:
        yield TemperatureService(0)


    @injector.injectable
    def main(temperature_service: TemperatureService = inject()):
        assert isinstance(temperature_service, TemperatureService)

    main()


def test_singleton_multuple_inject():
    injector = Injector()

    @injector.define('singleton')
    def temperature_service_def() -> Iterator[TemperatureService]:
        yield TemperatureService(0)

    @injector.define('singleton')
    def breeze_service_def() -> Iterator[BreezeService]:
        yield BreezeService(0)


    @injector.injectable
    def main(temperature_service: TemperatureService = inject(),
             breeze_service: BreezeService = inject()):

        assert isinstance(temperature_service, TemperatureService)
        assert isinstance(breeze_service, BreezeService)

    main()


def test_singleton_recursion_inject():
    injector = Injector()

    @injector.define('singleton')
    def temperature_service_def() -> Iterator[TemperatureService]:
        yield TemperatureService(0)

    @injector.define('singleton')
    def breeze_service_def() -> Iterator[BreezeService]:
        yield BreezeService(0)

    @injector.define('singleton')
    @injector.injectable
    def weather_service_def(temperature_service: TemperatureService = inject(),
                            breeze_service: BreezeService = inject()) -> Iterator[WeatherService]:
        yield WeatherService(temperature_service, breeze_service)


    @injector.injectable
    def main(weather_service: WeatherService = inject()):
        assert isinstance(weather_service, WeatherService)

        assert isinstance(weather_service.breeze_service, BreezeService)
        assert isinstance(weather_service.temperature_service, TemperatureService)

    main()


def test_lookup_error_inject():
    injector = Injector()

    @injector.injectable
    def main(undefined_service: UndefinedService = inject()):
        pass

    with pytest.raises(LookupError):
        main()


def test_without_injectable_inject():
    def main(undefined_service: UndefinedService = inject()):
        assert isinstance(undefined_service, Requirement)

    main()


def test_context_inject():
    injector = Injector()

    @injector.define('context')
    def temperature_service_def() -> Iterator[TemperatureService]:
        yield TemperatureService(0)

    @injector.injectable
    def main(temperature_service: TemperatureService = inject()):
        assert isinstance(temperature_service, TemperatureService)

    main()


def test_context_multiple_inject():
    injector = Injector()

    @injector.define('context')
    def temperature_service_def() -> Iterator[TemperatureService]:
        yield TemperatureService(0)

    @injector.define('context')
    def breeze_service_def() -> Iterator[BreezeService]:
        yield BreezeService(0)


    @injector.injectable
    def main(temperature_service: TemperatureService = inject(),
             breeze_service: BreezeService = inject()):

        assert isinstance(temperature_service, TemperatureService)
        assert isinstance(breeze_service, BreezeService)

    main()


def test_context_recursion_inject():
    injector = Injector()

    @injector.define('context')
    def temperature_service_def() -> Iterator[TemperatureService]:
        yield TemperatureService(0)

    @injector.define('context')
    def breeze_service_def() -> Iterator[BreezeService]:
        yield BreezeService(0)

    @injector.define('context')
    @injector.injectable
    def weather_service_def(temperature_service: TemperatureService = inject(),
                        breeze_service: BreezeService = inject()) -> Iterator[WeatherService]:
        yield WeatherService(temperature_service, breeze_service)


    @injector.injectable
    def main(weather_service: WeatherService = inject()):
        assert isinstance(weather_service, WeatherService)

        assert isinstance(weather_service.breeze_service, BreezeService)
        assert isinstance(weather_service.temperature_service, TemperatureService)

    main()


def test_context_with_multiple_context_inject():
    injector = Injector()

    @injector.define('context')
    def temperature_service_def() -> Iterator[TemperatureService]:
        yield TemperatureService(0)

    @injector.injectable
    def get_temperature_service(temperature_service: TemperatureService = inject()):
        return temperature_service

    assert Context().run(get_temperature_service) is not Context().run(get_temperature_service)

    context = Context()
    assert context.run(get_temperature_service) is context.run(get_temperature_service)


def test_context_container_enter_inject():
    injector = Injector()

    relove_count = 0
    release_count = 0

    @injector.define('context')
    def closable_service_def() -> Iterator[ClosableService]:
        nonlocal relove_count, release_count

        relove_count += 1
        service = ClosableService()

        yield service

        release_count += 1
        service.close()

    @injector.injectable
    def get_closable_service(closable_service: ClosableService = inject()) -> ClosableService:
        return closable_service

    def main():
        with injector.entry([closable_service_def]):
            closable_service = get_closable_service()
            assert not closable_service.closed

            assert relove_count == 1
            assert release_count == 0

            closable_service = get_closable_service()
            assert not closable_service.closed

            assert relove_count == 1
            assert release_count == 0

        assert closable_service.closed

        assert relove_count == 1
        assert release_count == 1

    main()


def test_container_error_handle_inject():
    injector = Injector()

    @injector.define('context')
    def closable_service_def() -> Iterator[ClosableService]:
        service = ClosableService()

        try:
            yield service
        finally:
            service.close()

    @injector.injectable
    def get_closable_service(closable_service: ClosableService = inject()) -> ClosableService:
        return closable_service

    def main():
        try:
            with injector.entry([closable_service_def]):
                closable_service = get_closable_service()
                raise RuntimeError()
        except Exception:
            pass

        assert closable_service.closed

    main()
