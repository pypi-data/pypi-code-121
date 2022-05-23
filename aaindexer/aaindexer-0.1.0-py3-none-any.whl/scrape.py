"""
The code for downloading the aaindex and applying the parser to it
"""
import requests
from rich.console import Console
from rich.progress import Progress

from aaindexer.models import AaindexRecord
from aaindexer.parser import aaindex_file

BASE_URL = "https://www.genome.jp/ftp/db/community/aaindex/aaindex"


def scrape_database(index: int) -> str:
    """
    Scrapes an aaindex database, and returns it as plain text

    :param index: The number of the database to return (1-3)
    :return: The aaindex database contents
    """
    return requests.get(BASE_URL + str(index)).text


def scrape_parse(index: int, progress=False) -> list[AaindexRecord]:
    """
    Scrapes an aaindex database and parses the result

    :param index: The number of the database to return (1-3)
    :param progress: If true, show progress
    """
    cols = Progress.get_default_columns()[:-2]
    with Progress(*cols, disable=not progress,
                  console=Console(stderr=True)) as progress:
        request_task = progress.add_task("Requesting Database", total=None)
        data = scrape_database(index)
        progress.update(request_task, total=1, completed=1)

        parse_task = progress.add_task("Parsing Database", total=None)
        parsed = aaindex_file.parse_string(data)
        progress.update(parse_task, total=1, completed=1)

        return list(parsed)
