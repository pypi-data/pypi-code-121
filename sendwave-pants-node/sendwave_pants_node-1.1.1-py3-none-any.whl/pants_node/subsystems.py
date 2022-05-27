"""Sendwave pants-node Options."""

from pants.engine.rules import SubsystemRule
from pants.option.subsystem import Subsystem


class NodeSubsystem(Subsystem):
    """Register plugin specific configuration options.

    These are used to control how the plugin will search for
    executables, including the npm binary that builds the project. It
    will also determine the PATH environment variable of the spawned
    npm/node processes. So, if your build script shells out to any
    other program on the machine (e.g.. 'sh') make sure that binaries
    location is included in the path.

    There are two options:
    - search_paths: a list of string (paths) where we will search for
        node binaries
    - use_nvm: Boolean, if True the plugin will add the value of NVM_BIN to the
        front of the search_path list
    """

    options_scope = "node"
    help = "Node Options."

    @classmethod
    def register_options(cls, register):
        """Register Sendwave pants-node options."""
        super().register_options(register)
        register(
            "--search-paths",
            type=list,
            member_type=str,
            default=["/bin", "/usr/bin/"],
            help="Directories in which to search for node binaries.'",
        )
        register(
            "--use-nvm",
            type=bool,
            default=True,
            help="If true, the value of $NVM_BIN will be "
            "appended to the front of the search path.",
        )


def rules():
    """Register the NodeSubsystem."""
    return [SubsystemRule(NodeSubsystem)]
