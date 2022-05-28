from exceptions import MaxRuntimeError

try:
    import qtmax
    import pymxs
    from pymxs import runtime as rt

    MAX_HWND = qtmax.GetQMaxMainWindow()
except (ImportError, ModuleNotFoundError):
    raise MaxRuntimeError()
