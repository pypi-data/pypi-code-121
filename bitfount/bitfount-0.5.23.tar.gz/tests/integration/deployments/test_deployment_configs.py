"""Tests deployment config files can be loaded."""
import desert
from jinja2 import Environment, FileSystemLoader, select_autoescape
import pytest
import yaml

from bitfount.runners.config_schemas import PodConfig
from tests.integration import DEPLOYMENTS_DIRECTORY
from tests.utils.helper import integration_test


@integration_test
@pytest.mark.parametrize("config_file", ["census_income_config.yaml"])
def test_staging_deployment_configs_are_valid(config_file: str) -> None:
    """Test that the staging pod deployment configs are valid."""
    expected_username = "someTestUser"
    env = Environment(
        loader=FileSystemLoader(DEPLOYMENTS_DIRECTORY), autoescape=select_autoescape()
    )

    template = env.get_template(config_file + ".j2")
    rendered_config = template.render(
        env={"USERNAME": expected_username, "STAGING": "true"}
    )
    config_yaml = yaml.safe_load(rendered_config)
    config = desert.schema(PodConfig).load(config_yaml)

    assert config.username == expected_username
    assert "staging" in config.access_manager.url
    assert "staging" in config.hub.url
    assert "staging" in config.message_service.url


@integration_test
@pytest.mark.parametrize("config_file", ["census_income_config.yaml"])
def test_production_deployment_configs_are_valid(config_file: str) -> None:
    """Test that the production pod deployment configs are valid."""
    expected_username = "anotherTestUser"
    env = Environment(
        loader=FileSystemLoader(DEPLOYMENTS_DIRECTORY), autoescape=select_autoescape()
    )

    template = env.get_template(config_file + ".j2")
    rendered_config = template.render(env={"USERNAME": expected_username})
    config_yaml = yaml.safe_load(rendered_config)
    config = desert.schema(PodConfig).load(config_yaml)

    assert config.username == expected_username
    assert "staging" not in config.access_manager.url
    assert "staging" not in config.hub.url
    assert "staging" not in config.message_service.url
