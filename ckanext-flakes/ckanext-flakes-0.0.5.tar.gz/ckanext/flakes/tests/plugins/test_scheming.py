from unittest.mock import ANY

import ckan.plugins.toolkit as tk
import pytest
from ckan.tests.helpers import call_action


@pytest.mark.ckan_config(
    "ckan.plugins",
    "flakes flakes_scheming scheming_datasets scheming_groups"
    " scheming_organizations",
)
@pytest.mark.usefixtures("with_plugins")
class TestPlugin:
    def test_organization(self):
        result = call_action(
            "flakes_data_validate",
            {"include_data": True},
            data={"flake_name": "name", "hello": "world"},
            schema="scheming_organization_flake-organization",
        )
        assert result == {
            "data": {
                "__extras": {"hello": "world"},
                "flake_name": "name",
                "flake_title": tk.missing,
            },
            "errors": {"flake_title": [ANY]},
        }

    def test_group(self):
        result = call_action(
            "flakes_data_validate",
            {"include_data": True},
            data={"flake_name": "name", "hello": "world"},
            schema="scheming_group_flake-group",
        )
        assert result == {
            "data": {
                "__extras": {"hello": "world"},
                "flake_name": "name",
                "flake_title": tk.missing,
            },
            "errors": {"flake_title": [ANY]},
        }

    def test_dataset(self):
        result = call_action(
            "flakes_data_validate",
            {"include_data": True},
            data={"flake_name": "name", "hello": "world"},
            schema="scheming_dataset_flake-dataset",
        )
        assert result == {
            "data": {
                "__extras": {"hello": "world"},
                "flake_name": "name",
                "flake_title": tk.missing,
            },
            "errors": {"flake_title": [ANY]},
        }

    def test_resource(self):
        result = call_action(
            "flakes_data_validate",
            {"include_data": True},
            data={"flake_name": "name", "hello": "world"},
            schema="scheming_resource_flake-dataset",
        )
        assert result == {
            "data": {"__extras": {"hello": "world"}, "flake_name": "name"},
            "errors": {},
        }
