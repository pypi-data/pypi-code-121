from compressnets.compression import *
import gzip
import json
import os
from importlib import resources


class Sample:

    @staticmethod
    def get_sample_temporal_network():
        # FILENAME = os.path.join(os.path.dirname(__file__), 'datafiles/sample_network')
        FILENAME = Sample.get_file()
        with gzip.open(FILENAME, 'r') as fin:  # 4. gzip
            json_bytes = fin.read()  # 3. bytes (i.e. UTF-8)

        json_str = json_bytes.decode('utf-8')  # 2. string (i.e. JSON)
        loaded_network = TemporalNetworkDecoder().decode(json_str=json_str)
        return loaded_network

    @staticmethod
    def get_file():
        with resources.path("compressnets.datafiles", "sample_network") as f:
            data_file_path = f
        return data_file_path
