"""Fixtures and other pytest specific components for the transformation tests."""
from _pytest.monkeypatch import MonkeyPatch
from pytest import fixture


@fixture
def fake_uuid(monkeypatch: MonkeyPatch) -> None:
    """Patch the uuid4().hex calls in base_transformation."""
    import bitfount.transformations.base_transformation as base_transformation

    class FakeUUID:
        hex = "FAKE_HEX"

    def fake_uuid() -> FakeUUID:
        return FakeUUID()

    monkeypatch.setattr(base_transformation, "uuid4", fake_uuid)


@fixture
def empty_registry(monkeypatch: MonkeyPatch) -> None:
    """Ensure an empty registry in base_transformation."""
    import bitfount.transformations.base_transformation as base_transformation

    monkeypatch.setattr(base_transformation, "TRANSFORMATION_REGISTRY", {})
