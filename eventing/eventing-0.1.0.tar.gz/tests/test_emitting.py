from unittest.mock import Mock

import pytest

import eventing


@pytest.fixture
def ee():
    return eventing.get_emitter()


@pytest.fixture
def add_mock_listener(ee):
    def _add_mock_listener(event_name):
        mock_listener = Mock(return_value=None)
        ee.add_listener(event_name, mock_listener)
        return mock_listener

    return _add_mock_listener


def test_emit_with_no_listeners_does_nothing(ee):
    ee.emit("foo")


def test_listener_of_event_called_once_on_emit(ee, add_mock_listener):
    foo_listener = add_mock_listener("foo")
    ee.emit("foo")
    foo_listener.assert_called_once()


def test_listener_called_with_emitted_positional_data(ee, add_mock_listener):
    foo_listener = add_mock_listener("foo")
    ee.emit("foo", "bar")
    foo_listener.assert_called_once_with("bar")


def test_listener_called_with_emitted_keyword_data(ee, add_mock_listener):
    foo_listener = add_mock_listener("foo")
    ee.emit("foo", bar=True, baz=1.0)
    foo_listener.assert_called_once_with(baz=1.0, bar=True)


def test_listener_not_called_on_different_event_emitted(ee, add_mock_listener):
    foo_listener = add_mock_listener("foo")
    ee.emit("bar")
    foo_listener.assert_not_called()


def test_all_added_listeners_get_called_on_emit(ee, add_mock_listener):
    foo_listeners = [add_mock_listener("foo") for _ in range(3)]
    ee.emit("foo")
    [foo_listener.assert_called_once() for foo_listener in foo_listeners]


def test_emit_returns_false_if_it_had_no_listeners(ee):
    assert ee.emit("foo") is False


def test_emit_returns_true_if_it_had_listeners(ee, add_mock_listener):
    _ = add_mock_listener("foo")
    assert ee.emit("foo") is True


def test_listener_not_call_for_same_event_on_different_emitter(
    ee, add_mock_listener
):
    foo_listener = add_mock_listener("foo")
    bar_ee = eventing.get_emitter("bar")
    bar_ee.emit("foo")
    foo_listener.assert_not_called()
