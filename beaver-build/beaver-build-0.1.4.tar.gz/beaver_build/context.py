import json
import logging
import os
import re
import typing
from . import artifacts


LOGGER = logging.getLogger(__name__)


class Context:
    """
    Context manager responsible for managing and updating state.
    """
    CURRENT_CONTEXT: "Context" = None
    CACHE_VERSION = "alpha"

    def __init__(self):
        self.artifacts = {}
        self.artifact_metadata = {}
        self.properties = {}

    def __enter__(self) -> "Context":
        if Context.CURRENT_CONTEXT is not None:
            raise RuntimeError("only one context can be active at the same time")
        Context.CURRENT_CONTEXT = self
        return self

    def __exit__(self, *_) -> None:
        if Context.CURRENT_CONTEXT is not self:
            raise RuntimeError("another context is active")  # pragma: no cover
        Context.CURRENT_CONTEXT = None

    def get_properties(self, cls) -> dict:
        """
        Get a modifiable dictionary of properties for the given class, e.g. a particular
        :cls:`Transform`.
        """
        if not isinstance(cls, type):
            raise ValueError(f"expected a type but got `{cls}`")  # pragma: no cover
        return self.properties.setdefault(cls, {})

    def match_artifacts(self, patterns: typing.Iterable[str], all: bool = False) \
            -> typing.Iterable["artifacts.Artifact"]:
        """
        Obtain all artifacts that match any of the patterns.

        Args:
            patterns: Sequence of patterns to match artifacts against.
            all: Whether to return all artifacts.

        Returns:
            matching: All matching artifacts.
        """
        if all:
            return self.artifacts.values()
        artifacts = [value for key, value in self.artifacts.items()
                     if any(re.match(pattern, key) for pattern in patterns)]
        if artifacts:
            LOGGER.debug("patterns matched %d artifacts", len(artifacts))
        else:
            LOGGER.warning("patterns did not match any artifacts")
        return artifacts

    def dump(self, filename: str) -> None:
        """
        Save all cached information.
        """
        cache = {
            "version": self.CACHE_VERSION,
            "artifact_metadata": {artifact.name: value for artifact, value in
                                  self.artifact_metadata.items()},
        }
        with open(filename, "w") as fp:
            json.dump(cache, fp, indent=4)

    def load(self, filename: str) -> None:
        """
        Load all cached information.
        """
        with open(filename) as fp:
            cache: dict = json.load(fp)

        if cache["version"] != self.CACHE_VERSION:  # pragma: no cover
            raise ValueError(f"expected cache version `{self.CACHE_VERSION}` but got "
                             f"`{cache['version']}`")

        self.artifact_metadata = {
            artifact: value for name, value in cache.get("artifact_metadata", {}).items() if
            (artifact := self.artifacts.get(name)) is not None
        }


DEFAULT_CONTEXT = Context()
STRICT_CONTEXT_MANAGEMENT = int(os.environ.get("BEAVER_STRICT_CONTEXT_MANAGEMENT", 0))


def get_current_context() -> Context:
    """
    Get the current context.

    Returns:
        context: The current context or a :code:`DEFAULT_CONTEXT` if no context is active.

    Raises:
        RuntimeError: If no context is active and :code:`STRICT_CONTEXT_MANAGEMENT` is enforced.
    """
    if Context.CURRENT_CONTEXT is None:
        if STRICT_CONTEXT_MANAGEMENT:
            raise RuntimeError("no context is active")
        else:
            return DEFAULT_CONTEXT  # pragma: no cover
    return Context.CURRENT_CONTEXT
