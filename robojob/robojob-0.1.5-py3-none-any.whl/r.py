import re
import subprocess

from .task_execution import TaskExecution, TaskException


class RExecution(TaskExecution):
    def __init__(self, filename):
        super().__init__(name=filename)
        self.filename = filename
        self.parameter_names = list()

    def bind_parameters(self, context_parameters):
        with open(self.filename, 'r') as scriptfile:
            first_line = scriptfile.readline()
        if not first_line.strip():
            return
        self.parameter_names = re.findall("[a-z_0-9]+", first_line, re.IGNORECASE)
        for parameter_name in self.parameter_names:
            self.parameters[parameter_name] = context_parameters[parameter_name]

    def execute(self):
        parameter_values = list()
        for name in self.parameter_names:
            value = self.parameters.get(name)
            if value is None:
                parameter_values.append('""')
            else:
                parameter_values.append(str(value))
        result = subprocess.run(["RScript.exe", "--encoding=utf8", self.filename] + parameter_values, capture_output=True)
        if result.returncode != 0:
            raise TaskException(result.stderr)


