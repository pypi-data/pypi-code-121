import json

import azure.identity
import azure.keyvault.secrets as secrets
import pytest
from cpg_utils.auth import check_dataset_access, check_global_access
from cpg_utils.config import get_deploy_config, get_server_config, set_deploy_config_from_env
from cpg_utils.secrets import SecretManager
from google.cloud import secretmanager

TEST_SERVER_CONFIG = json.dumps({
	"dataset1": {
		"projectId": "dataset1_id",
		"allowedRepos": ["sample-metadata", "fewgenomes"],
		"testToken": "Hail test SA account",
		"standardToken": "Hail standard SA account",
		"fullToken": "Hail full SA account" 
	}
})


class MockSecretResponse:
    class Payload:
        def __init__(self, secret_value):
            self.data = bytes(secret_value, "UTF-8")
    def __init__(self, secret_value):
        self.payload = MockSecretResponse.Payload(secret_value)
        self.value = secret_value


class MockSecretClientAzure:
    def __init__(self, *args, **kwargs):
        pass
    def get_secret(self, secret_name):
        if secret_name == "server-config":
            return MockSecretResponse(TEST_SERVER_CONFIG)
        if secret_name == "test_name":
            return MockSecretResponse("supersecret in azure")
        if secret_name == "project-creator-users":
            return MockSecretResponse("you@example.com,admin2@test.com")
        assert secret_name == "dataset1-read-members-cache"
        return MockSecretResponse("me@example.com,test2@test.com")


class MockSecretClientGCP:
    def secret_path(self, secret_host, secret_name):
        return secret_host + "/" + secret_name
    def access_secret_version(self, request):
        if request["name"] == "analysis-runner/server-config/versions/latest":
            return MockSecretResponse(TEST_SERVER_CONFIG)
        if request["name"] == "test_host/test_name/versions/latest":
            return MockSecretResponse("supersecret in gcp")
        if request["name"] == "analysis-runner/project-creator-users/versions/latest":
            return MockSecretResponse("you@example.com,admin1@test.com")
        assert request["name"] == "dataset1_id/dataset1-read-members-cache/versions/latest"
        return MockSecretResponse("me@example.com,test1@test.com")


def test_gcp_secret(monkeypatch):
    monkeypatch.setattr(secretmanager, "SecretManagerServiceClient", MockSecretClientGCP)
    sm = SecretManager.get_secret_manager("gcp")
    assert sm.read_secret("test_host", "test_name") == "supersecret in gcp"

    monkeypatch.setenv("CLOUD", "gcp")
    set_deploy_config_from_env()
    assert check_dataset_access("dataset1", "test1@test.com", "read") == True
    assert check_dataset_access("dataset1", "test2@test.com", "read") == False
    assert check_dataset_access("dataset2", "test2@test.com", "read") == False
    assert check_global_access("admin1@test.com", "project-creator-users") == True
    assert check_global_access("admin2@test.com", "project-creator-users") == False


def test_azure_secret(monkeypatch):
    monkeypatch.setattr(azure.identity, "DefaultAzureCredential", MockSecretClientAzure)
    monkeypatch.setattr(secrets, "SecretClient", MockSecretClientAzure)
    sm = SecretManager.get_secret_manager("azure")
    assert sm.read_secret("test_host", "test_name") == "supersecret in azure"

    monkeypatch.setenv("CLOUD", "azure")
    set_deploy_config_from_env()
    assert check_dataset_access("dataset1", "test1@test.com", "read") == False
    assert check_dataset_access("dataset1", "test2@test.com", "read") == True
    assert check_dataset_access("dataset2", "test2@test.com", "read") == False
    assert check_global_access("admin1@test.com", "project-creator-users") == False
    assert check_global_access("admin2@test.com", "project-creator-users") == True


def test_server_config(monkeypatch):
    monkeypatch.setattr(secretmanager, "SecretManagerServiceClient", MockSecretClientGCP)
    monkeypatch.setenv("CLOUD", "gcp")
    set_deploy_config_from_env()

    scfg1 = get_deploy_config().server_config
    scfg2 = get_server_config()
    assert scfg1 == scfg2
