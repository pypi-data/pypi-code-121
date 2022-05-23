import json
import time
import logging

from pathlib import Path

from alira.instance import Instance


class Store:
    def __init__(self, configuration_directory, store_configuration=None):
        logging.info("Store is configured to work with a JSON database.")

        store_configuration = store_configuration or {"filename": "store.json"}

        self._store_file = Path(str(configuration_directory)) / store_configuration.get(
            "filename", "store.json"
        )

        self.refresh()

    @staticmethod
    def configure(configuration_directory, store_configuration=None):
        return Store(
            configuration_directory=configuration_directory,
            store_configuration=store_configuration,
        )

    def refresh(self):
        if self._store_file.exists():
            with open(self._store_file, "r") as f:
                self.data = json.load(f)
        else:
            self.data = {}

    def get(self, id: str):
        entry = self.data.get(id, None)

        if entry is None:
            return None

        return Instance(**entry["instance"])

    def put(self, instance):
        self.data[instance.id] = {
            "instance": instance.to_dict(),
            "timestamp": time.time(),
        }
        self._flush()

    def list(self):
        result = sorted(
            self.data.items(), key=lambda item: item[1]["timestamp"], reverse=True
        )

        return [Instance(**entry[1]["instance"]) for entry in result[0:500]]

    def _flush(self):
        with open(self._store_file, "w") as f:
            json.dump(self.data, f)
