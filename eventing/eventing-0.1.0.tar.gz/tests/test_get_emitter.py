import pytest

import eventing


def test_get_emitter_of_same_name_is_same_instance():
    ee = eventing.get_emitter("foo")
    assert ee is eventing.get_emitter("foo")


def test_get_emitter_of_different_name_is_different_instance():
    ee = eventing.get_emitter("foo")
    assert ee is not eventing.get_emitter("bar")


def test_get_emitter_with_no_name_same_as_root():
    ee = eventing.get_emitter()
    assert ee is eventing.get_emitter("root")


def test_emitter_name_must_be_string():
    with pytest.raises(TypeError):
        eventing.get_emitter(False)
