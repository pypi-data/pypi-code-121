"""Commonly used Orange3 components for implementing Orange Widgets.
"""

from ..orange_version import ORANGE_VERSION

if ORANGE_VERSION == ORANGE_VERSION.oasys_fork:
    from oasys.widgets import gui  # noqa F401
    from oasys.widgets.settings import Setting  # noqa F401
    from oasyswidget.settings import Setting  # noqa F401
elif ORANGE_VERSION == ORANGE_VERSION.latest_orange:
    from Orange.widgets import gui  # noqa F401
    from Orange.widgets.widget import Input, Output  # noqa F401
    from Orange.widgets.settings import Setting  # noqa F401
else:
    from orangewidget import gui  # noqa F401
    from orangewidget.widget import Input, Output  # noqa F401
    from orangewidget.settings import Setting  # noqa F401
