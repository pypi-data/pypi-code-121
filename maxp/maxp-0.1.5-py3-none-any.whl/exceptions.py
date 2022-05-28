class MaxRuntimeError(Exception):
    def __init__(self) -> None:
        msg = "Module pymxs not found. Are you running this script in 3ds Max?"
        super().__init__(msg)
