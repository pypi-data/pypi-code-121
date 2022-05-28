"""
.. _constants:

Useful Constants
----------------

Specific constants to be used in the package, to help with consistency.
"""
from typing import List

from pyhdtoolkit.cpymadtools.constants import MONITOR_TWISS_COLUMNS

VARIED_IR_QUADRUPOLES: List[int] = list(range(4, 11))

# fmt: off
# To be formatted based on ip and beam
AFFECTED_ELEMENTS = [
    # left side, 1 to 10
    "mqml.10l{ip}.b{beam}", "mqmc.9l{ip}.b{beam}", "mqm.9l{ip}.b{beam}", "mqml.8l{ip}.b{beam}", "mqm.b7l{ip}.b{beam}", "mqm.a7l{ip}.b{beam}",
    "mqml.6l{ip}.b{beam}", "mqml.5l{ip}.b{beam}", "mqy.4l{ip}.b{beam}", "mqxa.3l{ip}", "mqxb.b2l{ip}", "mqxb.a2l{ip}", "mqxa.1l{ip}",
    # right side, 1 to 10
    "mqxa.1r{ip}", "mqxb.a2r{ip}", "mqxb.b2r{ip}", "mqxa.3r{ip}", "mqy.4r{ip}.b{beam}", "mqml.5r{ip}.b{beam}", "mqml.6r{ip}.b{beam}",
    "mqm.a7r{ip}.b{beam}", "mqm.b7r{ip}.b{beam}", "mqml.8r{ip}.b{beam}", "mqmc.9r{ip}.b{beam}", "mqm.9r{ip}.b{beam}", "mqml.10r{ip}.b{beam}",
]
# fmt: on

EXPORT_TWISS_COLUMNS: List[str] = [colname.upper() for colname in MONITOR_TWISS_COLUMNS]
EXPORT_TWISS_COLUMNS.remove("DBX")
EXPORT_TWISS_COLUMNS.remove("DBY")
EXPORT_TWISS_COLUMNS += ["BBX", "BBY"]  # beta-beat columns
