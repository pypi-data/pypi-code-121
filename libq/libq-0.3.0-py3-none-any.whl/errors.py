

class TimeoutFormatError(Exception):
    pass


class JobNotFound(Exception):
    def __init__(self, execid):
        msg = f"Execid {execid} not found"
        super().__init__(msg)


class FunctionCallError(Exception):
    def __init__(self, func_name, error):
        msg = f"{func_name} failed with error: {error}"
        super().__init__(msg)
