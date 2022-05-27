import py2neo
import pytest
from py2neo.wiring import WireError

from weaveio.basequery.query_objects import Path
from weaveio.basequery.tests.example_structures.one2one import MyDataOne2One


@pytest.fixture(scope='session')
def workdir(tmpdir_factory):
    d = tmpdir_factory.mktemp("data")
    for i in range(5):
        fname = Path(str(d.join(f'{i}.fits')))
        with open(str(fname), 'w') as file:
            file.write('')
    return d


@pytest.fixture
def data_one2one(workdir):
    return MyDataOne2One(workdir, port=None)  # set to None for safety


@pytest.fixture(scope='module')
def database_one2one(workdir):
    try:
        data = MyDataOne2One(workdir, port=7687, write=True)
        assert data.graph.neograph.name == 'testweaveiodonotuse', "I will not run tests on this database as a safety measure"
        data.graph.neograph.run('MATCH (n) DETACH DELETE n')
        data.graph.neograph.run('CALL apoc.schema.assert({},{},true) YIELD label, key RETURN *')
    except (AssertionError, WireError):
        pytest.xfail("unsupported configuration of testing database")
    else:
        data.write_directory()
        data.validate()
        return data