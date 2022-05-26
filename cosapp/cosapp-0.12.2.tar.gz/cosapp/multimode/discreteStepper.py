"""
Event handling and discrete stepping
"""
import scipy.optimize
from math import inf

from typing import NamedTuple, Iterator, List, Dict, Tuple
from cosapp.multimode.event import Event


class TimedEvent(NamedTuple):
    """Named tuple associating an event and its occurrence time"""
    event: Event
    time: float

    @classmethod
    def empty(cls):
        return cls(None, inf)


class DiscreteStepper():

    __slots__ = (
        '_owner', '_state', '_system', '_sysview',
        '_interval', '_nonprimitives', '_primitives',
    )

    def __init__(self, driver: "Driver"):
        # Local import to avoid cyclic dependency
        from cosapp.drivers.time.utils import SystemInterpolator

        self._owner = driver
        self._system = driver.owner
        self._sysview = SystemInterpolator(driver)
        self._interval = None
        self.set_events()

    def set_events(self) -> None:
        """Update event list from system of interest,
        and from stop criterion of owner time driver.
        """
        self._state: Dict[Event, bool] = dict.fromkeys(self._system.all_events(), False)
        stop = self._owner.scenario.stop
        if stop is not None:
            self._state[stop] = False
        self._primitives: List[Event] = list(filter(lambda e: e.is_primitive, self.events()))
        self._nonprimitives: List[Event] = list(filter(lambda e: not e.is_primitive, self.events()))

    def reset(self) -> None:
        """Update event list, and reset all events"""
        self.set_events()
        for event in self.events():
            event.reset()

    def events(self) -> Iterator[Event]:
        """Iterator on handled events"""
        return self._state.keys()

    def present_events(self) -> Iterator[Event]:
        """Returns an iterator on all present events"""
        return filter(lambda event: event.present, self.events())

    @property
    def sysview(self) -> "SystemInterpolator":
        """SystemInterpolator: system interpolator"""
        return self._sysview

    @property
    def interval(self) -> Tuple[float, float]:
        """Tuple[float, float]: time interval"""
        return self._interval

    @interval.setter
    def interval(self, interval: Tuple[float, float]):
        self._interval = interval

    def set_data(self, interval, interpol) -> None:
        """Sets interpolation data used for detecting the first event that occurred in a given time step."""
        self.interval = interval
        self._sysview.interp = interpol

    def trigger_time(self, event: Event) -> float:
        """Returns the date at which a primitive event was triggered.
        This method may only be called once the list of all triggered events is known
        and the interpolation data has been set."""
        def f(t):
            self._sysview.exec(t)
            return event.value()
        t1, t2 = self._interval
        t_event = scipy.optimize.brentq(f, t1, t2)
        # Reset system at original state
        self._sysview.exec(t1)
        return t_event

    def find_primal_event(self) -> TimedEvent:
        """Returns a `TimedEvent` named tuple containing the first primitive event triggered,
        together with its occurrence date ((None, inf) if no primitive event is triggered).
        The internal state is only updated if an event is triggered.
        This method should only be called at the first microstep of the first discrete time step.
        """
        # TODO: Possibility of several events at the same time (up to rounding errors)?
        # For instance, if an event occurs every 0.2s and another event every s...
        triggered_events = list(filter(lambda e: e.present, self._primitives))
        primal = TimedEvent.empty()
        for event in triggered_events:
            time = self.trigger_time(event)
            if time < primal.time:
                primal = TimedEvent(event, time)
        self._state[primal.event] = True
        self._sysview.exec(primal.time)
        return primal

    def event_detected(self) -> bool:
        """Tests all primitive events and returns a Boolean value indicating
        whether at least one of these events is to be triggered."""
        return any(event.to_trigger() for event in self._primitives)

    def _microstep(self) -> bool:
        """Performs an evaluation microstep for non-primitive events and returns a Boolean indicating
        whether one or several events were triggered in the current cascade.
        This method should not be called at the first microstep of a discrete time step.
        """
        has_changed = False
        for event in self._nonprimitives:
            triggered = event.step()
            self._state[event] |= triggered
            has_changed |= triggered
        return has_changed

    def first_discrete_step(self) -> TimedEvent:
        """Performs the first discrete step and returns a `TimedEvent` indicating which primitive event
        was triggered and at which date."""
        for event in self._primitives:
            event.step()
        occur = self.find_primal_event()
        while self._microstep():
            pass
        return occur

    def discrete_step(self) -> List[Event]:
        """Performs a discrete step other than the first one"""
        for event in self._primitives:
            self._state[event] = event.step()
        while self._microstep():
            pass
        return list(self.present_events())

    def tick(self):
        """Ends a discrete loop by ticking all events."""
        for event in self.events():
            event.tick()

    def shift(self) -> None:
        """Performs a time shift of all primitive events."""
        for event in self._primitives:
            event.tick()

    def reevaluate_primitive_events(self) -> None:
        for event in self._primitives:
            event.reevaluate()