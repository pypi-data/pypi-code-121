"""API for working with the query catalog."""
import json
import os
import re
from uuid import uuid1

from pyparsing import ParseException

from rdflib.plugins.sparql.parser import (
    parseUpdate
)
from rdflib.plugins.sparql import (
    prepareQuery
)

from cmem.cmempy.api import get_json
from cmem.cmempy.config import (
    get_cmem_base_uri,
    get_dp_api_endpoint
)
from cmem.cmempy.dp.proxy import sparql
from cmem.cmempy.dp.proxy import update

# read queries are send to the normal query endpoint
QUERY_TYPES_READ = ("SELECT", "ASK", "DESCRIBE", "CONSTRUCT")
# update queries are send to the update query endpoint
QUERY_TYPES_UPDATE_TRIPLE = ("UPDATE", "DELETE", "INSERT", "CLEAR", "LOAD")
QUERY_TYPES_UPDATE_GRAPHS = ("CREATE", "DROP", "COPY", "MOVE", "ADD")
QUERY_TYPES_UPDATE = QUERY_TYPES_UPDATE_TRIPLE + QUERY_TYPES_UPDATE_GRAPHS
# broken types
QUERY_TYPES_FAULTY = ("FAULTY", "UNKNOWN")
# all types
QUERY_TYPES = QUERY_TYPES_READ + QUERY_TYPES_UPDATE + QUERY_TYPES_FAULTY

QUERY_STRING = """
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX dct: <http://purl.org/dc/terms/>
    PREFIX shui: <https://vocab.eccenca.com/shui/>
    PREFIX dct: <http://purl.org/dc/terms/>
    SELECT DISTINCT ?query ?label ?text ?type ?description
    FROM <https://ns.eccenca.com/data/queries/>
    WHERE {
        ?query a shui:SparqlQuery ;
            rdfs:label ?label ;
            shui:queryText ?text ;
            shui:queryType ?type .
            OPTIONAL {?query dct:description ?description .}
    }
    """

DEFAULT_NS = "https://ns.eccenca.com/data/queries/"


def get_query_status():
    """Get status information of run and running queries."""
    endpoint = get_dp_api_endpoint() + "/api/admin/currentQueries"
    return get_json(endpoint)


def get_query_editor_for_uri():
    """Get query editor URI pattern for a query URI."""
    return get_cmem_base_uri() + "/query?tab=query&query={}"


def get_query_editor_for_string():
    """Get query editor URI pattern for a query string."""
    return get_cmem_base_uri() + "/query?tab=query&queryString={}"


