"""
tc2100: Receive data from a compatible USB digital thermometer

This module contains a parser for the TC2100 series of digital thermometers.
The parser is implemented as a `twisted` protocol, which enables a variety
of interesting use-cases for real-time temperature data.

This module includes :py:class:`ThermometerToCSVProtocol`, which dumps the
streaming temperature data to a CSV file. To do something else with the data,
subclass :py:class:`ThermometerProtocol` like so:

.. code-block:: python

   from twisted.internet import reactor
   from twisted.internet.serialport import SerialPort
   from tc2100 import ThermometerProtocol, discover

   class ThermPrinter(ThermometerProtocol):
     def observation_received(self, observation):
       print(observation.temperatures)

   SerialPort(ThermPrinter(), discover()[0].device, reactor, baudrate=9600)
   reactor.run()

A more detailed example can be found in :py:mod:`tc2100.__main__`.
"""

from .version import __version__        # noqa:F401
from .version import __author__         # noqa:F401
from .version import __copyright__      # noqa:F401
from .version import __license__        # noqa:F401

from .discover import discover          # noqa:F401
from .protocol import ThermometerProtocol          # noqa:F401
from .protocol import ThermometerToCSVProtocol     # noqa:F401
from .observation import Observation, MeterTime    # noqa:F401
from .observation import TemperatureUnit           # noqa:F401
from .observation import ThermocoupleType          # noqa:F401
