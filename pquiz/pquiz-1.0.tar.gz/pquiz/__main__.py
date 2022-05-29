# Gianluca Caronte 2019-2022(C)
from enum import Enum
import argparse
import sys

from termcolor import colored
from .pquiz import test_port, MAX_PORT




class PrintMode(Enum):
    pretty = 0
    printable = 1
    def __str__(self):
        return self.value


def get_parser():
    PORTS = [p for p in range(1,MAX_PORT+1) if p not in [22,25]]
    parser = argparse.ArgumentParser(prog='pquiz',description=
    """
    A simple utility to check what ports are available for outgoing tcp
    connection (ports 22 and 25 are not testable).

    Gianluca Caronte 2019-2022 (c)
    """)

    parser.add_argument('-b','--range-begin', type=int,
                        metavar=f'[1-{MAX_PORT}]',
                        choices=PORTS,
                        help='the begin of the ports range')

    parser.add_argument('-e','--range-end', type=int,
                        metavar=f'[1-{MAX_PORT}]',
                        choices=PORTS,
                        help='the end of the ports range')

    parser.add_argument('--all', action='store_true',
                        help='test all the ports')

    parser.add_argument('-p','--port', type=int,  nargs='+',
                        choices=PORTS,
                        metavar='PORT',
                        required=
                            (not '--range-begin' in sys.argv) and (not '--range-end' in sys.argv)  and (not '--all' in sys.argv)
                            and (not '-b' in sys.argv) and (not '-e' in sys.argv)  and (not '-a' in sys.argv),
                        help='the port(s) to test')

    parser.add_argument('-m','--print-mode', type=str.lower, choices=['pretty', 'printable'], default='pretty')
    parser.add_argument('-t','--timeout', type=float, default=5,help='timeout in seconds')

    #parser.add_argument('-',  help='read ports from stding', dest='read_stdin', type=bool)

    return parser


def print_res(port,ok, mode='pretty'):
    if mode=='pretty':
        print(f"{port}\t{colored('OK','green') if ok else colored('KO','red')}")
    elif mode=='printable' and ok:
        print(port)


if __name__ == "__main__":
    args = get_parser().parse_args()

    b = args.range_begin
    e = args.range_end

    if (b != None or e != None) and not args.all:
        if b == None: b = 1
        if e == None: e = MAX_PORT
        args.port = range(b,e+1)
    if args.all:
        args.port = range(1,MAX_PORT+1)

    for p in args.port:
        if p in [22,25]:
            continue
        print_res(p, test_port(p, args.timeout), args.print_mode)