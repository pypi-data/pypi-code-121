"""The type of dependency (prod/dev/peer)."""
from enum import Enum


class DependencyType(Enum):
    """The type of dependency (prod/dev/peer)."""

    DEV = "dev"
    PEER = "peer"
    PROD = "prod"
