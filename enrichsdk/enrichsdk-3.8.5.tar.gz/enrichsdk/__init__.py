"""
This developer kit is meant for advanced users of the `Scribble Enrich Feature Store`. 
This includes command line scripts to create and manage Enrich modules and APIs to 
write new modules on the platform::
  
      ______           _      __       _____ ____  __ __
     / ____/___  _____(_)____/ /_     / ___// __ \\/ //_/
    / __/ / __ \\/ ___/ / ___/ __ \\    \\__ \\/ / / / ,<   
   / /___/ / / / /  / / /__/ / / /   ___/ / /_/ / /| |  
  /_____/_/ /_/_/  /_/\\___/_/ /_/   /____/_____/_/ |_|  
  
"""
import os

VERSION = "3.8.5"


def _get_git_revision(path):
    revision_file = os.path.join(path, "refs", "heads", "master")
    if os.path.exists(revision_file):
        with open(revision_file) as fh:
            return fh.read().strip()[:7]


def get_revision():
    """
    :returns: Revision number of this branch/checkout, if available. None if
        no revision number can be determined.
    """
    package_dir = os.path.dirname(__file__)
    checkout_dir = os.path.normpath(os.path.join(package_dir, os.pardir))
    path = os.path.join(checkout_dir, ".git")
    if os.path.exists(path):
        return _get_git_revision(path)


def get_version():
    base = VERSION
    if __build__:
        base = "%s (%s)" % (base, __build__)
    return base


__build__ = get_revision()
__version__ = VERSION

from .core import *
from .package import *
from .lib import *
from .commands import *
from .tasks import *
from .services import *
from .datasets import *
from .quality import *
from . import featurestore, realtime, contrib, utils, notebook, feature_compute
