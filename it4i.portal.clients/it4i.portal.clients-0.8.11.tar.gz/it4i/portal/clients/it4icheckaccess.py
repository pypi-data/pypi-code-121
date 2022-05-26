#!/usr/bin/env python
"""
Show if IT4I account and/or related project has the access to specified cluster and queue.
"""

import argparse
import sys

from .logger import LOGGER
from .config import API_URL
from .jsonlib import jsondata

def main():
    """
    main function
    """

    parser = argparse.ArgumentParser(description="""
The command shows if an IT4I account and/or related project has the access to specified cluster and queue. \
Return exit code 99 if access is not granted.
""")
    parser.add_argument('-l', '--login',
                        required=True,
                        action='store',
                        help="user login")
    parser.add_argument('-c', '--cluster',
                        required=True,
                        action='store',
                        help="cluster name")
    parser.add_argument('-q', '--queue',
                        required=True,
                        action='store',
                        help="queue")
    parser.add_argument('-p', '--project',
                        default=None,
                        action='store',
                        help="project id, not required if querying projectless queue")
    arguments = parser.parse_args()

    if arguments.project is None and arguments.queue != 'qexp':
        LOGGER.error("Project id is required.")
        sys.exit(1)

    remote = ('%s/check-access' % (API_URL))
    data = {'login' : arguments.login,
            'queue': arguments.queue,
            'cluster': arguments.cluster}
    if arguments.project is not None:
        data['pid'] = arguments.project
    jsonout = jsondata(remote, data)

    print jsonout
    if jsonout in ['OK Access granted for projectless queue.',
                   'OK Access granted for out-of-resources queue.',
                   'OK Access granted for regular queue.']:
        sys.exit(0)
    else:
        sys.exit(99)

if __name__ == "__main__":
    main()
