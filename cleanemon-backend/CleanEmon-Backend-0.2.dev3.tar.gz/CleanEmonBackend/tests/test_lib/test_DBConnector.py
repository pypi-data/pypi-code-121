import pytest

from CleanEmonCore.models import EnergyData
from CleanEmonBackend.lib.DBConnector import fetch_data
from CleanEmonBackend.lib.DBConnector import send_data
from CleanEmonBackend.lib.DBConnector import adapter
from CleanEmonBackend.lib.DBConnector import clean_adapter

DUMMY_DATE = "2000-01-01"


@pytest.fixture
def energy_data():
    return EnergyData(DUMMY_DATE, [
        {"timestamp": 1, "power": 1, "temp": 1},
        {"timestamp": 2, "power": 2, "temp": 2},
        {"timestamp": 3, "power": 3, "temp": 3}
    ])


@pytest.mark.projectwise
def test_fetch_data():
    data = fetch_data("2022-05-01", from_clean_db=False)
    assert data
    assert type(data) is EnergyData

    data = fetch_data("2022-05-01", from_clean_db=True)
    assert not data.energy_data


@pytest.mark.projectwise
def test_clean_integration(energy_data):
    assert send_data(DUMMY_DATE, energy_data, to_clean_db=True)  # Send to clean db
    assert energy_data == fetch_data(DUMMY_DATE, from_clean_db=True)
    doc = clean_adapter.get_document_id_for_date(DUMMY_DATE)
    assert doc
    assert clean_adapter.delete_document(doc)

    assert not adapter.get_document_id_for_date(DUMMY_DATE)  # There should not be any changes in simple adapter


@pytest.mark.projectwise
def test_integration(energy_data):
    assert send_data(DUMMY_DATE, energy_data, to_clean_db=False)  # Send data to simple db
    assert energy_data == fetch_data(DUMMY_DATE, from_clean_db=False)
    doc = adapter.get_document_id_for_date(DUMMY_DATE)
    assert doc
    assert adapter.delete_document(doc)

    assert not clean_adapter.get_document_id_for_date(DUMMY_DATE)  # There should not be any changes in clean adapter
