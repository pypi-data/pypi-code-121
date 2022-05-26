#!/usr/bin/env python
"""
Shows project filesystem usage of IT4I cluster storage systems
"""
import argparse
import getpass
import sys
import humanize

from tabulate import tabulate
from .logger import LOGGER
from .config import API_URL
from .config import IT4IFREETOKEN
from .config import CONFIG_FILES
from .jsonlib import jsondata

def naturalsize(value):
    """
    Return human readable data size or N/A
    """
    try:
        return humanize.naturalsize(value)
    except (ValueError, TypeError):
        return 'N/A'

def intcomma(value):
    """
    Return human integer or N/A
    """
    try:
        return humanize.intcomma(value)
    except (ValueError, TypeError):
        return 'N/A'


def main():
    """
    main function
    """

    parser = argparse.ArgumentParser(description="""
The command shows project filesystem usage of IT4I cluster storage systems""")
    parser.add_argument('-p', '--pid',
                        default='all',
                        action='store',
                        help="enter project pid")
    arguments = parser.parse_args()

    if IT4IFREETOKEN is None:
        LOGGER.error("""Missing or unset configuration option: %s
Suggested paths:
%s
""", "it4ifreetoken", CONFIG_FILES)
        sys.exit(1)

    username = getpass.getuser().strip()

    remote = ('%s/project-fs-usage' % (API_URL))
    data = {'login': username,
            'it4ifreetoken' : IT4IFREETOKEN,
            'pid': arguments.pid}
    jsonout = jsondata(remote, data)

    table_header = ['PID',
                    'File System',
                    'Space used',
                    'Space limit',
                    'Entries used',
                    'Entries limit',
                    'Last update']

    table_data = []
    for row in jsonout:
        table_data.append([row['pid'],
                           row['fs'],
                           naturalsize(row['usage_space']),
                           naturalsize(row['hard_quota_space']),
                           intcomma(row['usage_files']),
                           intcomma(row['hard_quota_files']),
                           row['updated_at']])

    if table_data:
        print tabulate(table_data, table_header)

if __name__ == "__main__":
    main()
