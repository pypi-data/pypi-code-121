"""Imports core chart_me function for end users.

    Typical usage example:
    import chart_me as ce
    ce.chart_me(df, col1, col2...)
"""

__version__ = "0.1.5"


# chart_me imports
from chart_me.chart_me_logic import chart_me  # noqa: F401
