"""This module contains a set of utilities used to transform and prepare data for torch-nilm inference"""

import os
import json

from CleanEmonCore import CONFIG_FILE
from CleanEmonCore.models import EnergyData
from CleanEmonCore.CouchDBAdapter import CouchDBAdapter

from .. import CACHE_DIR
from .. import CLEAN_DB_CONFIG_FILE

adapter = CouchDBAdapter(CONFIG_FILE)
clean_adapter = CouchDBAdapter(CLEAN_DB_CONFIG_FILE)


def fetch_data(date_id: str, *, from_cache=False, from_clean_db: bool) -> EnergyData:

    if not os.path.exists(CACHE_DIR):
        os.mkdir(CACHE_DIR)

    if from_clean_db:
        name = f"{date_id}.clean"
    else:
        name = date_id

    cache_path = os.path.join(CACHE_DIR, name)

    fetch_ok = False

    energy_data = EnergyData()

    if from_cache:
        try:
            with open(cache_path, "r") as fin:
                raw_data = json.load(fin)
                energy_data = EnergyData(raw_data["date"], raw_data["energy_data"])

            print("Fetched data from cache")
            fetch_ok = True
        except OSError:
            print("No cached data!")

    if not from_cache or not fetch_ok:
        if from_clean_db:
            energy_data = clean_adapter.fetch_energy_data_by_date(date_id)
        else:
            energy_data = adapter.fetch_energy_data_by_date(date_id)

        # Cache data for future use
        with open(cache_path, "w") as fout:
            json.dump(energy_data.as_json(string=False), fout)

    return energy_data


def send_data(date_id: str, data: EnergyData, *, to_clean_db: bool):
    if to_clean_db:
        adapt = clean_adapter
    else:
        adapt = adapter

    return adapt.update_energy_data_by_date(date_id, data)
