from nexoclom.utilities.read_configfile import read_configfile
from nexoclom.utilities import database_connect
import pytest


@pytest.mark.utilities
def test_readconfigfile():
    assert read_configfile()

@pytest.mark.utilities
def test_database_connect():
    # Test database connection
    with database_connect() as con:
        assert con.autocommit