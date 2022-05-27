"""Utility modules for tests."""
from _pytest.fixtures import SubRequest
from typing_extensions import TypeAlias

# It's actually `SubRequest` that has the `param` attribute guaranteed so this
# is what we want for type checking purposes, even though it's not part of the
# public API.
PytestRequest: TypeAlias = SubRequest
