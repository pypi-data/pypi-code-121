"""
Orange widget base classes to execute Ewoks tasks
"""

import inspect
import logging
from contextlib import contextmanager
from typing import Mapping, Optional

from ..orange_version import ORANGE_VERSION

if ORANGE_VERSION == ORANGE_VERSION.oasys_fork:
    from oasys.widgets.widget import OWWidget
    from orangewidget.widget import WidgetMetaClass
    from orangewidget.settings import Setting

    OWBaseWidget = OWWidget
    summarize = None
    PartialSummary = None
    has_progress_bar = True
else:
    from orangewidget.widget import OWBaseWidget
    from orangewidget.settings import Setting
    from orangewidget.utils.signals import summarize
    from orangewidget.utils.signals import PartialSummary

    if ORANGE_VERSION == ORANGE_VERSION.latest_orange:
        from Orange.widgets.widget import OWWidget
        from Orange.widgets.widget import WidgetMetaClass

        has_progress_bar = True
    else:
        OWWidget = OWBaseWidget
        WidgetMetaClass = type(OWBaseWidget)
        has_progress_bar = False

from ewokscore.variable import Variable
from ewokscore.variable import value_from_transfer
from .progress import QProgress
from .taskexecutor import TaskExecutor
from .taskexecutor import ThreadedTaskExecutor
from .taskexecutor_queue import TaskExecutorQueue
from . import owsignals
from .events import scheme_ewoks_events
from . import invalid_data


_logger = logging.getLogger(__name__)


__all__ = [
    "OWEwoksWidgetNoThread",
    "OWEwoksWidgetOneThread",
    "OWEwoksWidgetOneThreadPerRun",
    "OWEwoksWidgetWithTaskStack",
    "ow_build_opts",
]


if summarize is not None:

    @summarize.register(Variable)
    def summarize_variable(var: Variable):
        if var.is_missing():
            dtype = var.value
        else:
            dtype = type(var.value).__name__
        desc = f"ewoks variable ({dtype})"
        return PartialSummary(desc, desc)

    @summarize.register(object)
    def summarize_object(value: object):
        return PartialSummary(str(type(value)), str(type(value)))


def prepare_OWEwoksWidgetclass(namespace, ewokstaskclass):
    """This needs to be called before signal and setting parsing"""
    namespace["ewokstaskclass"] = ewokstaskclass
    # Warning: default_inputs should convert MISSING_DATA to INVALIDATION_DATA
    #          when setting and convert INVALIDATION_DATA to MISSING_DATA when getting
    namespace["default_inputs"] = Setting(
        {name: invalid_data.INVALIDATION_DATA for name in ewokstaskclass.input_names()},
        schema_only=True,
    )
    namespace["varinfo"] = Setting(dict(), schema_only=True)
    owsignals.validate_inputs(namespace)
    owsignals.validate_outputs(namespace)


class _OWEwoksWidgetMetaClass(WidgetMetaClass):
    def __new__(metacls, name, bases, attrs, ewokstaskclass=None, **kw):
        if ewokstaskclass:
            prepare_OWEwoksWidgetclass(attrs, ewokstaskclass)
        return super().__new__(metacls, name, bases, attrs, **kw)


# insure compatibility between old orange widget and new
# orangewidget.widget.WidgetMetaClass. This was before split of the two
# projects. Parameter name "openclass" is undefined on the old version
ow_build_opts = {}
if "openclass" in inspect.signature(WidgetMetaClass).parameters:
    ow_build_opts["openclass"] = True


