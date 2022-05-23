from typing import List, Tuple

from ewokscore import Task
from ewokscore.utils import qualname
from ewokscore.utils import import_qualname
from ewokscore.variable import value_from_transfer

from .qtapp import ensure_qtapp
from .qtapp import process_qtapp_events
from .qtapp import QtEvent
from .owwidgets import is_ewoks_widget_class
from .owwidgets import is_native_widget_class
from . import owsignals
from . import owsettings
from . import invalid_data
from .owsignal_manager import SignalManagerWithoutScheme
from .owsignal_manager import set_input_value
from ..orange_version import ORANGE_VERSION

__all__ = ["OWWIDGET_TASKS_GENERATOR"]


def owwidget_task_wrapper(widget_qualname: str) -> Task:
    """Create a task that does the computation through an orange widget.
    When the widget is an ewoks widget, still use the widget and not
    the corresponding task class directly.
    """
    widget_class = import_qualname(widget_qualname)
    registry_name = widget_qualname + ".wrapper"
    if registry_name in Task.get_subclass_names():
        return Task.get_subclass(registry_name)

    if is_ewoks_widget_class(widget_class):
        return _ewoks_owwidget_task_wrapper(registry_name, widget_class)
    elif is_native_widget_class(widget_class):
        return _native_owwidget_task_wrapper(registry_name, widget_class)
    else:
        raise TypeError(widget_class, "expected to be an OWWidget")


OWWIDGET_TASKS_GENERATOR = qualname(owwidget_task_wrapper)


def _ewoks_owwidget_task_wrapper(registry_name, widget_class) -> Task:
    """Wrap an Ewoks widget with an Ewoks task"""
    all_input_names = widget_class.input_names()
    try:
        ewokstaskclass = widget_class.ewokstaskclass
        input_names = ewokstaskclass.required_input_names()
        optional_input_names = ewokstaskclass.optional_input_names()
        expected = set(input_names) | set(optional_input_names)
        assert all_input_names == expected
    except AttributeError:
        input_names = all_input_names
        optional_input_names = tuple()
    output_names = widget_class.output_names()

    class WrapperTask(
        Task,
        input_names=input_names,
        optional_input_names=optional_input_names,
        output_names=output_names,
        registry_name=registry_name,
    ):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.outputsReceived = None
            self.widget = None

        def run(self):
            ensure_qtapp()
            self.outputsReceived = QtEvent()
            self.widget = widget_class()
            try:
                self.widget.task_output_changed_callbacks.add(self.receiveOutputSend)

                # Call the input setters
                values = self.input_values

                if ORANGE_VERSION == ORANGE_VERSION.oasys_fork:
                    signals = self.widget.inputs
                else:
                    signals = self.widget.get_signals("inputs")
                orange_to_ewoks = owsignals.get_orange_to_ewoks_mapping(
                    widget_class, "inputs"
                )

                for index, signal in enumerate(signals):
                    if ORANGE_VERSION == ORANGE_VERSION.oasys_fork:
                        key = orange_to_ewoks.get(signal.name, signal.name)
                    else:
                        key = signal.ewoksname
                    set_input_value(self.widget, signal, values[key], index)

                # Start calculation
                self.widget.handleNewSignals()

                # Wait for the result
                self.outputsReceived.wait()
            finally:
                self.widget.close()
                self.widget = None
                self.outputsReceived = None

        def receiveOutputSend(self):
            try:
                for name, value in self.widget.task_output_values.items():
                    self.output_variables[name].value = value
            finally:
                if self.outputsReceived is not None:
                    self.outputsReceived.set()

    return WrapperTask


def _native_owwidget_task_wrapper(registry_name, widget_class) -> Task:
    """Wrap a native Orange widget with an Ewoks task"""
    input_signals = owsignals.get_signals(widget_class.Inputs)
    optional_input_names = set(input_signals.keys())
    output_signals = owsignals.get_signals(widget_class.Outputs)
    output_names = set(output_signals.keys())
    orange_to_ewoks_namemap = {
        ewoks_name: signal.name for ewoks_name, signal in output_signals.items()
    }
    input_names = tuple()
    setting_names = list(owsettings.get_settings(widget_class))

    class WrapperTask(
        Task,
        input_names=input_names,
        optional_input_names=optional_input_names,
        output_names=output_names,
        registry_name=registry_name,
    ):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.outputsReceived = None

        def run(self):
            input_list, settings_dict = self._parse_input_values()

            # Create widget with the proper settings
            ensure_qtapp()
            widget = instantiate_owwidget(
                widget_class,
                signal_manager=SignalManagerWithoutScheme(),
                stored_settings=settings_dict,
            )
            try:
                # Call input setters
                for index, (signal, value) in enumerate(input_list):
                    set_input_value(widget, signal, value, index)

                # Start calculation
                widget.handleNewSignals()

                # Wait for the result
                process_qtapp_events()

                for ewoks_name, orange_name in orange_to_ewoks_namemap.items():
                    value = widget.signalManager.get_output_value(
                        widget, orange_name, timeout=None
                    )
                    self.output_variables[ewoks_name].value = value
            finally:
                widget.close()

        def _parse_input_values(self) -> Tuple[List, dict]:
            values = self.input_values

            used_values = set()
            settings_dict = dict()
            input_list = list()

            # Values corresponding to settings
            for ewoksname in setting_names:
                if ewoksname not in values:
                    continue
                used_values.add(ewoksname)
                value = value_from_transfer(values[ewoksname])
                settings_dict[ewoksname] = value

            # Values corresponding to inputs
            for signal in widget_class.get_signals("inputs"):
                ewoksname = owsignals.signal_orange_to_ewoks_name(
                    widget_class, "inputs", signal.name
                )
                if ewoksname not in values:
                    continue
                used_values.add(ewoksname)
                value = value_from_transfer(values[ewoksname])
                input_list.append((signal, value))

            # Node properties not corresponding to settings or inputs
            # are used in settings migration
            unused_values = set(values.keys()) - used_values
            for ewoksname in unused_values:
                value = value_from_transfer(values[ewoksname])
                settings_dict[ewoksname] = value

            return input_list, settings_dict

    return WrapperTask


def instantiate_owwidget(widget_class, signal_manager=None, stored_settings=None):
    if stored_settings:
        stored_settings = {
            k: invalid_data.as_invalidation(v) for k, v in stored_settings.items()
        }
    widget = widget_class.__new__(
        widget_class, signal_manager=signal_manager, stored_settings=stored_settings
    )
    widget.__init__()
    return widget
