import inspect

from .task_execution import TaskExecution


class FunctionExecution(TaskExecution):
    def __init__(self, func):
        super().__init__(name=func.__name__)
        self.func = func

    def bind_parameters(self, context_parameters):
        for name in inspect.signature(self.func).parameters.keys():
            self.parameters[name] = context_parameters.get(name)

    def execute(self):
        self.func(**self.parameters)
        


