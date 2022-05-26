import abc
import logging, warnings
from numpy import bool_ as numpy_bool
from typing import Any, Union, Optional

from .zeroCrossing import ZeroCrossing
from cosapp.core.eval_str import EvalString
from cosapp.utils.naming import NameChecker, CommonPorts
from cosapp.utils.helpers import check_arg

logger = logging.getLogger(__name__)


class EventState(abc.ABC):
    """Interface describing the inner state of an event
    """
    @abc.abstractmethod
    def must_emit(self) -> bool:
        pass

    def to_emit(self) -> bool:
        return False

    def value(self) -> Any:
        """Returns value associated with event.
        By default, equivalent to `must_emit()`.
        """
        return self.must_emit()

    @property
    def is_primitive(self) -> bool:
        """bool: `True` if event triggering is self contained, `False` otherwise"""
        return False

    def reset(self) -> None:
        pass

    def reevaluate(self) -> None:
        pass

    def tick(self) -> None:
        pass

    def lock(self) -> None:
        pass


class Event:
    # TODO: Doc!
    """Class for events, to be used as local variables"""

    __slots__ = (
        "_name",
        "_desc",
        "_context",
        "_present",
        "_trigger",
        "_state",
        "_final",
    )
    __name_check = NameChecker(excluded=CommonPorts.names())

    def __init__(
        self,
        name: str,
        context: "cosapp.systems.System",
        desc: str = "",
        trigger: Optional[Union[str, ZeroCrossing, EventState, "Event"]] = None,
        final: bool = False,
    ):
        """`Event` constructor.

        Parameters
        ----------
        - name [str]:
            Event name
        - context [System]:
            Multimode system in which event is defined.
        - desc [str, optional]:
            Description of the event (default: "")
        - trigger [Union[str, ZeroCrossing, EventState, Event], optional]:
            Trigger defining event occurrence, given as either a string, a `ZeroCrossing` object,
            another event, or an `EvenState` derived from another event.
            If set to `None` or absent (default), the event is undefined, and thus never occurs
            (at least until `trigger` is redefined).
        - final [bool, optional]:
            Defines whether the occurrence of the event should stop time simulations. Defaults to `False`.
        """
        self._name = self.name_check(name)

        from cosapp.systems import System
        check_arg(context, "context", System)
        self._context: System = context
        
        self._desc = desc
        self._present = False  # presence at current instant
        self._state: EventState = None
        self.trigger = trigger
        self.final = final

    @classmethod
    def name_check(cls, name: str):
        return cls.__name_check(name)

    @property
    def name(self) -> str:
        """str : Event name"""
        return self._name

    @property
    def contextual_name(self) -> str:
        """str : Join context system name and event name.

        If the event has no context, only its name is returned.
        """
        context = self._context
        return self._name if context is None else f"{context.name}.{self._name}"

    def __repr__(self) -> str:
        return f"<{type(self).__name__} {self.contextual_name}>"

    def full_name(self, trim_root=False) -> str:
        """Returns full name up to root context.
        
        Parameters
        ----------
        trim_root : bool (optional, default False)
            Exclude root context name if True.

        Returns
        -------
        str
            The event full name
        """
        context = self._context
        path = []
        if context is not None:
            path = context.path_namelist()
            if trim_root:
                path = path[1:]
        path.append(self.name)
        return ".".join(path)

    @property
    def context(self) -> "cosapp.systems.System":
        return self._context

    @property
    def desc(self) -> str:
        """str : Event description"""
        return self._desc

    @property
    def trigger(self) -> Union[ZeroCrossing, EventState, "Event"]:
        return self._trigger

    @trigger.setter
    def trigger(self, trigger: Union[EventState, ZeroCrossing, str, "Event"]):
        state = None
        if isinstance(trigger, str):
            trigger = ZeroCrossing.from_comparison(trigger)
        if isinstance(trigger, ZeroCrossing):
            state = ZeroCrossingEvent(self, trigger)
        elif isinstance(trigger, Event):
            state = SynchronizedEvent(trigger)
        elif isinstance(trigger, EventState):
            state = trigger
        elif trigger is not None:
            raise TypeError(
                f"Event trigger cannot be defined by a {type(trigger).__name__}"
            )
        self._trigger = trigger
        self._state = state or UndefinedEvent()

    @property
    def is_primitive(self) -> bool:
        return self._state.is_primitive

    @property
    def present(self) -> bool:
        return self._present

    @property
    def final(self) -> bool:
        return self._final

    @final.setter
    def final(self, final: bool) -> None:
        check_arg(final, 'final', bool)
        self._final = final

    def value(self) -> Any:
        """Returns the value associated with the event."""
        return self._state.value()

    def __emit(self) -> None:
        self._present = True

    def tick(self) -> None:
        """Ticks the event, and locks it if it is a primitive event that has just been triggered."""
        self._state.tick()
        if self._present and self.is_primitive:
            self._state.lock()
        self._present = False

    def reset(self) -> None:
        """Resets the event."""
        self._state.reset()
        self._present = False

    def reevaluate(self) -> None:
        """Reevaluates the current state of the event; used to update information
        about zero-crossing events after an integration time step was interrupted by
        the triggering of an event."""
        self._state.reevaluate()

    def step(self) -> bool:
        """bool : Indicates whether the event was just triggered.
        
        Performs a step."""
        old = self._present
        if self._state.must_emit():
            self.__emit()
        # return True whenever the event has been emitted in this step
        return old ^ self._present

    def to_trigger(self) -> bool:
        """bool : Indicates whether the event has to be triggered in the next discrete step"""
        return self._present ^ self._state.to_emit()

    def filter(self, condition: str) -> "FilteredEvent":
        """Filters event with an additional boolean condition.
        
        Parameters:
        -----------
        - condition [str]:
            Evaluable boolean condition.
        
        Returns:
        --------
        - trigger [FilteredEvent]:
            The filtered event state, to be used as trigger.
        """
        return FilteredEvent(self, condition)

    @staticmethod
    def merge(*events: "Event") -> "MergedEvents":
        """Merges events into a trigger condition.
        
        Parameters:
        -----------
        - *events [Event]:
            Enumeration of events to be merged.
        
        Returns:
        --------
        - trigger [MergedEvents]:
            The merged event state, to be used as trigger.
        """
        return MergedEvents(*events)


