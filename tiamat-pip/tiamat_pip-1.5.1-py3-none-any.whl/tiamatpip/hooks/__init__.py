import logging
import pathlib

# Tell PyInstaller where to find hooks provided by this distribution;
# this is referenced by the :ref:`hook registration <hook_registration>`.
# This function returns a list containing only the path to this
# directory, which is the location of these hooks.

log = logging.getLogger(__name__)


def get_hook_dirs():
    """
    Return a list of paths to search for hooks.
    """
    return [str(pathlib.Path(__file__).parent)]
