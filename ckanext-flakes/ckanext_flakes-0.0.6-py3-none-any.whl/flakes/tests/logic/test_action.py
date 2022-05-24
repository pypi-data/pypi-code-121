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
        result = call_action(
            "flakes_flake_create", {"user": user["name"]}, data={}
        )
        assert model.Session.query(Flake).filter_by(id=result["id"]).one()

    def test_name_must_be_unique_for_user(self, user, user_factory):
        another_user = user_factory()
        result = call_action(
            "flakes_flake_create",
            {"user": user["name"]},
            data={},
            name="hello-world",
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
        parent = call_action(
            "flakes_flake_create", {"user": user["name"]}, data={}
        )

        child = call_action(
            "flakes_flake_create",
            {"user": user["name"]},
            data={},
            parent_id=parent["id"],
        )
        assert child["parent_id"] == parent["id"]

    def test_parent_from_other_user(self, user, user_factory):
        another_user = user_factory()
        parent = call_action(
            "flakes_flake_create", {"user": user["name"]}, data={}
        )
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
class TestFlakeOverride:
    def test_user_can_override_new(self, user):
        overriden = call_action(
            "flakes_flake_override",
            {"user": user["name"]},
            name="flake",
            data={"hello": "world"},
        )
        assert overriden["name"] == "flake"
        assert overriden["data"] == {"hello": "world"}

    def test_user_can_override_existing(self, user, flake_factory):
        flake = flake_factory(user=user, name="flake")

        overriden = call_action(
            "flakes_flake_override",
            {"user": user["name"]},
            name=flake["name"],
            data={"hello": "world"},
        )
        assert overriden["id"] == flake["id"]
        assert overriden["data"] == {"hello": "world"}


@pytest.mark.usefixtures("with_plugins", "clean_db")
class TestFlakeDelete:
    def test_base(self, flake):
        call_action("flakes_flake_delete", id=flake["id"])
        assert (
            not model.Session.query(Flake)
            .filter_by(id=flake["id"])
            .one_or_none()
        )

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

    def test_extra(self, user, flake_factory):
        first = flake_factory(
            user=user,
            extras={"xxx": {"yyy": "hello"}},
        )
        flake_factory(
            user=user,
            extras={"xxx": {"yyy": "world"}},
        )

        result = call_action(
            "flakes_flake_list",
            {"user": user["id"]},
            extra_value="hello",
            extra_path=["xxx", "yyy"],
        )
        assert {first["id"]} == {f["id"] for f in result}

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

        result = call_action(
            "flakes_flake_list", {"user": user["id"]}, expand=True
        )
        datas = [f["data"] for f in result]
        assert {"hello": "world"} in datas
        assert {"override": "first"} in datas
        assert {"hello": "world", "override": "second"} in datas


@pytest.mark.usefixtures("with_plugins", "clean_db")
class TestFlakeLookup:
    def test_base(self, flake_factory, user):
        hello = flake_factory(name="hello", user=user)
        world = flake_factory(name="world", user=user)
        flake_factory(user=user)

        assert (
            call_action(
                "flakes_flake_lookup", {"user": user["name"]}, name="hello"
            )
            == hello
        )
        assert (
            call_action(
                "flakes_flake_lookup", {"user": user["name"]}, name="world"
            )
            == world
        )

    def test_not_real(self, user):
        with pytest.raises(tk.ObjectNotFound):
            call_action(
                "flakes_flake_lookup", {"user": user["name"]}, name="not-real"
            )

    def test_different_user(self, flake_factory, user):
        flake = flake_factory(name="flake")

        with pytest.raises(tk.ObjectNotFound):
            call_action(
                "flakes_flake_lookup",
                {"user": user["name"]},
                name=flake["name"],
            )


@pytest.mark.ckan_config("ckan.plugins", "flakes flakes_test")
@pytest.mark.usefixtures("with_plugins", "clean_db")
class TestFlakeValidate:
    def test_missing(self):
        with pytest.raises(tk.ObjectNotFound):
            call_action("flakes_flake_validate", id="not-real", schema="empty")

    def test_base(self, flake):
        schema = "empty"
        result = call_action(
            "flakes_flake_validate", id=flake["id"], schema=schema
        )

        assert result == call_action(
            "flakes_data_validate", data=flake["data"], schema=schema
        )

    def test_expanded(self, flake, flake_factory):
        child = flake_factory(parent_id=flake["id"], data={"hello": "world"})

        result = call_action(
            "flakes_flake_validate",
            {"include_data": True},
            id=child["id"],
            schema="empty",
        )
        assert result["data"] == {"__extras": {"hello": "world"}}

        result = call_action(
            "flakes_flake_validate",
            {"include_data": True},
            id=child["id"],
            schema="empty",
            expand=True,
        )
        assert result["data"] == {
            "__extras": {**flake["data"], **{"hello": "world"}}
        }


@pytest.mark.ckan_config("ckan.plugins", "flakes flakes_test")
@pytest.mark.usefixtures("with_plugins")
class TestDataValidate:
    def test_base(self):
        data = {"hello": "world"}
        result = call_action(
            "flakes_data_validate",
            {"include_data": True},
            data=data,
            schema="empty",
        )

        assert result == {"errors": {}, "data": {"__extras": data}}

    def test_missing_schema(self):
        with pytest.raises(tk.ValidationError):
            call_action(
                "flakes_data_validate", data={}, schema="not-a-real-schema"
            )


@pytest.mark.ckan_config("ckan.plugins", "flakes flakes_test")
@pytest.mark.usefixtures("with_plugins")
class TestDataExample:
    def test_base(self):
        data = {"hello": "world"}

        result = call_action(
            "flakes_data_example", data=data, factory="identity"
        )
        assert result == {"data": data}

    def test_missing_schema(self):
        with pytest.raises(tk.ValidationError):
            call_action(
                "flakes_data_example", data={}, factory="not-a-real-factory"
            )


@pytest.mark.usefixtures("with_plugins", "clean_db")
class TestFlakeMaterialize:
    def test_missing(self):
        with pytest.raises(tk.ObjectNotFound):
            call_action(
                "flakes_flake_materialize",
                id="not-real",
                action="package_create",
            )

    def test_package_create(self, flake_factory):
        flake = flake_factory(data={"name": "flake-pkg"})
        result = call_action(
            "flakes_flake_materialize", id=flake["id"], action="package_create"
        )

        assert result == call_action("package_show", id=result["id"])
        assert flake == call_action("flakes_flake_show", id=flake["id"])

    def test_package_patch(self, flake_factory, package):
        flake = flake_factory(data={"name": "flake-pkg", "id": package["id"]})
        result = call_action(
            "flakes_flake_materialize", id=flake["id"], action="package_patch"
        )

        assert result == call_action("package_show", id=package["id"])
        assert result["name"] == "flake-pkg"

    def test_flake_removal(self, flake_factory):
        flake = flake_factory(data={"name": "flake-pkg"})
        call_action(
            "flakes_flake_materialize",
            id=flake["id"],
            action="package_create",
            remove=True,
        )

        with pytest.raises(tk.ObjectNotFound):
            call_action("flakes_flake_show", id=flake["id"])

    def test_expanded(self, flake_factory):
        parent = flake_factory(data={"title": "parent"})
        child = flake_factory(data={"name": "child"}, parent_id=parent["id"])

        slim = call_action(
            "flakes_flake_materialize", id=child["id"], action="package_create"
        )

        assert slim["name"] == "child"
        assert slim["title"] != "parent"
        slim = call_action(
            "flakes_flake_update", id=child["id"], data={"id": slim["id"]}
        )

        expanded = call_action(
            "flakes_flake_materialize",
            id=child["id"],
            action="package_patch",
            expand=True,
        )
        assert expanded["name"] == "child"
        assert expanded["title"] == "parent"


@pytest.mark.usefixtures("with_plugins", "clean_db")
class TestFlakeCombine:
    def test_one_missing(self, flake):
        with pytest.raises(tk.ObjectNotFound):
            call_action("flakes_flake_combine", id=[flake["id"], "not-real"])

    def test_empty(self, flake):
        result = call_action("flakes_flake_combine", id=[])
        assert result == {}

    def test_order(self, flake_factory):
        first = flake_factory()
        second = flake_factory()

        result = call_action(
            "flakes_flake_combine", id=[first["id"], second["id"]]
        )
        assert result == {**second["data"], **first["data"]}

        result = call_action(
            "flakes_flake_combine", id=[second["id"], first["id"]]
        )
        assert result == {**first["data"], **second["data"]}

    def test_expand(self, flake_factory):
        parent = flake_factory()
        child = flake_factory(parent_id=parent["id"])

        result = call_action("flakes_flake_combine", id=[child["id"]])
        assert result == child["data"]

        result = call_action(
            "flakes_flake_combine", id=[child["id"]], expand={"not-real": True}
        )
        assert result == child["data"]

        result = call_action(
            "flakes_flake_combine",
            id=[child["id"]],
            expand={child["id"]: True},
        )
        assert result == {**parent["data"], **child["data"]}


@pytest.mark.usefixtures("with_plugins", "clean_db")
class TestFlakeMerge:
    def test_new(self, flake_factory, user):
        flake = flake_factory(user=user)
        new = call_action(
            "flakes_flake_merge", {"user": user["name"]}, id=[flake["id"]]
        )
        assert new["id"] != flake["id"]
        assert new["data"] == flake["data"]

    def test_missing_destination(self, user, flake_factory):
        flake = flake_factory(user=user)
        with pytest.raises(tk.ObjectNotFound):
            call_action(
                "flakes_flake_merge",
                {"user": user["name"]},
                id=[flake["id"]],
                destination="not-real",
            )

    def test_destination(self, user, flake_factory):
        flake = flake_factory(user=user)
        dest = flake_factory(user=user)
        new = call_action(
            "flakes_flake_merge",
            {"user": user["name"]},
            id=[flake["id"]],
            destination=dest["id"],
        )

        assert new["id"] == dest["id"]
        assert new["data"] == flake["data"]

    def test_remove(self, flake_factory, user):
        flake = flake_factory(user=user)
        new = call_action(
            "flakes_flake_merge",
            {"user": user["name"]},
            id=[flake["id"]],
            remove=True,
        )

        assert call_action(
            "flakes_flake_show", {"user": user["name"]}, id=new["id"]
        )
        with pytest.raises(tk.ObjectNotFound):
            call_action(
                "flakes_flake_show", {"user": user["name"]}, id=flake["id"]
            )
