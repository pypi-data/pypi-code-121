import os

import pytest
from mock import Mock, patch

import vessl
from test.conftest import USE_MOCK
from vessl.util.config import VesslConfigLoader
from vessl.util.constant import (
    ACCESS_TOKEN_ENV_VAR,
    CREDENTIALS_FILE_ENV_VAR,
    DEFAULT_ORGANIZATION_ENV_VAR,
)
from vessl.util.exception import (
    InvalidOrganizationError,
    InvalidProjectError,
    InvalidTokenError,
    VesslApiException,
)

config_path_api = "test/config_api"


def teardown_module(module):
    try:
        os.remove(config_path_api)
    except OSError:
        pass

    # Reset access token and organization because tests override it
    if not USE_MOCK:
        vessl.init(is_test=True)


def test_configure_access_token():
    config_loader = VesslConfigLoader(config_path_api)
    config_loader_ = patch("vessl.vessl_api.config_loader", config_loader)
    get_my_user_info_api_ = patch(
        "vessl.vessl_api.get_my_user_info_api", return_value=Mock()
    )

    # Test `access_token`
    access_token = "abcde"
    with config_loader_, get_my_user_info_api_:
        vessl.configure_access_token(access_token=access_token)

    assert (
        vessl.vessl_api.api_client.default_headers["Authorization"]
        == f"Token {access_token}"
    )
    assert config_loader.access_token == access_token

    # Test `credentials_file`
    access_token = "bcdef"
    config_loader.access_token = access_token
    with config_loader_, get_my_user_info_api_:
        vessl.configure_access_token(credentials_file=config_path_api)

    assert (
        vessl.vessl_api.api_client.default_headers["Authorization"]
        == f"Token {access_token}"
    )
    assert VesslConfigLoader(config_path_api).access_token == access_token

    # Test `AUTH_TOKEN_ENV_VAR`
    access_token = "cdefg"

    access_token_env_var_ = patch.dict(os.environ, {ACCESS_TOKEN_ENV_VAR: access_token})
    with config_loader_, get_my_user_info_api_, access_token_env_var_:
        vessl.configure_access_token()

    assert (
        vessl.vessl_api.api_client.default_headers["Authorization"]
        == f"Token {access_token}"
    )
    assert VesslConfigLoader(config_path_api).access_token == access_token

    # Test `CREDENTIALS_FILE_ENV_VAR`
    access_token = "defgh"
    config_loader.access_token = access_token

    credentials_file_env_var_ = patch.dict(
        os.environ, {CREDENTIALS_FILE_ENV_VAR: config_path_api}
    )
    with config_loader_, get_my_user_info_api_, credentials_file_env_var_:
        vessl.configure_access_token()

    assert (
        vessl.vessl_api.api_client.default_headers["Authorization"]
        == f"Token {access_token}"
    )
    assert VesslConfigLoader(config_path_api).access_token == access_token

    # Test `force_update`
    access_token = "efghi"
    get_new_access_token_ = patch(
        "vessl.util.api.VesslApi._get_new_access_token", return_value=access_token
    )
    with config_loader_, get_my_user_info_api_, get_new_access_token_:
        vessl.configure_access_token(force_update=True)

    assert (
        vessl.vessl_api.api_client.default_headers["Authorization"]
        == f"Token {access_token}"
    )
    assert VesslConfigLoader(config_path_api).access_token == access_token

    # Test fail: expired
    get_my_user_info_api_ = patch(
        "vessl.vessl_api.get_my_user_info_api", side_effect=VesslApiException()
    )
    with config_loader_, get_my_user_info_api_:
        with pytest.raises(InvalidTokenError):
            vessl.configure_access_token(access_token=access_token)


