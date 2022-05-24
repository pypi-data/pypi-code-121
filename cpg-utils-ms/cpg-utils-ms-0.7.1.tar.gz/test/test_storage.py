import pytest
from cpg_utils.config import set_deploy_config_from_env
from cpg_utils.storage import DataManager, get_data_manager
import azure.core.exceptions
import azure.identity
import azure.storage.blob
import google.cloud.storage


class MockStorageResponse:
    def __init__(self, blob_contents):
        self.value = bytes(blob_contents, "UTF-8")
    def download_as_bytes(self):
        return self.value
    def readall(self):
        return self.value
    def open(self, mode):
        assert mode == "wb"
        return self
    def __enter__(self):
        return self
    def write(self, contents):
        pass
    def __exit__(self, type, value, traceback):
        pass

class MockStorageClientGCP:
    def bucket(self, bucket_name):
        assert bucket_name == "cpg-dataset0-main-read"
        return self
    def get_blob(self, blob_path):
        if blob_path == "missing.json":
            return None
        assert blob_path == "exists.json"
        return MockStorageResponse("GCP BLOB CONTENTS")
    def blob(self, blob_path):
        return MockStorageResponse("nothing")

class MockStorageClientAzure:
    def __init__(self, *args, **kwargs):
        if len(args) > 2:
            assert args[0] == "https://dataset1_idsa.blob.core.windows.net"
            assert args[1] == "cpg-dataset1-main-read"
            self.path = args[2]
    def download_blob(self):
        if self.path == "missing.json":
            raise azure.core.exceptions.ResourceNotFoundError()
        assert self.path == "exists.json"
        return MockStorageResponse("AZURE BLOB CONTENTS")
    def upload_blob(self, data: bytes, overwrite: bool):
        pass

@pytest.fixture
def mock_config_fixture(json_load):
    def mock_get_server_config():
        return json_load("server_config_01.json")
    return mock_get_server_config


def test_gcp_storage(monkeypatch):
    monkeypatch.setattr(google.cloud.storage, "Client", MockStorageClientGCP)
    monkeypatch.setenv("CLOUD", "gcp")
    set_deploy_config_from_env()
    sm = get_data_manager()
    assert sm.get_blob("dataset0", "main-read", "exists.json").decode("UTF-8") == "GCP BLOB CONTENTS"
    assert sm.get_blob("dataset0", "main-read", "missing.json") == None
    sm.set_blob("dataset0", "main-read", "exists.json", bytes("GCP BLOB CONTENTS", "UTF-8"))


def test_azure_storage(monkeypatch, mock_config_fixture):
    monkeypatch.setattr("cpg_utils.storage.get_server_config", mock_config_fixture)
    monkeypatch.setattr(azure.identity, "DefaultAzureCredential", MockStorageClientAzure)
    monkeypatch.setattr(azure.storage.blob, "BlobClient", MockStorageClientAzure)
    monkeypatch.setenv("CLOUD", "azure")
    set_deploy_config_from_env()
    sm = DataManager.get_data_manager()
    assert sm.get_blob("dataset1", "main-read", "exists.json").decode("UTF-8") == "AZURE BLOB CONTENTS"
    assert sm.get_blob("dataset1", "main-read", "missing.json") == None
    with pytest.raises(ValueError) as e:
        sm.get_blob("dataset0", "main-read", "exists.json")
        assert "No such dataset in server config" in str(e.value)
    sm.set_blob("dataset1", "main-read", "exists.json", bytes("AZURE BLOB CONTENTS", "UTF-8"))
    with pytest.raises(ValueError) as e:
        sm.set_blob("dataset0", "main-read", "exists.json", bytes("AZURE BLOB CONTENTS", "UTF-8"))
        assert "No such dataset in server config" in str(e.value)