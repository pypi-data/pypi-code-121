import sys
import webbrowser


def redirect_to_stack_over_flow(exception_type, value, traceback):
    sys.__excepthook__(exception_type, value, traceback)
    webbrowser.open(f"https://google.com/search?q=Python%20{exception_type.__name__}:%20{value}")


sys.excepthook = redirect_to_stack_over_flow