class UndefinedEvent(EventState):
    """Inner state of an undefined, never occurring event"""
    def must_emit(self) -> bool:
        return False


class ZeroCrossingEvent(EventState):
    """Inner state of an event triggered by a zero-crossing expression"""
    def __init__(self, event: Event, zeroxing: ZeroCrossing):
        check_arg(event, 'event', Event)
        expr = EvalString(zeroxing.expression, event.context)
        if expr.constant:
            raise ValueError("Zero-crossing functions is constant")
        if not isinstance(expr.eval(), float):
            raise TypeError(
                "Zero-crossing condition must be a float expression"
            )
        self._expr = expr
        self._direction = zeroxing.direction
        self._event = event
        self.reset()

    def reset(self) -> None:
        self._prec = self._curr = None
        self._locked = False

    def value(self) -> float:
        """Evaluates and returns the zero-crossing function defining the event."""
        return self._expr.eval()

    def zero_detected(self, prec, curr) -> bool:
        return self._direction.zero_detected(prec, curr)

    def must_emit(self) -> bool:
        """Checks whether the event is triggered in the current discrete step."""
        if self._curr is None and not self._event.present:
            self._curr = self.value()
            return not self._locked and self._prec is not None and self.zero_detected(self._prec, self._curr)
        return False

    def to_emit(self) -> bool:
        """Checks whether the event will have to be triggered in a new discrete step"""
        if not self._locked and self._curr is None and not self._event.present:
            next_value = self.value()
            return self._prec is not None and self.zero_detected(self._prec, next_value)
        return False
        
    def lock(self) -> None:
        """Locks the event"""
        self._locked = True

    def reevaluate(self):
        """Forces the reevaluation of the zero-crossing function"""
        self._curr = self.value()

    def tick(self):
        """Performs a tick and checks whether the event can be unlocked"""
        if self._locked:
            self._locked = (self._curr == self._prec)
        self._prec = self._curr
        self._curr = None

    def is_primitive(self) -> bool:
        return True


class FilteredEvent(EventState):
    """Inner state of an event triggered by another event,
    filtered by a Boolean condition.
    """
    def __init__(self, event: Event, condition: str):
        """`FilteredEvent` constructor.
        
        Parameters
        ----------
        event : Event
            Base event
        condition : str
            Boolean expression, as a string
        """
        check_arg(event, 'event', Event)
        expr = EvalString(condition, event.context)
        if not isinstance(expr.eval(), (bool, numpy_bool)):
            raise TypeError(
                "FilteredEvent condition must be a Boolean expression."
            )
        if expr.constant and not expr.eval():
            warnings.warn(
                f"Event {event.contextual_name} is filtered with"
                f" unconditionally false expression {str(expr)!r}",
                RuntimeWarning,
            )
        self._event = event
        self._condition = expr

    def must_emit(self) -> bool:
        return self._event.present and self._condition.eval()


class MergedEvents(EventState):
    """Inner state of an event triggered by the merging of
    of other, external events.
    """
    def __init__(self, *events: Event):
        """`MergedEvent` constructor.
        
        Parameters
        ----------
        *events : Event
            Any number of events
        """
        self._events = events

    def must_emit(self) -> bool:
        """Returns `True` if at least one event is present,
        `False` otherwise."""
        return any(event.present for event in self._events)


class SynchronizedEvent(EventState):
    """Inner state of an event synchronized with another event.
    """
    def __init__(self, event: Event):
        check_arg(event, 'event', Event)
        self._event = event

    def must_emit(self) -> bool:
        return self._event.present
