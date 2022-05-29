import argparse
import logging

from .webscrapers import mor
from . import renders


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="extraviadoscli",
        description="Use this web scraper to gather information about missing people "
        "from the official prosecutor's office websites of Mexico.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--format",
        help="In which format would you like to retrieve the data?",
        choices=["csv", "json"],
        default="json",
    )
    parser.add_argument(
        "--csv-no-headers",
        help="If you chosed csv as 'format', this option tells the program NOT to "
        "write the csv headers.",
        action="store_true",
    )
    parser.add_argument(
        "-o",
        "--outfile",
        help="Normally you can redirect the output of this program to a file using "
        "file redirection, but you can also specify a file to store the results.",
        type=str,
    )
    parser.add_argument(
        "--mode",
        choices=["wt", "at"],
        help="If you specified 'outfile', with this argument you can specify wether "
        "you want to replace the file ('wt') with the generated content or append the "
        "generated content to an existing file ('at'), this last option is specially "
        "useful when dealing with csv files.",
        type=str,
        default="wt",
    )
    subparsers = parser.add_subparsers(help="sub-command help", required=True)

    # SUB-COMMANDS FOR WEB SCRAPERS OF MORELOS
    # ========================================

    # Amber alerts
    mor_amber_parser = subparsers.add_parser(
        "mor-amber",
        help="Web scraper for Amber alerts of Morelos.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    mor.AmberAlertWebScraper.config_parser(mor_amber_parser)

    # Custom alerts
    mor_custom_parser = subparsers.add_parser(
        "mor-custom",
        help="Web scraper for custom alerts of Morelos.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    mor.CustomAlertWebScraper.config_parser(mor_custom_parser)
    return parser.parse_args()


def run():
    args = parse_args()
    mpps = args.func(args)
    logging.info("%s MPP(s) were extracted in total", len(mpps))
    renders.render_mpps(args, mpps)
    logging.info("done!")
