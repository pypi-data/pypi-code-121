from ewoksorange.bindings import OWEwoksWidgetOneThread
from ewoksorange.tests.listoperations import SumList


class SumListOneThread(OWEwoksWidgetOneThread, ewokstaskclass=SumList):
    """
    Simple demo class that contains a single thread to execute SumList.run
    when requested.
    If a processing is requested when the thread is already running this
    will be refused
    """

    name = "SumList one thread"
    description = "Sum all elements of a list using at most one thread"
    icon = "icons/mywidget.svg"
    want_main_area = False
