import os
import json

import pandas as pd
import pytest
from CleanEmonCore.models import EnergyData
from CleanEmonBackend.Disaggregator.preparation import energy_data_to_dataframe


@pytest.fixture(scope="package")
def energy_data() -> EnergyData:
    directory = os.path.dirname(__file__)
    file = os.path.join(directory, "energy_data.json")

    with open(file, "r") as fp:
        data_dict = json.load(fp)

    return EnergyData(data_dict["date"], data_dict["energy_data"])


@pytest.fixture(scope="package")
def dataframe(energy_data) -> pd.DataFrame:
    return energy_data_to_dataframe(energy_data)