class SparqlQuery:
    """A SPARQL query with optional placeholders."""

    # pylint: disable=too-many-arguments, too-many-instance-attributes

    def __init__(
            self, text, url=None, label=None, query_type=None,
            description=None, origin="unknown", placeholder=None):
        """Initialize a SparqlQuery object."""
        self.text = text
        self.short_url = None  # will be set with self.set_url
        self.url = self.set_url(url)
        self.label = label
        self.query_type = self.set_query_type(
            query_type, placeholder=placeholder
        )
        self.description = description
        # can be one of unknown, remote or file (used for get_editor_uri)
        self.origin = origin
        self.placeholder = placeholder

    def set_url(self, url=None):
        """Set (or generate) an URL for the query."""
        if url is not None:
            self.url = url
            self.short_url = url.replace(DEFAULT_NS, ':')
        else:
            uuid = str(uuid1())
            self.url = DEFAULT_NS + uuid
            self.short_url = ":" + uuid
        return self.url

    def __str__(self):
        """Get string representation (URL)."""
        return self.url

    def set_query_type(self, query_type=None, placeholder=None):
        """Set query type."""
        self.query_type = "UNKNOWN"
        if str(query_type).upper() in QUERY_TYPES:
            self.query_type = str(query_type).upper()
        else:
            parsed_type = str(
                self.get_query_type(placeholder=placeholder)
            ).upper()
            if parsed_type in QUERY_TYPES:
                self.query_type = parsed_type
        return self.query_type

    def get_query_type(self, placeholder=None):
        """Get type of query when placeholder are filled.

        Tries to get the type of the query - returns UNKNOWN if not possible,
        UPDATE, when an update query or a more specific READ query type
        """
        if placeholder is None:
            placeholder = {}
        algebra_names = {
            "DescribeQuery": "DESCRIBE",
            "ConstructQuery": "CONSTRUCT",
            "SelectQuery": "SELECT",
            "AskQuery": "ASK"
        }
        # prepare query text to parse
        string = self.text
        try:
            # try to fill with placeholders
            string = self.get_filled_text(placeholder)
        except ValueError:
            pass
        # 1. try parse as SPARQL query first and map algebra type to our type
        try:
            parsed_query = prepareQuery(string)
            if str(parsed_query.algebra.name) in algebra_names:
                # return the mapped read query type
                return algebra_names[str(parsed_query.algebra.name)]
        except ParseException:
            pass
        # 2. try to parse as UPDATE query
        try:
            parseUpdate(string)
            # return the default UPDATE query type
            return "UPDATE"
        except ParseException:
            pass
        # return the UNKNOWN query type
        return "UNKNOWN"

    def get_default_accept_header(self):
        """Return the default accept header string for the query.

        return value is based on the query type and biased towards
        command line shell environment.
        """
        default_header = {
            "SELECT": "text/csv",
            "ASK": "text/csv",
            "DESCRIBE": "text/turtle",
            "CONSTRUCT": "text/turtle"
        }
        return default_header.get(self.query_type, "*")

    def get_placeholder_keys(self, text=None):
        """Get all placeholder of a query text as a set of keys."""
        if text is None:
            text = self.text
        keys = re.findall(r"{{([a-zA-Z0-9_-]+)}}", text)
        return set(keys)

    def get_filled_text(self, placeholder):
        """Replace placeholders with given values and return text.

        raises an ValueError exception if not all placeholders are filled.
        """
        text = self.text
        for key, value in placeholder.items():
            text = text.replace('{{' + key + '}}', value)
        if self.get_placeholder_keys(text):
            raise ValueError("Not all placeholders filled for executing the "
                             "following query:\n"
                             "- Label: " + str(self.label) + "\n"
                             "- ID: " + str(self.url) + "\n"
                             "- Missing parameters: {}"
                             .format(self.get_placeholder_keys(text)))
        return text

    def get_csv_results(self, placeholder=None, owl_imports_resolution=True):
        """Get results as CSV text."""
        if self.query_type != "SELECT":
            raise ValueError("Wrong query type. "
                             "CSV result only supported for SELECT queries.")
        results = self.get_results(
            placeholder=placeholder,
            owl_imports_resolution=owl_imports_resolution,
            accept="text/csv"
        )
        return results

    def get_json_results(self, placeholder=None, owl_imports_resolution=True):
        """Get results as parsed json object."""
        results = self.get_results(
            placeholder=placeholder,
            owl_imports_resolution=owl_imports_resolution,
            accept="application/sparql-results+json"
        )
        return json.loads(results)

    def get_results(self, placeholder=None,
                    owl_imports_resolution=True,
                    base64_encoded=False,
                    accept="application/sparql-results+json",
                    distinct=False,
                    limit=None,
                    offset=None,
                    timeout=None,
                    replace_placeholder=True
                    ):
        """Get results as raw output from cmem.cmempy.dp.proxy.sparql."""
        if placeholder is None:
            placeholder = {}
        if self.query_type is None:
            # try to do last minute determination of type
            self.query_type = self.get_query_type(placeholder)
        if replace_placeholder:
            query_text = self.get_filled_text(placeholder)
        else:
            query_text = self.text
        if self.query_type in QUERY_TYPES_UPDATE:
            return update.post(
                query=query_text,
                accept=accept,
                base64_encoded=base64_encoded
            )
        return sparql.post(
            query=query_text,
            accept=accept,
            base64_encoded=base64_encoded,
            owl_imports_resolution=owl_imports_resolution,
            distinct=distinct,
            limit=limit,
            offset=offset,
            timeout=timeout
        )

    def get_editor_url(self):
        """Get query editor URI for the query."""
        if self.origin == "remote":
            return get_query_editor_for_uri().format(self.url)
        if self.origin == "file":
            return get_query_editor_for_string().format(self.text)
        raise ValueError(
            "Unknown origin, can not provide editor URL: " + self.origin
        )


class QueryCatalog:
    """A representation of the query catalog."""

    def __init__(self):
        """Initialize the catalog."""
        self.queries = None

    def get_query(self, identifier, placeholder=None):
        """Get a query by giving an url, a short_url or a file name."""
        if os.path.isfile(identifier):
            # do not fetch the catalog in case a file is requested
            with open(identifier, "rU", encoding="UTF-8") as file_handle:
                return SparqlQuery(
                    file_handle.read(),
                    label="query from file " + identifier,
                    origin="file",
                    placeholder=placeholder
                )
        queries = self.get_queries()
        if DEFAULT_NS + identifier[1:] in queries:
            # if identifier comes from shell (:uuid) then we remove : and add
            # the default namespace
            return queries[DEFAULT_NS + identifier[1:]]
        if identifier in queries:
            # maybe the correct full URI is given
            return queries[identifier]
        return None

    def get_queries(self):
        """Get the query catalog as a dictionary of SparqlQuery objects."""
        if self.queries is not None:
            return self.queries
        queries = {}
        results = SparqlQuery(
            QUERY_STRING,
            query_type="SELECT"
        ).get_json_results()
        for query in results["results"]["bindings"]:
            description = None
            if description in query:
                description = query["description"]
            queries[query["query"]["value"]] = SparqlQuery(
                query["text"]["value"],
                url=query["query"]["value"],
                label=query["label"]["value"],
                query_type=query["type"]["value"],
                description=description,
                origin="remote"
            )
        self.queries = queries
        return self.queries


QUERY_CATALOG = QueryCatalog()
