import pytest
from typing import Tuple

from cosapp.multimode.discreteStepper import DiscreteStepper
from cosapp.drivers import EulerExplicit
from cosapp.systems import System


class AcceleratedSystem(System):
    def setup(self):
        self.add_inward('a', 1.0)
        self.add_transient('v', der='a')
        self.add_transient('x', der='v')

        self.add_event('fly')
        self.add_event('stop')


@pytest.fixture
def accelerated_case() -> Tuple[System, DiscreteStepper]:
    system = AcceleratedSystem('system')
    driver = system.add_driver(
        EulerExplicit(
            'time_driver',
            time_interval=(0, 10)
        )  # arbitrary
    )
    system.a = 10
    system.fly.trigger = "v > 12.34"
    system.stop.trigger = "x > 2.58"
    handler = DiscreteStepper(driver)
    # Use exact solution as interpolators
    handler.sysview.interp = {
        'v': lambda t: system.a * t,
        'x': lambda t: 0.5 * system.a * t**2,
    }
    return system, handler


def test_DiscreteStepper_trigger_time(accelerated_case):
    system, stepper = accelerated_case
    stepper.interval = (0.5, 1.5)
    tf = stepper.trigger_time(system.fly)
    ts = stepper.trigger_time(system.stop)
    assert tf == pytest.approx(1.234)
    assert ts == pytest.approx(0.7183314)


def test_DiscreteStepper_event_detected(accelerated_case):
    system, stepper = accelerated_case
    stepper.interval = (0.5, 1.5)
    stepper.sysview.exec(0.5)
    stepper.shift()
    # Hack: manual event stepping just for testing
    for event in system.all_events():
        event.step()
    stepper.sysview.exec(0.7)
    stepper.shift()
    assert not stepper.event_detected()
    # Hack: manual event stepping just for testing
    for event in system.all_events():
        event.step()
    stepper.sysview.exec(1.5)
    stepper.shift()
    assert stepper.event_detected()


def test_DiscreteStepper_primal_event(accelerated_case):
    system, stepper = accelerated_case
    stepper.interval = (0.5, 1.5)
    stepper.sysview.exec(0.5)
    # Manual reevaluation and shifting for testing purposes
    stepper.reevaluate_primitive_events()
    stepper.shift()
    stepper.sysview.exec(1.5)  
    # Neither `event_detected()` nor `find_primal_event()` call the `step()` method of events
    assert stepper.event_detected()
    assert system.x > 2.58
    assert system.v > 12.34
    # Manual stepping for testing purposes
    for event in system.all_events():
        event.step()
    first = stepper.find_primal_event()
    assert first.event is system.stop
    assert first.time == pytest.approx(0.7183314)
