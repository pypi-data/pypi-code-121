
# flake8: noqa

# Import all APIs into this package.
# If you have many APIs here with many many models used in each API this may
# raise a `RecursionError`.
# In order to avoid this, import only the API that you directly need like:
#
#   from .api.artifacts_api import ArtifactsApi
#
# or import this package, but before doing it, use:
#
#   import sys
#   sys.setrecursionlimit(n)

# Import APIs into API package:
from satnogsdbapiclient.api.artifacts_api import ArtifactsApi
from satnogsdbapiclient.api.modes_api import ModesApi
from satnogsdbapiclient.api.satellites_api import SatellitesApi
from satnogsdbapiclient.api.telemetry_api import TelemetryApi
from satnogsdbapiclient.api.tle_api import TleApi
from satnogsdbapiclient.api.transmitters_api import TransmittersApi
