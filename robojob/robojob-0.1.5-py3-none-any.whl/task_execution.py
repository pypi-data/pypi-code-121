
class TaskException(Exception):
    pass

class TaskExecution:
    def __init__(self, name):
        self.name = name
        self.parameters = dict()
        self.id = None
        self.status = "Started"
        self.error_message = ""
    
    def bind_parameters(self, context_parameters):
        raise NotImplementedError()

    def execute(self):
        raise NotImplementedError()

    def __repr__(self):
        return f"<{self.__class__.__name__}: {self.name}>"

