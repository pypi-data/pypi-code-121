"""Console script for ebooks-lister."""
import argparse
import csv
import logging
import sys

from ebooks_lister.ebooks_lister import EbookLister


def main():
    """Parses arguments and iterates a generator. Can print details or send them to a csv outfile"""
    logging.info("started up the main() function")
    parser = argparse.ArgumentParser(description="Get normalized metadata from paths with ebooks")
    parser.add_argument(
        '--path', '--paths', help="path or paths to directories of ebooks", action='extend', nargs='+', dest='paths'
    )
    parser.add_argument('--fields', help="a list of fields to extract from ebook metadata", action='extend', nargs='+')
    parser.add_argument('--outfile', help="path to write a csv file to.")

    args = parser.parse_args()
    if args.paths and args.fields:
        lister = EbookLister(args.paths, args.fields)
        details = lister.get_ebooks_generator()
        if args.outfile:
            with open(args.outfile, 'w', newline='') as fout:
                csv_writer = csv.writer(fout)
                csv_writer.writerow(['path'] + args.fields)
                for detail in details:
                    csv_writer.writerow([str(detail[field]) for field in (['path'] + args.fields)])
        else:
            print(','.join(['path'] + args.fields))
            for detail in details:
                try:
                    print(','.join((str(detail[field]) for field in (['path'] + args.fields))))
                except KeyError as e:
                    logging.error(e)
                    logging.error(f"{detail=}")
                    raise e
            # print(detail)
    else:
        parser.print_help()
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