def test_configure_organization():
    config_loader = VesslConfigLoader(config_path_api)
    organization = Mock()
    response = Mock()
    response.organizations = [organization]

    config_loader_ = patch("vessl.vessl_api.config_loader", config_loader)
    organization_list_api_ = patch(
        "vessl.vessl_api.organization_list_api", return_value=response
    )

    # Test `organization_name`
    organization_name = "org1"
    organization.name = organization_name

    with config_loader_, organization_list_api_:
        vessl.configure_organization(organization_name=organization_name)

    assert vessl.vessl_api.organization.name == organization_name
    assert VesslConfigLoader(config_path_api).default_organization == organization_name

    # Test `credentials_file`
    organization_name = "org2"
    organization.name = organization_name
    config_loader.default_organization = organization_name

    with config_loader_, organization_list_api_:
        vessl.configure_organization(credentials_file=config_path_api)

    assert vessl.vessl_api.organization.name == organization_name
    assert VesslConfigLoader(config_path_api).default_organization == organization_name

    # Test `DEFAULT_ORGANIZATION_ENV_VAR`
    organization_name = "org3"
    organization.name = organization_name

    default_organization_env_var_ = patch.dict(
        os.environ, {DEFAULT_ORGANIZATION_ENV_VAR: organization_name}
    )

    with config_loader_, organization_list_api_, default_organization_env_var_:
        vessl.configure_organization()

    assert vessl.vessl_api.organization.name == organization_name
    assert VesslConfigLoader(config_path_api).default_organization == organization_name

    # Test `CREDENTIALS_FILE_ENV_VAR`
    organization_name = "org4"
    organization.name = organization_name
    config_loader.default_organization = organization_name

    credentials_file_env_var_ = patch.dict(
        os.environ, {CREDENTIALS_FILE_ENV_VAR: config_path_api}
    )

    with config_loader_, organization_list_api_, credentials_file_env_var_:
        vessl.configure_organization()

    assert vessl.vessl_api.organization.name == organization_name
    assert VesslConfigLoader(config_path_api).default_organization == organization_name

    # Test fail: no organizations
    response.organizations = []
    with organization_list_api_:
        with pytest.raises(InvalidOrganizationError):
            vessl.configure_organization(organization_name=organization_name)

    # Test fail: no such organization
    response.organizations = [Mock()]
    with organization_list_api_:
        with pytest.raises(InvalidOrganizationError):
            vessl.configure_organization(organization_name="nonexistent_organization")


def test_configure_project():
    config_loader = VesslConfigLoader(config_path_api)
    project = Mock()
    response = Mock()
    response.results = [project]

    config_loader_ = patch("vessl.vessl_api.config_loader", config_loader)
    project_list_api_ = patch("vessl.vessl_api.project_list_api", return_value=response)

    # Test `project_name`
    project_name = "proj1"
    project.name = project_name

    with config_loader_, project_list_api_:
        vessl.configure_project(project_name=project_name)

    assert vessl.vessl_api.project.name == project_name
    assert VesslConfigLoader(config_path_api).default_project == project_name

    # Test `credentials_file`
    project_name = "proj2"
    project.name = project_name
    config_loader.default_project = project_name

    with config_loader_, project_list_api_:
        vessl.configure_project(credentials_file=config_path_api)

    assert vessl.vessl_api.project.name == project_name
    assert VesslConfigLoader(config_path_api).default_project == project_name

    # Test `CREDENTIALS_FILE_ENV_VAR`
    project_name = "proj3"
    project.name = project_name
    config_loader.default_project = project_name

    credentials_file_env_var_ = patch.dict(
        os.environ, {CREDENTIALS_FILE_ENV_VAR: config_path_api}
    )

    with config_loader_, project_list_api_, credentials_file_env_var_:
        vessl.configure_project()

    assert vessl.vessl_api.project.name == project_name
    assert VesslConfigLoader(config_path_api).default_project == project_name

    # Test fail: no projects
    response.results = []
    with project_list_api_:
        with pytest.raises(InvalidProjectError):
            vessl.configure_project(project_name=project_name)

    # Test fail: no such project
    response.results = [Mock()]
    with project_list_api_:
        with pytest.raises(InvalidProjectError):
            vessl.configure_project(project_name="nonexistent_project")
