"""
Splits the video into frames stored as png files.
"""

import argparse
import sys


def parse_args(args):
    """ Command line parser. """
    parser = argparse.ArgumentParser(description="Capture video from camera to mp4 file.")
    parser.add_argument('--index', '-i', default=0, type=int, help="Camera index on this mc.")
    parser.add_argument('--time', '-t', default=4, type=int, help='Seconds to capture the video')
    parser.add_argument('outfile', type=str, help="Output mp4 file to store the video.")
    opt = parser.parse_args(args)

    if len(args) == 1:
        parser.print_help(sys.stderr)
        sys.exit(-1)

    return opt


def main():
    """ Main program. """
    opt = parse_args(sys.argv)


if __name__ == "__main__":
    main()