
# flake8: noqa

# Import all APIs into this package.
# If you have many APIs here with many many models used in each API this may
# raise a `RecursionError`.
# In order to avoid this, import only the API that you directly need like:
#
#   from vrt_lss_routing.api.matrix_api import MatrixApi
#
# or import this package, but before doing it, use:
#
#   import sys
#   sys.setrecursionlimit(n)

# Import APIs into API package:
from vrt_lss_routing.api.matrix_api import MatrixApi
from vrt_lss_routing.api.route_api import RouteApi
from vrt_lss_routing.api.system_api import SystemApi
