"""
    Builder Web Services
"""

from .admin.bootstrap import bootstrap
from .admin import urls
from .admin import json
from .admin import view
from .admin import create_admin
# from .admin.cmd import create_app
# from .admin.cmd import create_project


__version__ = "0.0.4a5"
__author__ = "Jose Angel Delgado"
__author_email__ = "esojangel@gmail.com"


__all__ = [
    "bootstrap",
    "urls",
    "json",
    "view",
    "create_admin",
]