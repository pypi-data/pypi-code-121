from pathlib import Path

from enot_lite.utils.initializer import init

try:
    # Importing onnx after torch leads to crash.
    # To avoid crash we must try to load onnx before.
    import onnx
except ImportError:
    pass

try:
    # Importing torch after ORT ld_preload leads to crash.
    # To avoid crash we must try to load torch before.
    import torch
except ImportError:
    pass

init()


# ENOT-Lite data dirs.
_ENOT_LITE_WORK_DIR = Path.home() / '.enot-lite'
_ENOT_LITE_CACHE_DIR = _ENOT_LITE_WORK_DIR / Path('cache')
_ENOT_LITE_LOG_DIR = _ENOT_LITE_WORK_DIR / Path('log')

# Create ENOT-Lite data dirs.
_ENOT_LITE_WORK_DIR.mkdir(parents=True, exist_ok=True)
_ENOT_LITE_CACHE_DIR.mkdir(parents=True, exist_ok=True)
_ENOT_LITE_LOG_DIR.mkdir(parents=True, exist_ok=True)


# Import backend module automatically.
import enot_lite.backend


def _get_version() -> str:
    with Path(__file__).parent.joinpath('VERSION').open('r') as version_file:
        version = version_file.read().strip()

    return version


__version__ = _get_version()
