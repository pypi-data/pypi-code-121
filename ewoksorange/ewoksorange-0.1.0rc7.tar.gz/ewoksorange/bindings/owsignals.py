import inspect
from typing import Callable, List, Optional
from ..orange_version import ORANGE_VERSION

if ORANGE_VERSION == ORANGE_VERSION.oasys_fork:
    from collections import namedtuple

    Input = namedtuple("Input", ["name", "type", "handler"])
    Input.ewoksname = property(lambda self: self.name)

    class Output(dict):
        @property
        def ewoksname(self):
            return self["name"]

        def __getattr__(self, attr):
            return self[attr]

else:
    from orangewidget.widget import Input, Output


SIGNAL_TYPES = (Input, Output)


def is_signal(obj):
    return isinstance(obj, SIGNAL_TYPES)


def get_signals(signal_container, orange_to_ewoks: Optional[dict] = None) -> dict:
    """Returns a map from ewoks names to signal objects"""
    if ORANGE_VERSION == ORANGE_VERSION.oasys_fork:
        if not signal_container:
            return dict()
        if isinstance(signal_container[0], tuple):
            return {
                orange_to_ewoks.get(tpl[0], tpl[0]): tpl for tpl in signal_container
            }
        else:
            return {
                orange_to_ewoks.get(adict["name"], adict["name"]): adict
                for adict in signal_container
            }
    else:
        """Returns a map from ewoks names to signal objects"""
        # TODO: getsignals doesn't work in the Orange3 hard-fork
        # from orangewidget.utils.signals import getsignals
        # return dict(getsignals(signal_container))
        return dict(inspect.getmembers(signal_container, is_signal))


def get_signal_container(widget_class, direction: str):
    if ORANGE_VERSION == ORANGE_VERSION.oasys_fork:
        return getattr(widget_class, direction, list())
        # List of tuples or dictionaries
    else:
        return getattr(widget_class, direction.title(), type)
        # Class


def get_orange_to_ewoks_mapping(widget_class, direction: str) -> Optional[dict]:
    if ORANGE_VERSION == ORANGE_VERSION.oasys_fork:
        return getattr(widget_class, direction + "_orange_to_ewoks", dict())
    else:
        return None


def get_ewoks_to_orange_mapping(widget_class, direction: str) -> Optional[dict]:
    if ORANGE_VERSION == ORANGE_VERSION.oasys_fork:
        return {
            v: k
            for k, v in get_orange_to_ewoks_mapping(widget_class, direction).items()
        }
    else:
        return None


def signal_ewoks_to_orange_name(widget_class, direction: str, ewoksname: str) -> str:
    signal_container = get_signal_container(widget_class, direction)
    if ORANGE_VERSION == ORANGE_VERSION.oasys_fork:
        orange_to_ewoks = get_orange_to_ewoks_mapping(widget_class, direction)
        for signal in signal_container:
            signal_ewoksname = orange_to_ewoks.get(signal.name, signal.name)
            if signal_ewoksname == ewoksname:
                return signal.name
        raise RuntimeError(f"{ewoksname} is not a signal of {signal_container}")
    else:
        try:
            return getattr(signal_container, ewoksname).name
        except AttributeError:
            raise RuntimeError(
                f"{ewoksname} is not a signal of {signal_container} of {widget_class}"
            ) from None


def signal_orange_to_ewoks_name(widget_class, direction: str, orangename: str) -> str:
    signal_container = get_signal_container(widget_class, direction)
    if ORANGE_VERSION == ORANGE_VERSION.oasys_fork:
        orange_to_ewoks = get_orange_to_ewoks_mapping(widget_class, direction)
        for signal in signal_container:
            if signal.name == orangename:
                return orange_to_ewoks.get(orangename, orangename)
        raise RuntimeError(f"{orangename} is not a signal of {signal_container}")
    else:
        for ewoksname, signal in get_signals(signal_container).items():
            if signal.name == orangename:
                return ewoksname
        raise RuntimeError(f"{orangename} is not a signal of {signal_container}")


