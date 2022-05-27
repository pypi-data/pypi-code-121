import os
import sys

if sys.version_info < (3, 8):
    raise SystemExit(
        "ERROR: Ansible requires Python 3.8 or newer on the controller. "
        f"Current version: {''.join(sys.version.splitlines())}"
    )

if not os.getenv('TROPS_DIR'):
    raise SystemExit('ERROR: TROPS_DIR has not been set')

# Check if TROPS_DIR is an existing directory
if not os.path.isdir(os.path.expanduser(os.path.expandvars(os.getenv('TROPS_DIR')))):
    raise SystemExit(
        "ERROR: TROPS_DIR is not an existing directory. "
        f"Current TROPS_DIR: {os.getenv('TROPS_DIR')}")
