#!/usr/bin/env python
"""
Show some basic information from IT4I PBS accounting
"""
import argparse
import getpass
import sys
import pycent

from tabulate import tabulate
from .logger import LOGGER
from .config import API_URL
from .config import IT4IFREETOKEN
from .config import CONFIG_FILES
from .jsonlib import jsondata

TABLE_ME_TITLE = 'Projects I am participating in'
TABLE_ME_AS_PI_TITLE = 'Projects I am Primarily Investigating'
TABLE_LEGENDS_TITLE = 'Legend'

def ifpercent(part, whole, percent):
    """
    Return percent if required and it is possible, otherwise return origin number
    """
    if percent:
        try:
            return pycent.percentage(part, whole)
        except ZeroDivisionError:
            return 0
            # sys.exit()
    else:
        return part

def user_header(arguments):
    """ Return user header """
    header = ['PID', 'Resource type', 'Days left']
    if not arguments.percent:
        header.append('Total')
        header.append('Used')
        header.append('By me')
        header.append('Free')
    else:
        header.append('Total %')
        header.append('Used %')
        header.append('By me %')
        header.append('Free %')
    return header

def pi_header(arguments):
    """ Return pi header """
    header = ['PID', 'Resource type', 'Login']
    if not arguments.percent:
        header.append('Usage')
        header.append('Free')
    else:
        header.append('Usage %')
        header.append('Free %')
    return header

def user_row(row, row_previous, arguments):
    """ Return user row """
    table_row = []
    if row['pid'] == row_previous['pid']:
        table_row.append('')
    else:
        table_row.append(row['pid'])
    for key in ['resource_type', 'days_left']:
        table_row.append(row[key])
    if not arguments.percent:
        for key in ['total', 'used', 'by_me', 'free']:
            table_row.append(row[key])
    else:
        try:
            table_row.append(ifpercent(row['total'], row['total'], arguments.percent))
            table_row.append(ifpercent(row['used'], row['total'], arguments.percent))
            table_row.append(ifpercent(row['by_me'], row['total'], arguments.percent))
            table_row.append(100-ifpercent(row['used'], row['total'], arguments.percent))
        except ZeroDivisionError:
            return None
    return table_row

def pi_row(row, arguments, row_previous):
    """ Return pi row """
    # total = [project['total'] for project in jsonout['me'] if project['pid'] == row['pid']][0]
    table_row = []
    table_row.append(row['pid'] if row['pid'] != row_previous['pid'] else '')
    table_row.append(row['resource_type'])
    table_row.append(row['login'])
    if not arguments.percent:
        table_row.append(row['usage'])
        # table_row.append(row['free'])
    else:
        try:
            table_row.append(ifpercent(row['usage'], row['total'], arguments.percent))
            # table_row.append(ifpercent(row['free'], row['total'], arguments.percent))
        except ZeroDivisionError:
            return None
    return table_row

def main():
    """
    main function
    """
#pylint: disable = consider-using-f-string
    parser = argparse.ArgumentParser(description="""
The command shows some basic information from IT4I PBS accounting. The
data is related to the current user and to all projects in which user
participates.""",
                                     epilog="""
Columns of "%s":
         PID: Project ID/account string.
Resource type: Kind of resource eg. Barbora CPU, Karolina GPU,...
   Days left: Days till the given project expires.
       Total: Node hours allocated to the given project.
        Used: Sum of node-hours used by all project members.
        Free: Node-hours that haven't yet been utilized.

Columns of "%s" (if present):
         PID: Project ID/account string.
Resource type: Kind of resource eg. Barbora CPU, Karolina GPU,...
       Login: Project member's login name.
        Used: Project member's used node-hours.
""" % (TABLE_ME_TITLE, TABLE_ME_AS_PI_TITLE),
                                     formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-p', '--percent', action='store_true',
                        help="""show values in percentage. Projects with unlimited resources are not displayed""")
    # parser.add_argument('-u', '--unit', action='store', help='unit', default='real',
    #                     choices=['perc', 'real', 'both'])
    parser.add_argument('-a', '--all', action='store_true',
                        help="""Show all resources include inactive and future ones.""")
    arguments = parser.parse_args()

    if IT4IFREETOKEN is None:
        LOGGER.error("""Missing or unset configuration option: %s
Suggested paths:
%s
""", "it4ifreetoken", CONFIG_FILES)
        sys.exit(1)

    username = getpass.getuser().strip()
    # username = 'kvi0029'

    if arguments.all != False:
        jsonout = jsondata(('%s/it4ifree/%s' % (API_URL, username)), {'it4ifreetoken': IT4IFREETOKEN, 'all': 'yes'})
    else:
        jsonout = jsondata(('%s/it4ifree/%s' % (API_URL, username)), {'it4ifreetoken': IT4IFREETOKEN})

    table_me_headers = user_header(arguments)
    table_me = []
    row_previous = {'pid': ''}
    for row in jsonout['me']:
        table_row = user_row(row, row_previous, arguments)
        if table_row:
            table_me.append(table_row)
        row_previous = {'pid': row['pid']}

    table_me_as_pi_headers = pi_header(arguments)
    table_me_as_pi = []
    row_previous = {'pid': '', 'resource_type': '', 'usage': ''}
    for row in jsonout['me_as_pi']:
        table_row = pi_row(row, arguments, row_previous)
        if table_row:
            table_me_as_pi.append(table_row)
        row_previous = {'pid': row['pid'],
                        'resource_type': row['resource_type'],
                        'usage': row['usage']}
    # pylint: disable = expression-not-assigned
    if table_me:
        print >> sys.stdout, '\n{}\n{}' .format(TABLE_ME_TITLE,
                                                len(TABLE_ME_TITLE) * '=')

        print (tabulate(table_me, table_me_headers, floatfmt="8.0f"))

    if table_me_as_pi:
        print >> sys.stdout, '\n{}\n{}' .format(TABLE_ME_AS_PI_TITLE,
                                                len(TABLE_ME_AS_PI_TITLE) * '=')

        print (tabulate(table_me_as_pi, table_me_as_pi_headers, floatfmt="8.0f"))

    print >> sys.stdout, '\n{}\n{}' .format(TABLE_LEGENDS_TITLE,
                                            len(TABLE_LEGENDS_TITLE) * '=')
    print ('N/A   =    No one used this resource yet')
    print ('Legacy Normalized core hours are in NCH')
    print ('Everything else is in Node Hours')

if __name__ == "__main__":
    main()
