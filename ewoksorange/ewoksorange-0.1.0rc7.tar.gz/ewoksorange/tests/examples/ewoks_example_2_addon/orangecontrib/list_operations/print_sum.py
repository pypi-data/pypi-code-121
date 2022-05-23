from ewoksorange.bindings import OWEwoksWidgetNoThread
from ewoksorange.tests.listoperations import PrintSum


class PrintSumOW(OWEwoksWidgetNoThread, ewokstaskclass=PrintSum):
    name = "Print list sum"
    description = "Print received list sum"
    icon = "icons/mywidget.svg"
    want_main_area = False
