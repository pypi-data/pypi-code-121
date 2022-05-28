#!/usr/bin/python3

"""Main function wrapper"""

from .cli import parse_args
from .scan import scan_wrapper
from .concerts import bit
from .output import output_wrapper


def main():
    """Main function."""
    args = parse_args()
    artist_list = scan_wrapper(args.directory, args.cache_dir)
    concert_list = bit(artist_list, args)
    output_wrapper(concert_list, args.output)


if __name__ == "__main__":
    main()
