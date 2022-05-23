import subprocess
import re

from .task_execution import TaskExecution, TaskException


class PowershellExecution(TaskExecution):
    def __init__(self, filename):
        super().__init__(name=filename)
        self.filename = filename
        self.parameter_names = list()

    def bind_parameters(self, context_parameters):
        with open(self.filename, 'r') as scriptfile:
            parameter_declaration = scriptfile.readline()
        m = re.match("param\(([^)]*)\)", parameter_declaration, flags=re.IGNORECASE)
        if m:
            param_string = m.group(1)
            self.parameter_names = [arg.strip() for arg in param_string.split(",")]
            for parameter_name in self.parameter_names:
                self.parameters[parameter_name] = context_parameters[parameter_name]

    def execute(self):
        parameter_values = list()
        for name in self.parameter_names:
            value = self.parameters.get(name)
            if value is None:
                parameter_values.append('')
            else:
                parameter_values.append(str(value))
        result = subprocess.run(["powershell", "-File", self.filename] + parameter_values, capture_output=True)
        if result.stderr:
            raise TaskException(result.stderr)
