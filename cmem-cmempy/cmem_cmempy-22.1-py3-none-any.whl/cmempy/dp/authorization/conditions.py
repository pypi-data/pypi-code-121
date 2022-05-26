"""API for managing conditions in DP."""

from cmem.cmempy import config
from cmem.cmempy.api import request


def get_graph_uri():
    """Get graph URI of the authorization conditions graph."""
    path = "/authorization/conditions"
    return config.get_dp_api_endpoint() + path


def get():
    """GET access conditions."""
    accept = "application/n-triples"
    headers = {"Accept": accept}
    return request(
        get_graph_uri(),
        method="GET",
        headers=headers
    )


def put(
        resource,
        access_conditions,
        rdf_serialization="application/n-triples"):
    """PUT access conditions."""
    params = {
        "resource": resource
    }
    data = access_conditions
    headers = {"Content-Type": rdf_serialization}
    return request(
        get_graph_uri(),
        method="PUT",
        params=params,
        data=data,
        headers=headers
    )


def post(
        access_conditions,
        rdf_serialization="application/n-triples"):
    """POST access conditions."""
    data = access_conditions
    headers = {"Content-Type": rdf_serialization}
    return request(
        get_graph_uri(),
        method="POST",
        data=data,
        headers=headers
    )


def delete(resource):
    """DELETE access condition."""
    params = {
        "resource": resource
    }
    return request(
        get_graph_uri(),
        method="DELETE",
        params=params
    )
