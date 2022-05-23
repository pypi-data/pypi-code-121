from typing import Tuple
from ewokscore import Task
from ewoksorange.bindings.owwidgets import OWEwoksBaseWidget
from ewoksorange.bindings import OWEwoksWidgetNoThread
from ewoksorange import registration
from ewoksorange.ewoks_addon import DEFAULT_WIDGET_CLASSES
from . import widgets


NAME = "Ewoks defaults"

DESCRIPTION = "Default widgets for Ewoks tasks"

LONG_DESCRIPTION = "Default widgets for Ewoks tasks"


def register_owwidget(widget_class, discovery_object=None):
    package_name = __name__
    category_name = "EwoksDefaults"
    project_name = "ewoks-addon"

    registration.register_owwidget(
        widget_class,
        package_name,
        category_name,
        project_name,
        discovery_object=discovery_object,
    )


def default_owwidget_class(task_class: Task) -> Tuple[OWEwoksBaseWidget, str]:
    widget_class = DEFAULT_WIDGET_CLASSES.get(task_class, None)
    if widget_class is not None:
        return widget_class, "ewoks-addon"

    # Create the widget class
    class DefaultOwWidget(OWEwoksWidgetNoThread, ewokstaskclass=task_class):
        name = f"DefaultOwWidget({task_class.__name__})"
        description = f"Orange widget is missing for Ewoks task {task_class.__name__}"
        want_main_area = False

        def __init__(self, *args, **kw):
            super().__init__(*args, **kw)
            self.handleNewSignals()

    widget_class = DefaultOwWidget

    # Add the class to the 'widgets' module
    widget_class.__name__ += "_" + task_class.class_registry_name().replace(".", "_")
    widget_class.__module__ = widgets.__name__
    setattr(widgets, widget_class.__name__, widget_class)

    # Register the widget class
    DEFAULT_WIDGET_CLASSES[task_class] = widget_class
    register_owwidget(widget_class)
    return widget_class, "ewoks-addon"


def widget_discovery(discovery):
    for widget_class in DEFAULT_WIDGET_CLASSES.values():
        register_owwidget(widget_class, discovery_object=discovery)
