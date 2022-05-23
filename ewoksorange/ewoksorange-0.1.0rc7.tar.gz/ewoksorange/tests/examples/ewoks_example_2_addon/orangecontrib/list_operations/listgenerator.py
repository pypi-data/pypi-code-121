from AnyQt.QtWidgets import QPushButton
from ewoksorange.orange_version import ORANGE_VERSION

if ORANGE_VERSION == ORANGE_VERSION.oasys_fork:
    from oasys.widgets import gui
elif ORANGE_VERSION == ORANGE_VERSION.latest_orange:
    from Orange.widgets import gui
else:
    from orangewidget import gui
from ewoksorange.bindings import OWEwoksWidgetNoThread
from ewoksorange.gui.parameterform import ParameterForm
from ewoksorange.tests.listoperations import GenerateList


class ListGenerator(OWEwoksWidgetNoThread, ewokstaskclass=GenerateList):
    name = "List generator"
    description = "Generate a random list with X elements"
    icon = "icons/mywidget.svg"
    want_main_area = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

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

        box = gui.widgetBox(self.controlArea, "Commands")
        layout = box.layout()
        self._validateButton = QPushButton("generate", self)
        layout.addWidget(self._validateButton)

        # connect signal / slot
        self._validateButton.released.connect(self.handleNewSignals)

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
