from unittest.mock import ANY

import ckan.model as model
import ckan.plugins.toolkit as tk
import pytest

from ckanext.flakes.model import Flake


@pytest.mark.usefixtures("with_plugins", "clean_db")
class TestDBValdiators:
    def test_flake_id_exists(self, user):
        validator = tk.get_validator("flakes_flake_id_exists")

        assert tk.navl_validate(
            {"id": "not-real"}, {"id": [validator]}, {"session": model.Session}
        )[1]

        flake = Flake(data={}, author_id=user["id"])
        model.Session.add(flake)
        model.Session.commit()
        assert not tk.navl_validate(
            {"id": flake.id}, {"id": [validator]}, {"session": model.Session}
        )[1]


@pytest.mark.usefixtures("with_plugins")
class TestIntoApiAction:
    def test_existing(self):
        validator = tk.get_validator("flakes_into_api_action")
        data, errors = tk.navl_validate(
            {"action": "package_create"}, {"action": [validator]}
        )
        assert data["action"] == tk.get_action("package_create")
        assert not errors

        data, errors = tk.navl_validate(
            {"action": "flakes_flake_update"}, {"action": [validator]}
        )
        assert data["action"] == tk.get_action("flakes_flake_update")
        assert not errors

    def test_non_existing(self):
        validator = tk.get_validator("flakes_into_api_action")
        data, errors = tk.navl_validate(
            {"action": "not-a-real-action"}, {"action": [validator]}
        )
        assert data == {"action": "not-a-real-action"}
        assert errors == {"action": [ANY]}
