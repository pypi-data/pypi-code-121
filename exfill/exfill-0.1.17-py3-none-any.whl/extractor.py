"""exfill will scrape LinkedIn job postings, parse out details about
each posting, then combine all of the information into a single useable
csv file.
"""
import logging
import os
from argparse import ArgumentParser
from configparser import ConfigParser, ExtendedInterpolation

from parsers.parser_factory import ParserFactory
from scrapers.factory import ScraperFactory


class ConfigFileMissing(Exception):
    pass


def init_parser() -> dict:
    """Initialize argument parser."""
    parser = ArgumentParser()
    parser.add_argument("site", choices=["linkedin"], help="Site to scrape")
    parser.add_argument(
        "action", choices=["scrape", "parse"], help="Action to perform"
    )
    return vars(parser.parse_args())


def load_config() -> ConfigParser:
    """Load config file"""

    config_file = os.path.dirname(__file__) + "/config.ini"
    if not os.path.exists(config_file):
        raise ConfigFileMissing("Default config.ini is missing")

    config = ConfigParser(interpolation=ExtendedInterpolation())
    config.read(config_file)

    return config


def create_dirs(config: ConfigParser) -> None:
    """Create directories referenced in the config file"""
    # for item in config['Directories']:
    for dir_path in config.items("Directories"):
        if not os.path.exists(dir_path[1]):
            os.mkdir(dir_path[1])


def main() -> None:
    """Main controller function used to call child functions/modules."""
    # Load config
    config = load_config()

    create_dirs(config)

    # Initialize logging
    log_file_name = config.get("Paths", "app_log")
    logging.basicConfig(
        filename=log_file_name,
        level=logging.INFO,  # level=logging.INFO should be default
        format="[%(asctime)s] [%(levelname)s] - %(message)s",
        filemode="w+",
    )

    args = init_parser()
    logging.info(f"Starting app with the following input args: {args}")

    if args.get("action") == "scrape":
        scraper = ScraperFactory.create("linkedin", config)
        scraper.scrape_postings(48)

    if args.get("action") == "parse":
        parser = ParserFactory.create("linkedin", config)
        parser.parse_postings()

    logging.info("Finished execution.  Exiting application.")


if __name__ == "__main__":

    main()
