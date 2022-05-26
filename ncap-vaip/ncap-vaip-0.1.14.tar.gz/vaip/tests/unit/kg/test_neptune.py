###
#   This test file is a starting point for running local tests with NeptuneClient.
#   For further development, we could try adding in env variables that control if
#   these are run locally, or against AWS Neptune if available (eg. CI/CD).
###

import pytest
import uvicorn
import os
import time
from pathlib import Path
from multiprocessing import Process
from rdflib import ConjunctiveGraph
from rdflib_endpoint import SparqlEndpoint
from vaip.kg.client.neptune import NeptuneClient
import vaip.data

def init_server(host, port):
    data_path = Path(vaip.data.__file__)
    owl_dir = data_path.parent.absolute()
    path = os.path.join(owl_dir, 'vaip-0.3.2.owl')

    g = ConjunctiveGraph(identifier="http://test.foo/vaip")
    g.parse(path, format="application/rdf+xml")

    app = SparqlEndpoint(graph=g)
    uvicorn.run(app, host=host, port=port)

# This fixture function is copied from code in the rdflib-endpoint repo, and it's how they run query tests.
@pytest.fixture(scope="module")
def spawn_server():
    proc = Process(target=init_server, args=('localhost', 8182), daemon=True)
    proc.start()
    time.sleep(2) # This number might need to be tweaked depending on hardware?
    yield proc
    proc.kill()

# Make the NeptuneClient fixture dependent on spawn_server
@pytest.fixture(scope="module")
def client(spawn_server):
    client = NeptuneClient("http://localhost/sparql", 8182)
    return client


def test_neptune_foo(client):
    query = f"""
    SELECT ?g
    WHERE {{
        GRAPH ?g {{ }}
    }}
    """

    response = client.query(query)
    assert len(response['content']) > 0