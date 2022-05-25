# https://stackoverflow.com/questions/15411967/how-can-i-check-if-code-is-executed-in-the-ipython-notebook


def is_notebook():
    try:
        shell = get_ipython().__class__.__name__
        if shell == "ZMQInteractiveShell":
            return True  # Jupyter notebook or qtconsole
        elif shell == "TerminalInteractiveShell":
            return False  # Terminal running IPython
        else:
            return False  # Other type (?)
    except NameError:
        return False  # Probably standard Python interpreter


def get_default_callback():
    if is_notebook():
        from servicefoundry.core.notebook.notebook_callback import (
            NotebookOutputCallBack,
        )

        return NotebookOutputCallBack()
    else:
        from servicefoundry.internal.output_callback import OutputCallBack

        return OutputCallBack()
