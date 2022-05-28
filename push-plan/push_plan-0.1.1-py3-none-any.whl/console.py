# Application to archive and push finger status

from types import SimpleNamespace as SNS
from . import dirs
from .dprint import dprint
from . import record
from . import publish
from . import config as cfg


def run():
    # Main configurtion variable
    config = SNS()
    # Process command line parameters
    cfg.cmd_params(config)
    # Read configuration file
    cfg.read_config(config)
    # Check presence of work files and read them
    dirs.read_workfiles(config)
    # Read current plan/project if available
    dirs.read_current(config)
    # Prepare index directory for archival
    dirs.create_index(config)
    # Get filenames for recording
    dirs.name_record(config)
    # Save both files
    record.archive_link(config, 'plan')
    record.archive_link(config, 'project')
    # Publish files
    publish.publish(config)

    if config.options.debug:
        dprint(config)

