"""Test time observer pattern used in CoSApp"""
import pytest

from cosapp.core.time import TimeManager, UniversalClock, TimeObserver


@pytest.fixture(scope="function", autouse=True)
def final_check():
    yield None
    # teardown
    assert UniversalClock().n_observers == 0


@pytest.fixture(scope="function")
def clock():
    return UniversalClock()


class MockTimeObserver(TimeObserver):
    """Concrete mock-up of TimeObserver"""
    def _update(self, dt):
        pass


@pytest.mark.parametrize("args", [[], [0], [0.5], [-10]])
def test_TimeManager__init__(args):
    manager = TimeManager(*args)
    assert manager.time == (args[0] if args else 0)
    assert manager.n_observers == 0


def test_UniversalClock__init__():
    clock = UniversalClock()
    assert clock.time == 0
    assert clock.n_observers == 0
    clock.time = 0.2
    assert clock.time == 0.2
    clock.reset()
    assert clock.time == 0


def test_UniversalClock_unicity():
    clock1 = UniversalClock()
    clock2 = UniversalClock()
    assert clock1 is clock2


def test_TimeObserver_explicit_delete(clock):
    observer = MockTimeObserver(True)
    assert clock.n_observers == 1
    del observer
    assert clock.n_observers == 0


@pytest.mark.parametrize("sign_in", [True, False])
def test_TimeObserver__init__(sign_in, clock):
    observer = MockTimeObserver(sign_in)
    assert hasattr(observer, 'time')
    assert observer.time == clock.time
    assert observer.observes() == sign_in
    assert clock.n_observers == (1 if sign_in else 0)


def test_TimeObserver__delete__(clock):
    observers = [MockTimeObserver(True) for _ in range(10)]
    assert clock.n_observers == len(observers)

    for _ in range(5):
        MockTimeObserver(True)  # create unreferenced, temporary objects
    assert clock.n_observers == len(observers)

    for _ in range(5):
        tmp = MockTimeObserver(True)  # referenced temporary objects
        assert clock.n_observers == len(observers) + 1
    assert clock.n_observers == len(observers) + 1
    del tmp
    assert clock.n_observers == len(observers)

