from servicefoundry.internal.io.input_hook import InputHook
from servicefoundry.internal.io.output_callback import OutputCallBack
from servicefoundry.internal.predictor import Predictor

from .python.main_file_interceptor import main_file_interceptor
from .python.requirements_file_interceptor import requirements_file_interceptor
from .sf_template import SfTemplate
from .template_parameters import FILE, NUMBER, OPTIONS, PYTHON_FILE, STRING, WORKSPACE


class TemplateWorkflow:
    def __init__(self, template_name: str, input_hook: InputHook):
        self.template = SfTemplate.get_template(template_name)
        self.input_hook = input_hook
        self.parameters = None

    def process_parameter(self, parameter_values={}):
        final_params = {}
        for param in self.template.parameters:
            if not param.default:
                final_params[param.id] = self._get_parameters(param, parameter_values)
        additional_param = [p for p in self.template.parameters if p.default]
        change_additional = self.input_hook.confirm(
            "Would you like to change additional parameter?"
        )
        for param in additional_param:
            if change_additional:
                final_params[param.id] = self._get_parameters(param, parameter_values)
            else:
                final_params[param.id] = param.default
        self.parameters = final_params
        return final_params

    def _get_parameters(self, param, parameter_values):
        _id = param.id
        if _id in parameter_values:
            return parameter_values[_id]
        elif param.kind == STRING:
            return self.input_hook.ask_string(param)
        elif param.kind == NUMBER:
            return self.input_hook.ask_number(param)
        elif param.kind == OPTIONS:
            return self.input_hook.ask_option(param)
        elif param.kind == WORKSPACE:
            return self.input_hook.ask_workspace(param)
        elif param.kind == FILE:
            return self.input_hook.ask_file_path(param)
        elif param.kind == PYTHON_FILE:
            python_file = self.input_hook.ask_python_file(param)
            return python_file
        else:
            raise RuntimeError(f"Unsupported param kind {param.kind}")

    def write(
        self,
        out_folder,
        input_hook: InputHook = None,
        overwrite=False,
        callback=OutputCallBack(),
    ):
        parameters = {}
        for key, value in self.parameters.items():
            # If this special param is present in template, then we will attempt to update requirement.txt
            if key == "python_service_file":
                if isinstance(value, Predictor):
                    parameters[key] = value.predict_file
                    predictor = value
                else:
                    parameters[key] = value
                    predictor = Predictor.load_predictor(value)
                self.template.add_file_interceptor(
                    "requirements.txt", requirements_file_interceptor(predictor)
                )
                # @TODO Get rid of this interceptor by using reflection.
                self.template.add_file_interceptor(
                    "main.py", main_file_interceptor(predictor)
                )
            else:
                parameters[key] = value

        self.template.write(
            parameters,
            out_folder,
            input_hook,
            overwrite=overwrite,
            callback=callback,
        )
