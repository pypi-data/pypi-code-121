from ewoksorange.bindings import OWEwoksWidgetWithTaskStack
from ewoksorange.tests.listoperations import SumList3


class SumListWithTaskStack(OWEwoksWidgetWithTaskStack, ewokstaskclass=SumList3):
    """
    Simple demo class that will process task with a FIFO stack and one thread
    connected with the stack
    """

    name = "SumList with one thread and a stack"
    description = "Sum all elements of a list using a thread and a stack"
    icon = "icons/mywidget.svg"
    want_main_area = False
