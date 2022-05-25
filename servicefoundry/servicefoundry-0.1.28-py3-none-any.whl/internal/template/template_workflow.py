from ..output_callback import OutputCallBack
from .input_hook import InputHook
from .sf_template import SfTemplate
from .template_parameters import FILE_PATH, NUMBER, OPTIONS, STRING, WORKSPACE


class TemplateWorkflow:
    def __init__(self, template: SfTemplate, input_hook: InputHook):
        self.template = template
        self.input_hook = input_hook
        self.parameters = None

    def process_parameter(self, parameters={}):
        final_params = {}
        for param in self.template.parameters:
            id = param.id
            if id in parameters:
                final_params[id] = parameters[id]
            elif param.kind == STRING:
                final_params[id] = self.input_hook.ask_string(param)
            elif param.kind == NUMBER:
                final_params[id] = self.input_hook.ask_number(param)
            elif param.kind == OPTIONS:
                final_params[id] = self.input_hook.ask_option(param)
            elif param.kind == FILE_PATH:
                final_params[id] = self.input_hook.ask_file_path(param)
            elif param.kind == WORKSPACE:
                final_params[id] = self.input_hook.ask_workspace(param)
        self.parameters = final_params

    def add_file_interceptor(self, file_name, interceptor):
        self.template.add_file_interceptor(file_name, interceptor)

    def write(
        self,
        out_folder,
        input_hook: InputHook = None,
        overwrite=False,
        verbose=False,
        callback=OutputCallBack(),
    ):
        self.template.write(
            self.parameters,
            out_folder,
            input_hook,
            overwrite=overwrite,
            verbose=verbose,
            callback=callback,
        )