def receiveDynamicInputs(name: str) -> Callable:
    setter_name = f"{name}_ewoks_setter"

    def setter(self, value):
        # Called by the SignalManager as a result of calling
        # `send` on an upstream output.
        self.receiveDynamicInputs(name, value)

    setter.__name__ = setter_name
    return setter


def _validate_signals_oasys(namespace: dict, direction: str, names: List[str]) -> None:
    is_inputs = direction == "inputs"
    signal_container = namespace[direction]

    orange_to_ewoks = namespace.get(direction + "_orange_to_ewoks", dict())
    signal_dict = get_signals(signal_container, orange_to_ewoks)

    signal_container = namespace[direction] = list()
    for ewoksname in names:
        signal = signal_dict.get(ewoksname, None)
        if is_inputs:
            if signal is None:
                orangename, stype, handler = ewoksname, object, None
            else:
                orangename, stype, handler = signal

            if not handler:
                setter = receiveDynamicInputs(ewoksname)
                namespace[setter.__name__] = setter
                handler = setter.__name__
            signal = Input(
                name=orangename,
                type=stype,
                handler=handler,
            )
        else:
            if signal is None:
                signal = Output(
                    [("name", ewoksname), ("type", object), ("id", ewoksname)]
                )
            else:
                signal = Output(signal)
        signal_container.append(signal)


def _validate_signals(namespace: dict, direction: str, names: List[str]) -> None:
    signals_class_name = direction.title()
    is_inputs = direction == "inputs"
    signal_container = namespace[signals_class_name]

    signal_dict = get_signals(signal_container)

    for ewoksname in names:
        signal = signal_dict.get(ewoksname, None)
        if signal is None:
            if is_inputs:
                signal = Input(name=ewoksname, type=object)
            else:
                signal = Output(name=ewoksname, type=object)
            setattr(signal_container, ewoksname, signal)
        signal.ewoksname = ewoksname
        if is_inputs and not signal.handler:  # str
            setter = receiveDynamicInputs(ewoksname)
            namespace[setter.__name__] = signal(setter)


def validate_inputs(namespace) -> None:
    if ORANGE_VERSION == ORANGE_VERSION.oasys_fork:
        if "inputs" not in namespace:
            namespace["inputs"] = list()

        if "inputs_orange_to_ewoks" not in namespace:
            namespace["inputs_orange_to_ewoks"] = dict()

        _validate_signals_oasys(
            namespace, "inputs", namespace["ewokstaskclass"].input_names()
        )
    else:
        if "Inputs" not in namespace:

            class Inputs:
                pass

            namespace["Inputs"] = Inputs

        _validate_signals(
            namespace, "inputs", namespace["ewokstaskclass"].input_names()
        )


def validate_outputs(namespace) -> None:
    if ORANGE_VERSION == ORANGE_VERSION.oasys_fork:
        if "outputs" not in namespace:
            namespace["outputs"] = list()

        if "outputs_orange_to_ewoks" not in namespace:
            namespace["outputs_orange_to_ewoks"] = dict()

        _validate_signals_oasys(
            namespace, "outputs", namespace["ewokstaskclass"].output_names()
        )
    else:
        if "Outputs" not in namespace:

            class Outputs:
                pass

            namespace["Outputs"] = Outputs

        _validate_signals(
            namespace, "outputs", namespace["ewokstaskclass"].output_names()
        )


def get_input_names(widget_class) -> List[str]:
    """Returns the Orange signal names, not the Ewoks output names"""
    signal_container = get_signal_container(widget_class, "inputs")
    orange_to_ewoks = get_orange_to_ewoks_mapping(widget_class, "inputs")
    return [
        signal.name
        for signal in get_signals(signal_container, orange_to_ewoks).values()
    ]


def get_output_names(widget_class) -> List[str]:
    """Returns the Orange signal names, not the Ewoks output names"""
    signal_container = get_signal_container(widget_class, "outputs")
    orange_to_ewoks = get_orange_to_ewoks_mapping(widget_class, "outputs")
    return [
        signal.name
        for signal in get_signals(signal_container, orange_to_ewoks).values()
    ]
