from dataclasses import dataclass

@dataclass
class LifetimeScopeOptions:
    """Holds options for a lifetime scope."""

    suppress_captive_dependency_warnings: bool = False
    """Gets or sets whether to suppress warning logs about captive dependencies."""

    raise_on_captive_dependency: bool = True
    """Gets or sets whether to raise an exception when a captive dependency is detected."""
