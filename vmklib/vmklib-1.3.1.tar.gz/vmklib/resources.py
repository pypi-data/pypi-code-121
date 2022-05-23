"""
A module for finding package resources.
"""

# built-in
import os
from pathlib import Path

# third-party
import pkg_resources
from vcorelib.paths import find_file


def get_resource(resource_name: str) -> Path:
    """Locate the path to a package resource."""

    resource_path = str(Path(os.path.join("data", resource_name)).parent)

    locations = [
        pkg_resources.resource_filename(__name__, resource_path),
        os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            resource_path,
        ),
    ]
    found = find_file(
        Path(resource_name).name,
        locations,
    )

    # ensure that the resource can actually be found
    assert found is not None, (
        f"Couldn't load resource '{resource_name}' in: "
        f"{', '.join(locations)}!"
    )
    return found
