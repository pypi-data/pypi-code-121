from datetime import datetime

import py2neo
import pytest
from py2neo.wiring import WireError

from weaveio.graph import Graph


@pytest.fixture(scope='module')
def procedure_tag():
    return str(hash(datetime.now())).replace('-', '')[:5]


@pytest.fixture(scope='function')
def write_database(procedure_tag) -> Graph:
    try:
        graph = Graph(port=7687, host='host.docker.internal')
        assert graph.neograph.name == 'testweaveiodonotuse', "I will not run tests on this database as a safety measure"
        graph.neograph.run('MATCH (n) DETACH DELETE n')
        graph.neograph.run('CALL apoc.schema.assert({},{},true) YIELD label, key RETURN *')
        graph.neograph.run('call db.clearQueryCaches')
        return graph
    except (AssertionError, WireError):
        pytest.xfail("unsupported configuration of testing database")

