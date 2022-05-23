from ..orange_version import ORANGE_VERSION

if ORANGE_VERSION == ORANGE_VERSION.oasys_fork:
    from oasys.canvas.widgetsscheme import (
        OASYSSignalManager as _SignalManagerWithSchemeOrg,
    )
    import oasys.canvas.widgetsscheme as widgetsscheme_module

    class _SignalManagerWithScheme(_SignalManagerWithSchemeOrg):
        def has_pending(self):
            return bool(self._input_queue)

    notify_input_helper = None
else:
    from orangewidget.workflow.widgetsscheme import (
        WidgetsSignalManager as _SignalManagerWithScheme,
    )
    import orangewidget.workflow.widgetsscheme as widgetsscheme_module

    from orangewidget.utils.signals import notify_input_helper

from ewokscore.variable import value_from_transfer

from .owwidgets import is_native_widget
from .qtapp import QtEvent
from ..bindings.owsignals import get_input_names, get_output_names
from . import invalid_data


class _MissingSignalValue:
    """Indicates a missing signal value and allows waiting for the real signal value"""

    completed = QtEvent()


class _SignalValues:
    """Store signal values per widget and allow waiting for a value"""

    def __init__(self):
        self.values = dict()

    def _get_value(self, widget, signal_name):
        if not isinstance(signal_name, str):
            signal_name = signal_name.name
        values = self.values.setdefault(widget, dict())
        if signal_name not in values:
            values[signal_name] = _MissingSignalValue()
        return values[signal_name]

    def _set_value(self, widget, signal_name, value):
        if not isinstance(signal_name, str):
            signal_name = signal_name.name
        values = self.values.setdefault(widget, dict())
        values[signal_name] = value

    def set_value(self, widget, signal_name, value):
        previous_value = self._get_value(widget, signal_name)
        self._set_value(widget, signal_name, value)
        if isinstance(previous_value, _MissingSignalValue):
            previous_value.completed.set()

    def invalidate_value(self, widget, signal_name):
        previous_value = self._get_value(widget, signal_name)
        if isinstance(previous_value, _MissingSignalValue):
            return
        self.set_value(widget, signal_name, _MissingSignalValue())

    def get_value(self, widget, signal_name, timeout=None):
        value = self._get_value(widget, signal_name)
        if isinstance(value, _MissingSignalValue):
            value.completed.wait(timeout=timeout)
            value = self._get_value(widget, signal_name)
        return value

    def has_value(self, widget, signal_name):
        value = self._get_value(widget, signal_name)
        return not isinstance(value, _MissingSignalValue)


class SignalManagerWithOutputTracking:
    """Store input and output signal value per widget. Knows
    when a widget is "executed" or not.

    Losely based on Orange.widgets.tests.base.DummySignalManager
    """

    def __init__(self, *args, **kwargs):
        self.output_values = _SignalValues()
        self.input_values = _SignalValues()
        self._widget_cache = dict()
        super().__init__(*args, **kwargs)

    def set_output_value(self, widget, signal_name, value):
        self.output_values.set_value(widget, signal_name, value)

    def invalidate_output_value(self, widget, signal_name):
        self.output_values.invalidate_value(widget, signal_name)

    def get_output_value(self, widget, signal_name, timeout=None):
        return self.output_values.get_value(widget, signal_name, timeout=timeout)

    def has_output_value(self, widget, signal_name):
        return self.output_values.has_value(widget, signal_name)

    def set_input_value(self, widget, signal_name, value):
        self.input_values.set_value(widget, signal_name, value)

    def invalidate_input_value(self, widget, signal_name):
        self.input_values.invalidate_value(widget, signal_name)

    def get_input_value(self, widget, signal_name, timeout=None):
        return self.input_values.get_value(widget, signal_name, timeout=timeout)

    def has_input_value(self, widget, signal_name):
        return self.input_values.has_value(widget, signal_name)

    def widget_is_executed(self, widget):
        variable_names, widget_has_outputs = self._widget_cache.get(
            widget, (None, None)
        )
        if variable_names is None:
            variable_names = get_output_names(widget)
            widget_has_outputs = variable_names
            if not widget_has_outputs:
                variable_names = get_input_names(widget)
            self._widget_cache[widget] = variable_names, widget_has_outputs
        if widget_has_outputs:
            # Widget is executed when all outputs are set
            for name in variable_names:
                if not self.has_output_value(widget, name):
                    return False
        else:
            # Widget has no outputs
            if variable_names:
                # Widget is executed when all inputs are set
                for name in variable_names:
                    if not self.has_input_value(widget, name):
                        return False
            else:
                # Widget is executed when any input is set
                return bool(self.input_values.values.get(widget, False))
        return True


class SignalManagerWithoutScheme(SignalManagerWithOutputTracking):
    """Used when no Orange canvas is present.

    Only needs to keep track of widget outputs because data between tasks
    is passed by the Ewoks mechanism, not the Orange mechanism (signal manager).
    """

    def send(self, widget, signal_name, value, *args, **kwargs):
        self.set_output_value(widget, signal_name, value)


class SignalManagerWithScheme(
    SignalManagerWithOutputTracking, _SignalManagerWithScheme
):
    """Used when the Orange canvas is present.

    Dereference `Variable` types for native Orange widget inputs.
    """

    def send(self, widget, signal_name, value, *args, **kwargs):
        super().send(widget, signal_name, value, *args, **kwargs)
        self.set_output_value(widget, signal_name, value)

    def process_signals_for_widget(self, node, widget, signals):
        for signal in signals:
            if ORANGE_VERSION == ORANGE_VERSION.oasys_fork:
                signal_name = signal.link.sink_channel
            else:
                signal_name = signal.channel.name
            self.set_input_value(widget, signal_name, signal.value)
        if is_native_widget(widget):
            modified_signals = list()
            for signal in signals:
                sinfo = signal._asdict()
                sinfo["value"] = value_from_transfer(sinfo["value"])
                modified_signals.append(type(signal)(**sinfo))
            signals = modified_signals
        super().process_signals_for_widget(node, widget, signals)

    def invalidate(self, node, channel):
        super().invalidate(node, channel)
        widget = self.scheme().widget_for_node(node)
        if widget is None:
            return
        self.invalidate_input_value(widget, channel.name, _MissingSignalValue())

    def widget_is_executed(self, widget):
        if self.has_pending():
            return False  # The widget might be executed again
        return super().widget_is_executed(widget)


def set_input_value(widget, signal, value, index):
    value = invalid_data.as_invalidation(value)
    key = id(widget), signal.name, signal.id
    if ORANGE_VERSION == ORANGE_VERSION.oasys_fork:
        handler = getattr(widget, signal.handler)
        handler(value)
    else:
        notify_input_helper(signal, widget, value, key=key, index=index)


def patch_signal_manager():
    if ORANGE_VERSION == ORANGE_VERSION.oasys_fork:
        widgetsscheme_module.OASYSSignalManager = SignalManagerWithScheme
    else:
        widgetsscheme_module.WidgetsSignalManager = SignalManagerWithScheme
