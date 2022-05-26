"""API for eccenca DataPlatform administration."""

from cmem.cmempy import config
from cmem.cmempy.api import request


def create_showcase_data(scale_factor=None):
    """Insert the showcase data.

    Args:
        scale_factor (int): multiplies the default showcase with a factor
    """
    uri = config.get_dp_api_endpoint() + "/api/admin/showcase"
    data = {}
    if scale_factor is not None:
        data["scaleFactor"] = scale_factor
    return request(
        uri,
        method="POST",
        data=data
    )


def import_bootstrap_data():
    """Replace the bootstrap data with the most current one.

    Overwrites all data in the shape, vocabulary, query and other catalogues.
    This operation overwrites data. Use with care.
    """
    uri = config.get_dp_api_endpoint() + "/api/admin/bootstrap"
    data = {}
    return request(
        uri,
        method="POST",
        data=data
    )


def get_prometheus_data():
    """Get DP /actuator/prometheus data."""
    uri = config.get_dp_api_endpoint() + "/actuator/prometheus"
    return request(
        uri,
        method="GET"
    )
