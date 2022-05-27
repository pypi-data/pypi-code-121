"""Dealing with interactions with configuration and environment variables."""
from functools import lru_cache
import logging
import os
from pathlib import Path
from typing import Callable, Dict, Final, List, Optional, Tuple

import GPUtil

__all__: List[str] = [
    "BITFOUNT_ENGINE",
    "BITFOUNT_KEY_STORE",
    "BITFOUNT_LOGS_DIR",
    "BITFOUNT_STORAGE_PATH",
    "get_gpu_metadata",
]

logger = logging.getLogger(__name__)

BITFOUNT_STORAGE_PATH: Path = Path.home() / ".bitfount"
BITFOUNT_KEY_STORE: Path = BITFOUNT_STORAGE_PATH / "known_workers.yml"
BITFOUNT_LOGS_DIR = Path("bitfount_logs")

_PRODUCTION_ENVIRONMENT: Final[str] = "production"
_STAGING_ENVIRONMENT: Final[str] = "staging"
_DEVELOPMENT_ENVIRONMENT: Final[str] = "dev"
_ENVIRONMENT_CANDIDATES: Tuple[str, ...] = (
    _PRODUCTION_ENVIRONMENT,
    _STAGING_ENVIRONMENT,
    _DEVELOPMENT_ENVIRONMENT,
)


@lru_cache(maxsize=1)
def _get_environment() -> str:
    """Returns bitfount environment to be used from BITFOUNT_ENVIRONMENT variable.

    The result is cached to avoid multiple warning messages. This means that changes to
    the `BITFOUNT_ENVIRONMENT` environment variable will not be detected whilst the
    library is running.

    Returns:
        str: PRODUCTION_ENVIRONMENT, STAGING_ENVIRONMENT or DEVELOPMENT_ENVIRONMENT

    """
    BITFOUNT_ENVIRONMENT = os.environ.get(
        "BITFOUNT_ENVIRONMENT", _PRODUCTION_ENVIRONMENT
    )
    if BITFOUNT_ENVIRONMENT not in _ENVIRONMENT_CANDIDATES:
        raise ValueError(
            f"The environment specified by the environment variable "
            f"BITFOUNT_ENVIRONMENT ({BITFOUNT_ENVIRONMENT}) is not in the supported "
            f"list of environments ({_ENVIRONMENT_CANDIDATES})"
        )
    if BITFOUNT_ENVIRONMENT == _STAGING_ENVIRONMENT:
        logger.warning(
            "Using the staging environment. "
            + "This will only work for Bitfount employees."
        )
    if BITFOUNT_ENVIRONMENT == _DEVELOPMENT_ENVIRONMENT:
        logger.warning(
            "Using the development environment. "
            + "This will only work if you have all Bitfount services running locally."
        )

    return BITFOUNT_ENVIRONMENT


_PYTORCH_ENGINE: Final[str] = "pytorch"
_BASIC_ENGINE: Final[str] = "basic"
_ENGINE_CANDIDATES: Tuple[str, ...] = (
    _BASIC_ENGINE,
    _PYTORCH_ENGINE,
)

# Set BITFOUNT_ENGINE, defaulting to PYTORCH_ENGINE or BASIC_ENGINE
# Start with BASIC_ENGINE as default
BITFOUNT_ENGINE: str = _BASIC_ENGINE
try:
    # Use the type specified by envvar if present
    BITFOUNT_ENGINE = os.environ["BITFOUNT_ENGINE"]
    # Check that the engine option is a valid one
    if BITFOUNT_ENGINE not in _ENGINE_CANDIDATES:
        raise ValueError(
            f"The backend engine specified by the environment variable "
            f"BITFOUNT_ENGINE ({BITFOUNT_ENGINE}) is not in the supported list of "
            f"backends ({_ENGINE_CANDIDATES})"
        )
except KeyError:
    # Otherwise, if PyTorch is installed use PYTORCH_ENGINE
    try:
        import torch  # noqa: F401

        BITFOUNT_ENGINE = _PYTORCH_ENGINE
    except ImportError:
        pass


def _get_gpu_metadata_gputil() -> Tuple[Optional[str], int]:
    """Returns gpu metadata from GPUtil.

    Uses the name of the first GPU thereby assuming that there is only 1 type of GPU
    attached to the machine.

    Returns:
        Tuple[Optional[str], int]: name of gpu and how many there are
    """
    gpus = GPUtil.getGPUs()
    if gpus:
        return gpus[0].name, len(gpus)
    # nvidia-smi installed, but no GPU available
    return None, 0


def _get_gpu_metadata_pytorch() -> Tuple[Optional[str], int]:
    """Return gpu metadata from pytorch.

    Returns:
        Tuple[Optional[str], int]: name of gpu and how many there are
    """
    import torch.cuda as cuda

    if cuda.is_available():
        # Devices without CUDA can still use pytorch,
        # but this will throw an exception
        return cuda.get_device_name(), cuda.device_count()
    else:
        raise Exception("CUDA not available.")


_GPU_COUNT_FUNCTION_LOOKUP: Dict[str, Callable[..., Tuple[Optional[str], int]]] = {
    _BASIC_ENGINE: _get_gpu_metadata_gputil,
    _PYTORCH_ENGINE: _get_gpu_metadata_pytorch,
}


def get_gpu_metadata() -> Tuple[Optional[str], int]:
    """Retrieve details about GPUs if available.

    Uses tools available in the appropriate backend,
    to find GPUs that are usable by the backend.

    Returns: a tuple of GPU name and count.
    """
    # noinspection PyBroadException
    try:
        return _GPU_COUNT_FUNCTION_LOOKUP[BITFOUNT_ENGINE]()
    except Exception as ex:
        # Broad exception handling here as libraries may throw various exceptions
        # But if anything is raised we can assume we don't have GPU access
        logger.warning(f"Encountered exception whilst gathering GPU information: {ex}")
        logger.warning("No GPU info will be used.")
        return None, 0
