#!/usr/bin/env python
"""
Shows IT4I dedicated time
"""

import argparse
import sys

from tabulate import tabulate
from .config import API_URL
from .jsonlib import jsondata

def main():
    """
    main function
    """

    parser = argparse.ArgumentParser(description="""
The command shows IT4I dedicated time. By default all planned and active outages of all clusters \
are displayed. Return exit code 99 if there is no outage, otherwise return 0.""")
    parser.add_argument('-m', '--message',
                        default='planned',
                        action='store',
                        choices=['active', 'planned'],
                        help="select type of dedicated time. Planned contains also active")
    parser.add_argument('-c', '--cluster',
                        default='all',
                        action='store',
                        choices=['anselm', 'salomon', 'barbora'],
                        help="select cluster")
    arguments = parser.parse_args()

    remote = ('%s/dedicated-time/%s' % (API_URL, arguments.message))
    jsonout = jsondata(remote)

    table_header = ['Cluster',
                    'Start',
                    'End',
                    'Last update']
    table_data = []
    for row in jsonout:
        if arguments.cluster == row['cluster_type'] or arguments.cluster == 'all':
            table_data.append([row['cluster_type'],
                               row['dateefficiency'],
                               row['dateexpiration'],
                               row['updated_at']])
    if table_data:
        print tabulate(table_data, table_header)
    else:
        sys.exit(99)

if __name__ == "__main__":
    main()
