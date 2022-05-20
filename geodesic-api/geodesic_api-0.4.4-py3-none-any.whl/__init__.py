# If this was checked out from a git tag, this version number may not match.
# Refer to the git tag for the correct version number
__version__ = "0.4.4"

from geodesic.oauth import AuthManager
from geodesic.stac import Item, Feature, FeatureCollection, Asset
from geodesic.client import Client, get_client, raise_on_error
from geodesic.raster import Raster, RasterCollection
from geodesic.entanglement import Dataset, DatasetList, list_datasets, get_dataset, get_objects
from geodesic.boson import BosonConfig
from geodesic.account import create_project, get_project, get_projects, set_active_project, \
                             get_active_project, myself, Project

__all__ = [
    "authenticate",
    "Item",
    "Feature",
    "FeatureCollection",
    "Asset",
    "BosonConfig",
    "Client",
    "get_client",
    "raise_on_error",
    "Raster",
    "RasterCollection",
    "Dataset",
    "DatasetList",
    "list_datasets",
    "get_dataset",
    "get_objects",
    "Project",
    "create_project",
    "get_project",
    "get_projects",
    "set_active_project",
    "get_active_project",
    "myself"
]


def authenticate():
    auth = AuthManager()
    auth.authenticate()
