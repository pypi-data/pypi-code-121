import pytest
import json
import os


from CleanEmonCore.models import EnergyData
from CleanEmonBackend.lib.plots import plot_data


@pytest.fixture
def clean_data_df():
    directory = os.path.dirname(__file__)
    file = os.path.join(directory, "2022-05-15.json")

    with open(file, "r") as f_in:
        j = json.load(f_in)

    return EnergyData(date=j["date"], energy_data=j["energy_data"])


def test_plot_data(clean_data_df):
    plot_data(clean_data_df, columns=["timestamp", "power", "pred_fridge"])
