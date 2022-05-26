import pytest
import sys
from pathlib import Path

from cosapp.systems import System


@pytest.fixture
def test_library():
    library_path = Path(__file__).parent / "library" / "systems"

    # Add path to allow System to find the component
    sys.path.append(str(library_path))
    try:
        yield library_path
    finally:
        # Undo path modification
        sys.path.remove(str(library_path))


@pytest.fixture
def test_data():
    return Path(__file__).parent / "data"


@pytest.fixture(scope="function")
def DummySystemFactory():
    """Factory creating a dummy system class with custom attributes"""
    # mapping option / method
    # for example: `inputs` <-> `add_input`
    mapping = dict(
        (option, f"add_{option[:-1]}")
        for option in (
            "inputs", "outputs", "inwards", "outwards",
            "transients", "rates", "unknowns", "equations",
            "targets", "design_methods",
        )
    )
    mapping["properties"] = "add_property"
    traits = set(mapping)

    def Factory(classname, **settings):
        method_dict = dict(
            (mapping[option], settings.get(option))
            for option in traits.intersection(settings)
        )
        base = settings.get("base", System)
        class Prototype(base):
            def setup(self, **kwargs):
                super().setup(**kwargs)
                for method, values in method_dict.items():
                    if values is None:
                        continue
                    if not isinstance(values, list):
                        values = [values]
                    for args, kwargs in values:  # expects a list of (tuple, dict)
                        getattr(self, method)(*args, **kwargs)
        return type(classname, (Prototype,), {})

    return Factory
