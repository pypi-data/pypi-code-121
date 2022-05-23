import ckan.model as model
import pytest
from sqlalchemy.exc import IntegrityError

from ckanext.flakes.model.flake import Flake


@pytest.mark.usefixtures("with_plugins", "clean_db")
class TestFlake:
    def test_autoremove_with_user(self, user):
        flake = Flake(data={}, author_id=user["id"])
        model.Session.add(flake)
        model.Session.commit()

        assert model.Session.query(Flake).filter_by(id=flake.id).one_or_none()

        userobj = model.User.get(user["id"])
        model.Session.delete(userobj)
        model.Session.commit()

        assert (
            not model.Session.query(Flake).filter_by(id=flake.id).one_or_none()
        )

    def test_user_not_removed_with_flake(self, user):
        flake = Flake(data={}, author_id=user["id"])
        model.Session.add(flake)
        model.Session.commit()

        assert model.Session.query(Flake).filter_by(id=flake.id).one_or_none()
        assert model.User.get(user["id"])

        model.Session.delete(flake)
        model.Session.commit()

        assert (
            not model.Session.query(Flake).filter_by(id=flake.id).one_or_none()
        )
        assert model.User.get(user["id"])

    def test_relationship(self, user):
        parent = Flake(data={}, author_id=user["id"])
        brother = Flake(data={}, author_id=user["id"], parent=parent)
        sister = Flake(data={}, author_id=user["id"], parent=parent)
        model.Session.add_all([parent, brother, sister])
        model.Session.commit()

        assert set(parent.flakes) == {brother, sister}
        assert brother.parent == parent
        assert sister.parent == parent

    def test_autoremove_of_children(self, user):
        parent = Flake(data={}, author_id=user["id"])
        brother = Flake(data={}, author_id=user["id"], parent=parent)
        sister = Flake(data={}, author_id=user["id"], parent=parent)
        model.Session.add_all([parent, brother, sister])
        model.Session.commit()

        q = model.Session.query(Flake)

        assert q.filter_by(id=parent.id).one_or_none()
        assert q.filter_by(id=brother.id).one_or_none()
        assert q.filter_by(id=sister.id).one_or_none()

        model.Session.delete(brother)
        model.Session.commit()
        assert q.filter_by(id=parent.id).one_or_none()
        assert not q.filter_by(id=brother.id).one_or_none()
        assert q.filter_by(id=sister.id).one_or_none()

        model.Session.delete(parent)
        model.Session.commit()
        assert not q.filter_by(id=parent.id).one_or_none()
        assert not q.filter_by(id=brother.id).one_or_none()
        assert not q.filter_by(id=sister.id).one_or_none()

    def test_empty_name_no_unique(self, user):
        model.Session.add_all(
            [
                Flake(data={}, author_id=user["id"]),
                Flake(data={}, author_id=user["id"]),
            ]
        )
        model.Session.commit()

    def test_same_name_can_be_used_by_different_user(self, user_factory):
        first = user_factory()
        second = user_factory()

        model.Session.add_all(
            [
                Flake(data={}, name="name", author_id=first["id"]),
                Flake(data={}, name="name", author_id=second["id"]),
            ]
        )
        model.Session.commit()

    def test_same_name_canont_be_used_by_same_user(self, user):
        model.Session.add_all(
            [
                Flake(data={}, name="name", author_id=user["id"]),
                Flake(data={}, name="name", author_id=user["id"]),
            ]
        )
        with pytest.raises(IntegrityError):
            model.Session.commit()

    def test_search_by_name(self, user_factory):
        first = user_factory()
        second = user_factory()

        f1 = Flake(data={}, name="first", author_id=first["id"])
        f2 = Flake(data={}, name="second", author_id=second["id"])
        model.Session.add_all(
            [
                f1,
                f2,
            ]
        )
        model.Session.commit()

        assert not Flake.by_name(f1.name, f2.author_id)
        assert not Flake.by_name(f2.name, f1.author_id)

        assert Flake.by_name(f1.name, f1.author_id) == f1
        assert Flake.by_name(f2.name, f2.author_id) == f2

    def test_search_by_extra(self, user_factory):
        first = user_factory()
        second = user_factory()

        f1 = Flake(data={}, extras={"tag": "hello"}, author_id=first["id"])
        f2 = Flake(data={}, extras={"tag": "hello"}, author_id=second["id"])
        f3 = Flake(
            data={}, extras={"tag": {"nested": "hello"}}, author_id=first["id"]
        )
        model.Session.add_all([f1, f2, f3])
        model.Session.commit()

        assert list(Flake.by_extra(["tag"], "hello", f2.author_id)) == [f2]
        assert list(Flake.by_extra(["tag"], "hello", f1.author_id)) == [f1]

        assert list(
            Flake.by_extra(["tag", "nested"], "hello", f1.author_id)
        ) == [f3]
        assert (
            list(Flake.by_extra(["tag", "nested"], "hello", f2.author_id))
            == []
        )

    def test_search_by_author(self, user_factory):
        first = user_factory()
        second = user_factory()

        f1 = Flake(data={}, author_id=first["id"])
        f2 = Flake(data={}, author_id=second["id"])
        model.Session.add_all(
            [
                f1,
                f2,
            ]
        )
        model.Session.commit()

        assert list(Flake.by_author(f2.author_id)) == [f2]
        assert list(Flake.by_author(f1.author_id)) == [f1]
