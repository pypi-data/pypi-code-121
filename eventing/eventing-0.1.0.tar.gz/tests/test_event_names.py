import pytest

import eventing


@pytest.fixture(
    params=[
        "listener_count",
        "listeners",
        "add_listener",
        "remove_listener",
        "emit",
    ]
)
def mocked_event_name_func(request, auto_bind_func_with_mocks_from_signature):
    ee = eventing.get_emitter()
    func = getattr(ee, request.param)
    return auto_bind_func_with_mocks_from_signature(func)


def test_event_names_may_only_be_strings(mocked_event_name_func):
    with pytest.raises(TypeError):
        mocked_event_name_func(event_name=False)


def test_event_name_may_not_be_empty(mocked_event_name_func):
    with pytest.raises(ValueError, match="must not be empty"):
        mocked_event_name_func(event_name="")
