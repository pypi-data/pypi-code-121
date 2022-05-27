"""Model parameter aggregators for Federated Averaging."""
import importlib
import pkgutil

from bitfount.federated.logging import _get_federated_logger

_logger = _get_federated_logger(__name__)


def _log_import_error(pkg: str) -> None:
    _logger.error(f"Issue importing {pkg}")


# Find and import all modules in this package. This ensures that the subclasses are
# all registered against their BaseAggregator(s).
for module in pkgutil.walk_packages(
    path=__path__,
    prefix=__name__ + ".",
    onerror=_log_import_error,
):
    _logger.debug(f"Importing {module.name} within {__name__}")
    importlib.import_module(module.name)