class OWEwoksBaseWidget(OWWidget, metaclass=_OWEwoksWidgetMetaClass, **ow_build_opts):
    """
    Base class to handle boiler plate code to interconnect ewoks and
    orange3
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__dynamic_inputs = dict()
        self.__task_output_changed_callbacks = {self.task_output_changed}

    @classmethod
    def input_names(cls):
        return cls.ewokstaskclass.input_names()

    @classmethod
    def output_names(cls):
        return cls.ewokstaskclass.output_names()

    def _getTaskArguments(self):
        if self.signalManager is None:
            execinfo = None
            node_id = None
        else:
            scheme = self.signalManager.scheme()
            node = scheme.node_for_widget(self)
            node_id = node.title
            if not node_id:
                node_id = scheme.nodes.index(node)
            execinfo = node.properties.get("execinfo", None)
            execinfo = scheme_ewoks_events(scheme, execinfo)
        return {
            "inputs": self.task_inputs,
            "varinfo": self.varinfo,
            "execinfo": execinfo,
            "node_id": node_id,
        }

    @staticmethod
    def _get_value(value):
        """Value comes from the orange input settings or from the previous task"""
        if isinstance(value, Variable):
            return value.value
        return value

    @property
    def default_input_values(self) -> dict:
        return {
            name: invalid_data.as_missing(value)
            for name, value in self.default_inputs.items()
        }

    @property
    def valid_default_input_values(self) -> dict:
        return {
            name: value
            for name, value in self.default_inputs.items()
            if not invalid_data.is_invalid_data(value)
        }

    def update_default_inputs(self, inputs: Mapping):
        for name, value in inputs.items():
            self.default_inputs[name] = invalid_data.as_invalidation(value)

    @property
    def dynamic_input_values(self) -> dict:
        return {k: self._get_value(v) for k, v in self.__dynamic_inputs.items()}

    @property
    def task_inputs(self) -> dict:
        """Default inputs overwritten by inputs from previous tasks"""
        inputs = self.valid_default_input_values
        inputs.update(self.__dynamic_inputs)
        return inputs

    def receiveDynamicInputs(self, name, value):
        if invalid_data.is_invalid_data(value):
            self.__dynamic_inputs.pop(name, None)
        else:
            self.__dynamic_inputs[name] = value

    def _get_output_signal(self, ewoksname):
        if ORANGE_VERSION == ORANGE_VERSION.oasys_fork:
            for signal in self.outputs:
                if signal.name == ewoksname:
                    break
            else:
                signal = None
        else:
            signal = getattr(self.Outputs, ewoksname, None)
        if signal is None:
            raise RuntimeError(f"Output signal '{ewoksname}' does not exist")
        return signal

    def trigger_downstream(self):
        if ORANGE_VERSION == ORANGE_VERSION.oasys_fork:
            for ewoksname, var in self.task_outputs.items():
                ewoks_to_orange = owsignals.get_ewoks_to_orange_mapping(
                    type(self), "outputs"
                )
                orangename = ewoks_to_orange.get(ewoksname, ewoksname)
                if invalid_data.is_invalid_data(var.value):
                    self.send(
                        orangename, invalid_data.INVALIDATION_DATA
                    )  # or channel.invalidate?
                else:
                    self.send(orangename, var)
        else:
            for ewoksname, var in self.task_outputs.items():
                channel = self._get_output_signal(ewoksname)
                if invalid_data.is_invalid_data(var.value):
                    channel.send(
                        invalid_data.INVALIDATION_DATA
                    )  # or channel.invalidate?
                else:
                    channel.send(var)

    def _output_changed(self):
        for cb in self.__task_output_changed_callbacks:
            cb()

    @property
    def task_output_changed_callbacks(self) -> set:
        return self.__task_output_changed_callbacks

    def task_output_changed(self):
        """Called when the task output has changed"""
        pass

    def clear_downstream(self):
        if ORANGE_VERSION == ORANGE_VERSION.oasys_fork:
            for name in self.task_outputs:
                self.send(
                    name, invalid_data.INVALIDATION_DATA
                )  # or channel.invalidate?
        else:
            for name in self.task_outputs:
                channel = self._get_output_signal(name)
                channel.send(invalid_data.INVALIDATION_DATA)  # or channel.invalidate?

    def propagate_downstream(self, succeeded: Optional[bool] = None):
        if succeeded is None:
            succeeded = self.task_succeeded
        if succeeded:
            self.trigger_downstream()
        else:
            self.clear_downstream()

    def defaultInputsHaveChanged(self):
        """Needs to be called when default inputs have changed"""
        self.executeEwoksTask()

    def handleNewSignals(self):
        """Invoked by the workflow signal propagation manager after all
        signals handlers have been called.
        """
        self.executeEwoksTask()

    def executeEwoksTask(self):
        self._executeEwoksTask(propagate=True)

    def executeEwoksTaskWithoutPropagation(self):
        self._executeEwoksTask(propagate=False)

    def _executeEwoksTask(self, propagate: bool):
        raise NotImplementedError("Base class")

    @property
    def task_succeeded(self):
        raise NotImplementedError("Base class")

    @property
    def task_outputs(self):
        raise NotImplementedError("Base class")

    @property
    def task_output_values(self):
        return {name: var.value for name, var in self.task_outputs.items()}

    def get_task_output_value(self, name):
        return self.task_outputs[name].value

    @property
    def task_input_values(self):
        return {
            name: value_from_transfer(var, varinfo=self.varinfo)
            for name, var in self.task_inputs.items()
        }

    def get_task_input_value(self, name):
        return value_from_transfer(self.task_inputs[name])


def is_orange_widget_class(widget_class):
    return issubclass(widget_class, OWBaseWidget)


def is_ewoks_widget_class(widget_class):
    return issubclass(widget_class, OWEwoksBaseWidget)


def is_native_widget_class(widget_class):
    return is_orange_widget_class(widget_class) and not is_ewoks_widget_class(
        widget_class
    )


def is_orange_widget(widget):
    return isinstance(widget, OWBaseWidget)


def is_ewoks_widget(widget):
    return isinstance(widget, OWEwoksBaseWidget)


def is_native_widget(widget_class):
    return is_orange_widget(widget_class) and not is_ewoks_widget(widget_class)


class OWEwoksWidgetNoThread(OWEwoksBaseWidget, **ow_build_opts):
    """Widget which will executeEwoksTask the ewokscore.Task directly"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__taskExecutor = TaskExecutor(self.ewokstaskclass)

    def _executeEwoksTask(self, propagate: bool):
        self.__taskExecutor.create_task(**self._getTaskArguments())
        try:
            self.__taskExecutor.execute_task()
        except Exception:
            _logger.error("task failed", exc_info=True)
        finally:
            self._output_changed()
        if propagate:
            self.propagate_downstream()

    @property
    def task_succeeded(self):
        return self.__taskExecutor.succeeded

    @property
    def task_outputs(self):
        return self.__taskExecutor.output_variables


