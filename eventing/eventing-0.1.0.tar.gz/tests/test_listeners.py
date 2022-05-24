import pytest

import eventing


@pytest.fixture
def ee():
    return eventing.get_emitter()


def a_listener():
    pass


def test_emitter_without_added_listeners_has_no_listeners(ee):
    assert ee.listener_count("foo") == 0


def test_event_with_one_added_listener_has_one_listener(ee):
    ee.add_listener("foo", a_listener)
    assert ee.listener_count("foo") == 1


def test_event_with_two_added_listeners_has_two_listeners(ee):
    ee.add_listener("foo", a_listener)
    # Same listener is okay
    ee.add_listener("foo", a_listener)
    assert ee.listener_count("foo") == 2


def test_listeners_for_event_with_no_listeners_returns_empty_list(ee):
    assert ee.listeners("foo") == []


def test_added_listener_is_returned_with_get_listeners(ee):
    ee.add_listener("foo", a_listener)
    assert ee.listeners("foo") == [a_listener]


def test_removing_listener_for_not_added_listener_warns(ee):
    with pytest.warns(UserWarning):
        ee.remove_listener("foo", a_listener)


def test_added_listener_can_be_removed(ee):
    ee.add_listener("foo", a_listener)
    ee.remove_listener("foo", a_listener)
    assert ee.listeners("foo") == []


def test_removing_a_listener_removes_only_one_if_multiple(ee):
    ee.add_listener("foo", a_listener)
    ee.add_listener("foo", a_listener)
    ee.remove_listener("foo", a_listener)
    assert ee.listeners("foo") == [a_listener]


def test_adding_listener_to_an_event_doesnt_affect_another(ee):
    ee.add_listener("foo", a_listener)
    assert ee.listeners("bar") == []
    assert ee.listener_count("bar") == 0


def test_add_listener_returns_the_emitter(ee):
    assert ee.add_listener("foo", a_listener) is ee


def test_removing_listener_returns_the_emitter(ee):
    assert ee.remove_listener("foo", a_listener) is ee
