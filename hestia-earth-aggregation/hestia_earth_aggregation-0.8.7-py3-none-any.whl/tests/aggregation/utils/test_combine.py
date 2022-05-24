from unittest.mock import patch
import pandas as pd

from tests.utils import fixtures_path
from hestia_earth.aggregation.utils.combine import run

class_path = 'hestia_earth.aggregation.utils.combine'
fixtures_folder = f"{fixtures_path}/utils/combine"

FILES = [
    {'Key': f"{fixtures_folder}/cycle-tomato-GADM-CHN-2019.csv"},
    {'Key': f"{fixtures_folder}/cycle-tomato-GADM-ESP-2009.csv"}
]


class FakeS3Client():
    def __init__(self, files=FILES):
        self.files = files

    def list_objects(self, **kwargs): return {'Contents': self.files}

    def get_object(self, Key, **kwargs):
        file = [f for f in self.files if f['Key'] == Key][0]
        return {'Body': file['Key']}


@patch(f"{class_path}.download_hestia", return_value={})
@patch(f"{class_path}._get_s3_client", return_value=FakeS3Client())
def test_run(*args):
    expected = pd.read_csv(f"{fixtures_folder}/output.csv", index_col='Cycle > Id')
    df = run('', 'Cycle', 'tomato')
    assert df.to_string() == expected.to_string()


@patch(f"{class_path}._get_s3_client", return_value=FakeS3Client([]))
def test_run_no_files(*args):
    df = run('', 'Cycle', 'tomato')
    assert df is None
