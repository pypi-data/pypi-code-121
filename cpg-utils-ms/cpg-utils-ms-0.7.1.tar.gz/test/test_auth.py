import os

import azure.identity
import google.auth
import google.auth.exceptions
import google.auth.transport.requests
import pytest
from cpg_utils.auth import get_sample_metadata_token, get_user_from_headers
from cpg_utils.config import set_deploy_config_from_env
from google.oauth2 import service_account

# Mocked tokens from https://www.javainuse.com/jwtgenerator
TEST_TOKEN1 = "eyJhbGciOiJIUzI1NiJ9.eyJSb2xlIjoiQWRtaW4iLCJJc3N1ZXIiOiJJc3N1ZXIiLCJVc2VybmFtZSI6IkphdmFJblVzZSIsImV4cCI6MTY1MDczNDA0NSwiaWF0IjoxNjUwNzM0MDQ1LCJlbWFpbCI6InRlc3QxQHRlc3QuY29tIn0.OJ-39xdDbIH8FDsdlwFsIwyDzgSbA_gOtYbRNhBmLxo"
TEST_TOKEN2 = "eyJhbGciOiJIUzI1NiJ9.eyJSb2xlIjoiQWRtaW4iLCJJc3N1ZXIiOiJJc3N1ZXIiLCJVc2VybmFtZSI6IkphdmFJblVzZSIsImV4cCI6MTY1MDczNDA0NSwiaWF0IjoxNjUwNzM0MDQ1LCJlbWFpbCI6InRlc3QyQHRlc3QuY29tIn0.ONbKZ4cf0jb9wtVJBprdtRhAhc5KVp9hSAPWN6ukt9A"
TEST_TOKEN3 = "eyJhbGciOiJIUzI1NiJ9.eyJSb2xlIjoiQWRtaW4iLCJJc3N1ZXIiOiJJc3N1ZXIiLCJVc2VybmFtZSI6IkphdmFJblVzZSIsImV4cCI6MTY1MDczNDA0NSwiaWF0IjoxNjUwNzM0MDQ1LCJlbWFpbCI6InRlc3QzQHRlc3QuY29tIn0.njCokays7b_Yl2O0_1lKROvLV-MiA0RW4bwx68dqeTo"


def test_bogus_header(monkeypatch):
    assert get_user_from_headers({}) is None
    headers = { "x-goog-iap-jwt-assertion" : "bogus" }
    monkeypatch.setenv("CLOUD", "gcp")
    set_deploy_config_from_env()
    with pytest.raises(ValueError, match="Wrong number of segments in token"):
        get_user_from_headers(headers)
    headers = { "Authorization" : "Bearer bogus" }
    with pytest.raises(ValueError, match="Wrong number of segments in token"):
        get_user_from_headers(headers)


def test_headers(monkeypatch):
    headers = {
        "x-goog-iap-jwt-assertion" : TEST_TOKEN1,
        "x-ms-client-principal-name" : "test2@test.com",
        "Authorization" : "Bearer " + TEST_TOKEN3
    }
    monkeypatch.setenv("CLOUD", "gcp")
    set_deploy_config_from_env()
    assert get_user_from_headers(headers) == "test1@test.com"
    monkeypatch.setenv("CLOUD", "azure")
    set_deploy_config_from_env()
    assert get_user_from_headers(headers) == "test2@test.com"
    headers = {
        "x-goog-iap-jwt-assertion" : TEST_TOKEN1,
        "Authorization" : "Bearer " + TEST_TOKEN3
    }
    assert get_user_from_headers(headers) == "test3@test.com"


class MockCredentials():
    def __init__(self, **kwargs):
        assert kwargs.get("tenant", "TENANT") == "TENANT"
        assert kwargs.get("appId", "APPID") == "APPID"
        assert kwargs.get("password", "supersecret") == "supersecret"
        self.token = "creds"
        self.id_token = "gcpcredsdef"

    def get_token(self, scope):
        assert scope == "api://smapi-sample-metadata/.default"
        return self

    def refresh(self, auth_req):
        pass


def mock_get_creds(*args, **kwargs):
    assert kwargs.get("target_audience", "http://localhost:8000") == "http://localhost:8000"
    return MockCredentials()


def mock_get_default_creds():
    return MockCredentials(), 42


def test_az_default_token(monkeypatch):
    monkeypatch.setenv("CLOUD", "azure")
    monkeypatch.setattr(azure.identity, "DefaultAzureCredential", mock_get_creds)
    set_deploy_config_from_env()
    assert get_sample_metadata_token() == "creds"


def test_az_file_token(monkeypatch, test_resources_path):
    monkeypatch.setenv("CLOUD", "azure")
    set_deploy_config_from_env()
    monkeypatch.setattr(azure.identity, "ClientSecretCredential", mock_get_creds)
    monkeypatch.setenv("AZURE_APPLICATION_CREDENTIALS", os.path.join(test_resources_path, "azure_creds.json"))
    assert get_sample_metadata_token() == "creds"


def test_gcp_default_token(monkeypatch):
    monkeypatch.setenv("CLOUD", "gcp")
    set_deploy_config_from_env()
    monkeypatch.setattr(google.auth, "default", mock_get_default_creds)
    assert get_sample_metadata_token() == "gcpcredsdef"


def test_gcp_file_token(monkeypatch, test_resources_path):
    monkeypatch.setenv("CLOUD", "gcp")
    set_deploy_config_from_env()
    monkeypatch.setattr(service_account.IDTokenCredentials, "from_service_account_info", mock_get_creds)
    monkeypatch.setenv("GOOGLE_APPLICATION_CREDENTIALS", os.path.join(test_resources_path, "gcp_creds.json"))
    assert get_sample_metadata_token() == "creds"
