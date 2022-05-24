try:
    from pymxs import runtime as rt
    import qtmax
    maxhwnd = qtmax.GetQMaxMainWindow()
except (ImportError, ModuleNotFoundError):
    print('DCC not running!')
    rt = None
    maxhwnd = None
