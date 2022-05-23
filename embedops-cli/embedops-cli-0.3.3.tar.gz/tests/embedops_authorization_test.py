"""
`embedops_authorization_test`
=======================================================================
Unit tests for the authorization retrival and storage for EmbedOps 
* Author(s): Bailey Steinfadt
"""

import os
import pytest

from embedops_cli import embedops_authorization
from embedops_cli.eo_types import UnauthorizedUserException, LoginFailureException, DockerRegistryException


def test_set_and_get_auth_token():
    """testing setting token"""
    test_secret = "SUPER_DUPER_SECRET_TOKEN_SAUCE"
    test_secret_file = ".test_eosecrets.toml"

    embedops_authorization.set_auth_token(test_secret, test_secret_file)
    retrieved_secret = embedops_authorization.get_auth_token(test_secret_file)

    assert test_secret == retrieved_secret

    os.remove(test_secret_file)


def test_set_and_get_registry_token():
    """testing setting token"""
    test_secret = "YULE NEFFER GESS WOT"
    test_secret_file = ".test_eosecrets.toml"

    embedops_authorization.set_registry_token(test_secret, test_secret_file)
    retrieved_secret = embedops_authorization.get_registry_token(test_secret_file)

    assert test_secret == retrieved_secret

    os.remove(test_secret_file)


def test_setting_both_tokens():
    """Test that both the registry token and auth token can be read and written together"""

    auth_secret = "SUPER_DUPER_SECRET_TOKN_SAUCE"
    other_auth_secret = "THIS IS THE GOOD ONE"
    registry_secret = "YULE NEFFER GESS WOT"

    test_secret_file = ".test_eosecrets.toml"

    embedops_authorization.set_auth_token(auth_secret, test_secret_file)
    embedops_authorization.set_registry_token(registry_secret, test_secret_file)

    read_auth_token = embedops_authorization.get_auth_token(test_secret_file)
    read_registry_token = embedops_authorization.get_registry_token(test_secret_file)

    assert auth_secret == read_auth_token
    assert registry_secret == read_registry_token

    embedops_authorization.set_auth_token(other_auth_secret, test_secret_file)
    read_auth_token = embedops_authorization.get_auth_token(test_secret_file)
    read_registry_token = embedops_authorization.get_registry_token(test_secret_file)

    assert other_auth_secret == read_auth_token
    assert registry_secret == read_registry_token

    os.remove(test_secret_file)


def test_login_to_registry_no_registry_credentials_fails_login(mocker):
    """Test that the function handles non-existent creds correctly"""

    mock_docker_cli_login = mocker.patch(
        "embedops_cli.embedops_authorization.docker_cli_login",
        return_value=2 # docker cli process returns exit code 2 if login failed
    )

    with pytest.raises(UnauthorizedUserException) as pytest_wrapped_e:
        embedops_authorization.login_to_registry("non-existent-secrets.toml")

    assert pytest_wrapped_e.type == UnauthorizedUserException
    mock_docker_cli_login.assert_not_called()


def test_login_to_registry_incorrect_registry_credentials_fails_login(mocker):
    """Test that the function handles invalid credentials correctly"""

    mocker.patch(
        "embedops_cli.embedops_authorization.get_registry_token",
        return_value="BAD_TOKEN_BAD"
    )
    mocker.patch(
        "embedops_cli.embedops_authorization.docker_cli_login",
        return_value=1 # docker cli process returns exit code 1 if login failed
    )

    with pytest.raises(DockerRegistryException) as pytest_wrapped_e:
        embedops_authorization.login_to_registry()

    assert pytest_wrapped_e.type == DockerRegistryException


def test_login_to_registry(mocker):
    """Test that the function handles a successful login correctly"""
    mock_get_registry_token = mocker.patch(
        "embedops_cli.embedops_authorization.get_registry_token",
        return_value="MAGIC_GOOD_TOKEN"
    )
    mock_docker_cli_login = mocker.patch(
        "embedops_cli.embedops_authorization.docker_cli_login",
        return_value=0 
    )
    try:
        embedops_authorization.login_to_registry()
    except Exception as exc:
        assert False, f"'test_login_to_registry' raised an exception {exc}"

    mock_get_registry_token.assert_called()
    mock_docker_cli_login.assert_called()
