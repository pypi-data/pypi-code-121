try:
    import qtmax
    import pymxs
    from pymxs import runtime as rt

    maxhwnd = qtmax.GetQMaxMainWindow()
except (ImportError, ModuleNotFoundError):
    print("DCC not running!")
    rt = None
    maxhwnd = None
