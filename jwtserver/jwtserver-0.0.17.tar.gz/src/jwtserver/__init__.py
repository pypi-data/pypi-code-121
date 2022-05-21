"""JWTServer is a lightweight and fast JWT microservice."""
__version__ = '0.0.17'

from jwtserver.app import app as app
from jwtserver.app import create_app as create_app
from jwtserver.server import dev as dev
