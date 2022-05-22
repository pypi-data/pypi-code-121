import ckan.model as model
import ckan.plugins.toolkit as tk
import pytest

from ckanext.flakes.model import Flake


@pytest.mark.usefixtures("with_plugins", "clean_db")
class TestValdiators:
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
