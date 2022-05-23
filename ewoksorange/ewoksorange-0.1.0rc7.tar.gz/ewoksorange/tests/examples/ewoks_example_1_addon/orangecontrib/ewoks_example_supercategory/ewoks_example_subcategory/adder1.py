from ewoksorange.orange_version import ORANGE_VERSION

if ORANGE_VERSION == ORANGE_VERSION.oasys_fork:
    from oasys.widgets import gui
elif ORANGE_VERSION == ORANGE_VERSION.latest_orange:
    from Orange.widgets import gui
    from Orange.widgets.widget import Input, Output
else:
    from orangewidget import gui
    from orangewidget.widget import Input, Output

from ewoksorange.bindings import OWEwoksWidgetNoThread
from ewoksorange.gui.parameterform import ParameterForm
from ewoks_example_addon import SumTaskSubCategory1


__all__ = ["Adder1"]


class Adder1(OWEwoksWidgetNoThread, ewokstaskclass=SumTaskSubCategory1):
    name = "Adder1"
    description = "Adds two numbers"
    icon = "icons/mywidget.svg"
    want_main_area = False

    if ORANGE_VERSION == ORANGE_VERSION.oasys_fork:
        inputs = [("A", object, ""), ("B", object, "")]
        outputs = [{"name": "A + B", "id": "A + B", "type": object}]
        inputs_orange_to_ewoks = {"A": "a", "B": "b"}
        outputs_orange_to_ewoks = {"A + B": "result"}
    else:

        class Inputs:
            a = Input("A", object)
            b = Input("B", object)

        class Outputs:
            result = Output("A + B", object)

    def __init__(self):
        super().__init__()

        box = gui.widgetBox(self.controlArea, "Default Inputs")
        self._default_inputs_form = ParameterForm(parent=box)
        for name, value in self.default_input_values.items():
            self._default_inputs_form.addParameter(
                name,
                value=value,
                default=0,
                changeCallback=self.defaultInputsHaveChanged,
            )

        box = gui.widgetBox(self.controlArea, "Dynamic Inputs")
        self._dynamic_input_form = ParameterForm(parent=box)
        for name in self.input_names():
            self._dynamic_input_form.addParameter(name)

        box = gui.widgetBox(self.controlArea, "Outputs")
        self._output_form = ParameterForm(parent=box)
        for name in self.output_names():
            self._output_form.addParameter(name)

        self.handleNewSignals()

    def defaultInputsHaveChanged(self):
        self.update_default_inputs(self._default_inputs_form.get_parameter_values())
        super().defaultInputsHaveChanged()

    def handleNewSignals(self):
        for name, value in self.dynamic_input_values.items():
            self._dynamic_input_form.set_parameter_value(name, value)
            self._default_inputs_form.set_parameter_enabled(name, False)
        super().handleNewSignals()

    def task_output_changed(self):
        for name, value in self.task_output_values.items():
            self._output_form.set_parameter_value(name, value)
        super().task_output_changed()
