import argparse
import sys

from osgeonorge.geonorge import atom_url, list_feeds

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--url', type=str, dest="url", default=atom_url, help='URL to list with ATOM feeds')
    args = parser.parse_args()

    list_feeds(args.url)


if __name__ == '__main__':
    main()
