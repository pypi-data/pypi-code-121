# -*- coding: utf-8 -*-

"""
@author: onefeng
@time: 2022/5/23 15:39
"""
import argparse

parser = argparse.ArgumentParser(description="")

parser.add_argument('-f', '--filter', help='Get version of Gerapy')


def cmd():
    args = parser.parse_args()
    if args.filter:
        print('filter', args.filter)
    else:
        from wands.server.manage import manage
        manage()


if __name__ == '__main__':
    cmd()
