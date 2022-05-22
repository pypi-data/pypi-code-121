import ckan.model as model
import ckan.plugins.toolkit as tk
import pytest
from ckan.tests.helpers import call_action

from ckanext.flakes.model import Flake


@pytest.mark.usefixtures("with_plugins", "clean_db")
class TestFlakeCreate:
    def test_user_required(self, user):
        with pytest.raises(tk.NotAuthorized):
            call_action("flakes_flake_create", data={})

    def test_base(self, user):
        result = call_action("flakes_flake_create", {"user": user["name"]}, data={})
        assert model.Session.query(Flake).filter_by(id=result["id"]).one()

    def test_name_must_be_unique_for_user(self, user, user_factory):
        another_user = user_factory()
        result = call_action(
            "flakes_flake_create", {"user": user["name"]}, data={}, name="hello-world"
        )
        assert result["name"] == "hello-world"

        with pytest.raises(tk.ValidationError):
            call_action(
                "flakes_flake_create",
                {"user": user["name"]},
                data={},
                name="hello-world",
            )

        another = call_action(
            "flakes_flake_create",
            {"user": another_user["name"]},
            data={},
            name="hello-world",
        )
        assert another["name"] == "hello-world"

    def test_parent_must_be_real(self, user):
        with pytest.raises(tk.ValidationError):
            call_action(
                "flakes_flake_create",
                {"user": user["name"]},
                data={},
                parent_id="not-real",
            )

    def test_normal_parent(self, user):
        parent = call_action("flakes_flake_create", {"user": user["name"]}, data={})

        child = call_action(
            "flakes_flake_create",
            {"user": user["name"]},
            data={},
            parent_id=parent["id"],
        )
        assert child["parent_id"] == parent["id"]

    def test_parent_from_other_user(self, user, user_factory):
        another_user = user_factory()
        parent = call_action("flakes_flake_create", {"user": user["name"]}, data={})
        with pytest.raises(tk.ValidationError):
            call_action(
                "flakes_flake_create",
                {"user": another_user["name"]},
                data={},
                parent_id=parent["id"],
            )


@pytest.mark.usefixtures("with_plugins", "clean_db")
class TestFlakeUpdate:
    def test_base(self, flake):
        q = model.Session.query(Flake).filter_by(id=flake["id"])
        context = {"model": model, "session": model.Session}

        assert q.one().dictize(context) == flake

        updated = call_action(
            "flakes_flake_update", id=flake["id"], data={"hello": "world"}
        )
        assert flake["id"] == updated["id"]
        assert updated["data"] == {"hello": "world"}
        assert q.one().dictize(context) == updated

    def test_missing(self):
        with pytest.raises(tk.ObjectNotFound):
            call_action("flakes_flake_update", id="not-real", data={})


@pytest.mark.usefixtures("with_plugins", "clean_db")
class TestFlakeDelete:
    def test_base(self, flake):
        call_action("flakes_flake_delete", id=flake["id"])
        assert not model.Session.query(Flake).filter_by(id=flake["id"]).one_or_none()

    def test_missing(self):
        with pytest.raises(tk.ObjectNotFound):
            call_action("flakes_flake_delete", id="not-real")


@pytest.mark.usefixtures("with_plugins", "clean_db")
class TestFlakeShow:
    def test_missing(self):
        with pytest.raises(tk.ObjectNotFound):
            call_action("flakes_flake_show", id="not-real")

    def test_base(self, flake_factory):
        flake = flake_factory(
            data={"hello": "world", "override": "parent"},
        )
        result = call_action("flakes_flake_show", id=flake["id"])
        assert flake == result

    def test_parent(self, flake_factory):
        parent = flake_factory(data={"hello": "world"})
        child = flake_factory(
            data={"override": "child"},
            parent_id=parent["id"],
        )

        result = call_action("flakes_flake_show", id=child["id"])
        assert result["data"] == {"override": "child"}

        result = call_action("flakes_flake_show", id=child["id"], expand=True)
        assert result["data"] == {"override": "child", "hello": "world"}


@pytest.mark.usefixtures("with_plugins", "clean_db")
class TestFlakeList:
    def test_base(self, user, flake_factory):
        first = flake_factory(
            user=user,
            data={},
        )
        second = flake_factory(
            user=user,
            data={},
        )
        result = call_action("flakes_flake_list", {"user": user["id"]})
        assert {first["id"], second["id"]} == {f["id"] for f in result}

    def test_parent(self, user, flake_factory):
        parent = flake_factory(
            user=user,
            data={"hello": "world"},
        )

        flake_factory(
            user=user,
            data={"override": "first"},
        )
        flake_factory(
            user=user,
            data={"override": "second"},
            parent_id=parent["id"],
        )

        result = call_action("flakes_flake_list", {"user": user["id"]})
        datas = [f["data"] for f in result]
        assert {"hello": "world"} in datas
        assert {"override": "first"} in datas
        assert {"override": "second"} in datas

        result = call_action("flakes_flake_list", {"user": user["id"]}, expand=True)
        datas = [f["data"] for f in result]
        assert {"hello": "world"} in datas
        assert {"override": "first"} in datas
        assert {"hello": "world", "override": "second"} in datas


@pytest.mark.usefixtures("with_plugins", "clean_db")
class TestFlakeLookup:
    def test_base(self, flake_factory, user):
        hello = flake_factory(name="hello", user=user)
        world = flake_factory(name="world", user=user)
        anon = flake_factory(user=user)

        assert (
            call_action("flakes_flake_lookup", {"user": user["name"]}, name="hello")
            == hello
        )
        assert (
            call_action("flakes_flake_lookup", {"user": user["name"]}, name="world")
            == world
        )
        assert (
            call_action("flakes_flake_lookup", {"user": user["name"]}, name=None)
            == anon
        )

    def test_not_real(self, user):
        with pytest.raises(tk.ObjectNotFound):
            call_action("flakes_flake_lookup", {"user": user["name"]}, name="not-real")

    def test_different_user(self, flake_factory, user):
        flake = flake_factory(name="flake")

        with pytest.raises(tk.ObjectNotFound):
            call_action(
                "flakes_flake_lookup", {"user": user["name"]}, name=flake["name"]
            )


@pytest.mark.ckan_config("ckan.plugins", "flakes flakes_test")
@pytest.mark.usefixtures("with_plugins", "clean_db")
class TestFlakeValidate:
    def test_missing(self):
        with pytest.raises(tk.ObjectNotFound):
            call_action("flakes_flake_validate", id="not-real", schema="empty")

    def test_base(self, flake):
        schema = "empty"
        result = call_action("flakes_flake_validate", id=flake["id"], schema=schema)

        assert result == call_action(
            "flakes_data_validate", data=flake["data"], schema=schema
        )

    def test_expanded(self):
        # TODO: spent another 1.5 minutes on this test
        pass


@pytest.mark.ckan_config("ckan.plugins", "flakes flakes_test")
@pytest.mark.usefixtures("with_plugins")
class TestDataValidate:
    def test_base(self):
        data = {"hello": "world"}
        result = call_action("flakes_data_validate", data=data, schema="empty")

        assert result == {"errors": {}, "data": {"__extras": data}}
