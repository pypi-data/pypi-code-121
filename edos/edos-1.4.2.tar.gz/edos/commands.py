import logging

from edos.cli.do.cluster import cluster
from edos.cli.do.database import database
from edos.cli.do.spaces import spaces
from edos.cli.docker import docker

LOG = logging.getLogger(__name__)


def register_commands(group):
    group.add_command(cluster)
    group.add_command(database)
    group.add_command(spaces)
    group.add_command(docker)
