"""API for working with the vocabulary catalog."""

import json

import requests

from cmem.cmempy import config
from cmem.cmempy.api import send_request
from cmem.cmempy.dp.proxy.graph import (
    delete as delete_graph,
    put as put_graph
)
from cmem.cmempy.queries import SparqlQuery
from cmem.cmempy.workspace import (
    reload_prefixes,
    update_global_vocabulary_cache
)

DEFAULT_CATALOG_GRAPH = "https://ns.eccenca.com/example/data/vocabs/"

REMOVE_CATALOG_ENTRY_IF_NOT_INSTALLABLE = """
PREFIX dcat: <http://www.w3.org/ns/dcat#>
WITH <{{graph}}>
DELETE { ?s ?p ?o }
WHERE {
    ?s ?p ?o .
    FILTER NOT EXISTS { ?s dcat:distribution ?downloadUrl . }
    FILTER (STR(?s) = "{{vocab}}")
}
"""


def get_vocabs_endpoint():
    """Get endpoint URL for the dataplatform vocabs API."""
    return config.get_dp_api_endpoint() + "/api/vocabs"


def get_global_vocabs_cache_endpoint():
    """Get endpoint URL for the dataintegration vocabs cache."""
    path = "/workspace/globalWorkspaceActivities/GlobalVocabularyCache/value"
    return config.get_di_api_endpoint() + path


def get_vocabularies(
        catalog_uri=DEFAULT_CATALOG_GRAPH,
        limit=1000,
        offset=0,
        filter_="all"):
    """Get all vocabularies from a vocabulary catalog."""
    allowed_filter = ("all", "installed", "installable")
    if filter_ not in allowed_filter:
        raise ValueError(
            "Parameter filter_ not in ({})".format(', '.join(allowed_filter))
        )
    params = {
        "vocabGraph": catalog_uri,
        "limit": limit,
        "offset": offset
    }
    response = send_request(
        get_vocabs_endpoint(),
        method="GET",
        params=params
    )
    vocabs = json.loads(response.decode("utf-8"))["vocabularies"]
    if filter_ == "installed":
        vocabs = [
            vocab for vocab in vocabs
            if vocab["installed"]
        ]
    if filter_ == "installable":
        vocabs = [
            vocab for vocab in vocabs
            if not vocab["installed"] and vocab["downloadUrl"]
        ]
    return vocabs


def get_vocabulary(iri, catalog_uri=DEFAULT_CATALOG_GRAPH):
    """Get a vocabulary from a vocabulary catalog."""
    vocabs = get_vocabularies(catalog_uri=catalog_uri)
    for _ in vocabs:
        if _["iri"] == iri:
            return _
    raise FileNotFoundError("not available in the catalog")


def install_vocabulary(iri, catalog_uri=DEFAULT_CATALOG_GRAPH):
    """Install a vocabulary."""
    vocab = get_vocabulary(iri, catalog_uri=catalog_uri)
    if "downloadUrl" not in vocab:
        raise KeyError("no downloadable URL found")
    response = requests.api.request(
        "GET",
        vocab["downloadUrl"],
        verify=True,
    )
    if response.status_code is requests.status_codes.codes.ok:
        response.raise_for_status()
    put_graph(iri, response.content, "text/turtle")
    reload_prefixes()
    update_global_vocabulary_cache(iri)


def uninstall_vocabulary(iri, catalog_uri=DEFAULT_CATALOG_GRAPH):
    """Delete a vocabulary."""
    # make sure its a vocabulary graph
    get_vocabulary(iri, catalog_uri=catalog_uri)
    delete_graph(iri)
    reload_prefixes()
    update_global_vocabulary_cache(iri)
    remove_metadata = SparqlQuery(
        REMOVE_CATALOG_ENTRY_IF_NOT_INSTALLABLE,
        query_type="UPDATE"
    )
    placeholder = {
        "graph": DEFAULT_CATALOG_GRAPH,
        "vocab": iri
    }
    remove_metadata.get_results(placeholder=placeholder)


def get_global_vocabs_cache():
    """Get the global vocabulary cache value."""
    headers = {
        "Accept": "application/json"
    }
    response = send_request(
        get_global_vocabs_cache_endpoint(),
        method="GET",
        headers=headers
    )
    cache_ = json.loads(response.decode("utf-8"))
    return cache_
