import logging

import pytest

log = logging.getLogger(__name__)

try:
    import flywheel
except (ImportError, ModuleNotFoundError) as e:
    raise ValueError(
        "This module requires flywheel-sdk, please install the `flywheel` extra."
    ) from e

default_gear = {
    "name": "a-gear",
    "version": "0.0.0",
    "inputs": {
        "api-key": {"base": "api-key"},
        "file0": {"base": "file", "description": "a file"},
    },
    "config": {"config0": {"type": "string", "default": False, "description": ""}},
    "custom": {
        "gear-builder": {"image": "image-name"},
        "docker-image": "image-name",
    },
}


def make_gear(updates=None):
    """Make a gear manifest.

    Default values:
        {
            name: "a-gear",
            version: "0.0.0",
            inputs: {
                "api-key": {"base": "api-key"},
                "file0": {"base": "file", "description": "a file"},
            },
            config: {"config0": {"type": "string", "default": False, "description": ""}},
            custom: {
                "gear-builder": {"image": "image-name"},
                "docker-image": "image-name",
            },
        }

    Pass in dictionary of dotty keys to update the default dictionary, i.e.:
    ```python
    >>> gear = make_gear({'config.debug':{'type':'boolean','default': False}})
    ```
    """
    try:
        from dotty_dict import dotty
    except (ModuleNotFoundError, ImportError):
        raise RuntimeError("Please install `dotty_dict` to use this function")
    my_gear = dotty(default_gear)
    if updates:
        for k, v in updates.items():
            my_gear[k] = v
    print(my_gear)
    return flywheel.Gear(**my_gear)


@pytest.fixture
def gear_fixture():
    """Wrapper for `make_gear`."""
    return make_gear


def get_gear_doc(category=None, gear=None):
    """Create a gear doc from a gear and category."""
    default_category = "utility"
    if not gear:
        gear = gear_fixture()
    if not category:
        category = default_category
    return flywheel.GearDoc(category=category, gear=gear)


@pytest.fixture(scope="function")
def gear_doc(gear_fixture):
    """Wrapper for `get_gear_doc`."""

    return get_gear_doc