class _OWEwoksThreadedBaseWidget(OWEwoksBaseWidget, **ow_build_opts):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__taskProgress = QProgress()
        if has_progress_bar:
            self.__taskProgress.sigProgressChanged.connect(self.progressBarSet)

    def onDeleteWidget(self):
        if has_progress_bar:
            self.__taskProgress.sigProgressChanged.disconnect(self.progressBarSet)
        self._cleanupTaskExecutor()
        super().onDeleteWidget()

    def _cleanupTaskExecutor(self):
        raise NotImplementedError("Base class")

    @contextmanager
    def _ewoksTaskStartContext(self):
        try:
            self.__ewoksTaskInit()
            yield
        except Exception:
            self.__ewoksTaskFinished()
            raise

    @contextmanager
    def _ewoksTaskFinishedContext(self):
        try:
            yield
        finally:
            self.__ewoksTaskFinished()

    def __ewoksTaskInit(self):
        self.progressBarInit()

    def __ewoksTaskFinished(self):
        self.progressBarFinished()
        self._output_changed()

    def _getTaskArguments(self):
        adict = super()._getTaskArguments()
        adict["progress"] = self.__taskProgress
        return adict


class OWEwoksWidgetOneThread(_OWEwoksThreadedBaseWidget, **ow_build_opts):
    """
    All the processing is done on one thread.
    If a processing is requested when the thread is already running then
    it is refused.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__taskExecutor = ThreadedTaskExecutor(ewokstaskclass=self.ewokstaskclass)
        self.__taskExecutor.finished.connect(self._ewoksTaskFinishedCallback)
        self.__propagate = None

    def _executeEwoksTask(self, propagate: bool):
        if self.__taskExecutor.isRunning():
            _logger.error("A processing is already ongoing")
            return
        else:
            self.__taskExecutor.create_task(**self._getTaskArguments())
            if self.__taskExecutor.is_ready_to_execute:
                with self._ewoksTaskStartContext():
                    self.__propagate = propagate
                    self.__taskExecutor.start()

    @property
    def task_succeeded(self):
        return self.__taskExecutor.succeeded

    @property
    def task_outputs(self):
        return self.__taskExecutor.output_variables

    def _ewoksTaskFinishedCallback(self):
        with self._ewoksTaskFinishedContext():
            if self.__propagate:
                self.propagate_downstream()

    def _cleanupTaskExecutor(self):
        self.__taskExecutor.finished.disconnect(self._ewoksTaskFinishedCallback)
        self.__taskExecutor.stop()
        self.__taskExecutor = None


class OWEwoksWidgetOneThreadPerRun(_OWEwoksThreadedBaseWidget, **ow_build_opts):
    """
    Each time a task processing is requested this will create a new thread
    to do the processing.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__taskExecutors = dict()
        self.__last_output_variables = dict()
        self.__last_task_succeeded = None

    def _executeEwoksTask(self, propagate: bool):
        taskExecutor = ThreadedTaskExecutor(ewokstaskclass=self.ewokstaskclass)
        taskExecutor.create_task(**self._getTaskArguments())
        if not taskExecutor.is_ready_to_execute:
            return
        with self.__init_task_executor(taskExecutor, propagate):
            with self._ewoksTaskStartContext():
                taskExecutor.start()

    @contextmanager
    def __init_task_executor(self, taskExecutor, propagate: bool):
        self.__disconnectAllTaskExecutors()
        taskExecutor.finished.connect(self._ewoksTaskFinishedCallback)
        self.__add_task_executor(taskExecutor, propagate)
        try:
            yield
        except Exception:
            taskExecutor.finished.disconnect(self._ewoksTaskFinishedCallback)
            self.__remove_task_executor(taskExecutor)
            raise

    def __disconnectAllTaskExecutors(self):
        for taskExecutor, _ in self.__taskExecutors:
            try:
                taskExecutor.finished.disconnect(self._ewoksTaskFinishedCallback)
            except KeyError:
                pass

    def _ewoksTaskFinishedCallback(self):
        with self._ewoksTaskFinishedContext():
            taskExecutor = None
            try:
                taskExecutor = self.sender()
                self.__last_output_variables = taskExecutor.output_variables
                self.__last_task_succeeded = taskExecutor.succeeded
                if self.__is_task_executor_propagated(taskExecutor):
                    self.propagate_downstream(succeeded=taskExecutor.succeeded)
            finally:
                self.__remove_task_executor(taskExecutor)

    def _cleanupTaskExecutor(self):
        self.__disconnectAllTaskExecutors()
        for taskExecutor, _ in self.__taskExecutors:
            taskExecutor.quit()
        self.__taskExecutors.clear()

    def __add_task_executor(self, taskExecutor, propagate: bool):
        self.__taskExecutors[id(taskExecutor)] = taskExecutor, propagate

    def __remove_task_executor(self, taskExecutor):
        self.__taskExecutors.pop(id(taskExecutor), None)

    def __is_task_executor_propagated(self, taskExecutor) -> bool:
        return self.__taskExecutors.get(id(taskExecutor), (None, False))[1]

    @property
    def task_succeeded(self):
        return self.__last_task_succeeded

    @property
    def task_outputs(self):
        return self.__last_output_variables


class OWEwoksWidgetWithTaskStack(_OWEwoksThreadedBaseWidget, **ow_build_opts):
    """
    Each time a task processing is requested add it to the FIFO stack.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__taskExecutorQueue = TaskExecutorQueue(ewokstaskclass=self.ewokstaskclass)
        self.__last_output_variables = dict()
        self.__last_task_succeeded = None

    def _executeEwoksTask(self, propagate):
        def callback():
            self._ewoksTaskFinishedCallback(propagate)

        with self._ewoksTaskStartContext():
            self.__taskExecutorQueue.add(
                _callbacks=(callback,),
                **self._getTaskArguments(),
            )

    @property
    def task_succeeded(self):
        return self.__last_task_succeeded

    @property
    def task_outputs(self):
        return self.__last_output_variables

    def _cleanupTaskExecutor(self):
        self.__taskExecutorQueue.stop()
        self.__taskExecutorQueue = None

    def _ewoksTaskFinishedCallback(self, propagate: bool):
        with self._ewoksTaskFinishedContext():
            taskExecutor = self.sender()
            self.__last_output_variables = taskExecutor.output_variables
            self.__last_task_succeeded = taskExecutor.succeeded
            if propagate:
                self.propagate_downstream()
