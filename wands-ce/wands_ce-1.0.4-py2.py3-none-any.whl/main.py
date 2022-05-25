# -*- coding: utf-8 -*-

"""
@author: onefeng
@time: 2022/5/23 9:09
"""
import argparse

from wands.server.manage import manage

if __name__ == '__main__':
    manage()
    __usage__ = "count the amount of lines and files under the current directory"
    parser = argparse.ArgumentParser(description=__usage__)

    parser.add_argument('-v', '--version', action='version',
                        version='1.0.1', help='Get version of Gerapy')

    parser.add_argument("-s", "--suffix", type=str,
                        help="count by suffix file name, format: .suffix1.suffix2... e.g: .cpp.py (without space)")
    parser.add_argument("-f", "--filter", type=str,
                        help="count without filter name, format: .suffix1.suffix2... e.g: .cpp.py (without space)")
    parser.add_argument("-d", "--detail", action="store_true",
                        help="show detail results")

    args = parser.parse_args()

    if args.filter:
        print('filter', args.filter)
    if args.suffix:
        print('suffix', args.suffix)

    if args.detail:
        print('detail', args.detail)
