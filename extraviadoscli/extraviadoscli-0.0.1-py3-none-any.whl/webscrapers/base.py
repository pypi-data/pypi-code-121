import abc
import argparse
import concurrent.futures
import logging
from typing import Any, Generator

import bs4

from .. import mpp


def humanize_pages(page_numbers: tuple[int, ...]) -> str:
    page_numbers_len = len(page_numbers)
    page_numbers_str = tuple(map(str, page_numbers))
    if page_numbers_len <= 15:
        return ", ".join(page_numbers_str)
    return ", ".join(page_numbers_str[:3]) + ", ..., " + ", ".join(page_numbers_str[-3:])


def humanize_page_range(page_from: int, page_to: int) -> str:
    return f"{page_from} -> {page_to}"


class PaginatedContentWebScraper(abc.ABC):

    @abc.abstractmethod
    def make_url(self, page_number: int) -> str:
        ...

    @abc.abstractmethod
    def extract_mpp_data_from_html(self, soup: bs4.BeautifulSoup) -> dict[str, Any]:
        ...

    @abc.abstractmethod
    def extract_mpps_in_html(self, page_url: str) -> list[bs4.BeautifulSoup]:
        ...

    def scrap_page(
        self,
        page_url: str,
    ) -> Generator[mpp.MissingPersonPoster, None, None]:
        try:
            for mpp_in_html in self.extract_mpps_in_html(page_url):
                try:
                    m = mpp.MissingPersonPoster(
                        **self.extract_mpp_data_from_html(mpp_in_html)
                    )
                except Exception as e:
                    logging.exception("unable to scrap 1 MPP from %s", page_url)
                    continue
                else:
                    yield m
        except Exception as e:
            logging.warning(
                "unable to scrap page %s due to an error: %s",
                page_url,
                str(e),
            )

    def scrap_mpps_by_pages(
        self,
        page_urls: list[str],
    ) -> list[mpp.MissingPersonPoster]:
        mpps = []
        for page_number, page_url in enumerate(page_urls):
            logging.info("scraping URL %s", page_url)
            mpps += [*self.scrap_page(page_url)]
            if (page_number + 1) % 5 == 0:
                logging.info("%s MPP(s) have been scraped in total", len(mpps))
        return mpps

    def scrap_mpps_until_find_po_post_url(
        self,
        post_url: str = "",
        max_pages=5,
    ) -> list[mpp.MissingPersonPoster]:
        mpps = []
        page_number = 1
        stop = False
        while not stop:
            if not page_number - 1 < max_pages:
                logging.info("max amount of pages (%s) has been scraped", max_pages)
                break
            page_url = self.make_url(page_number)
            logging.info("scraping URL %s", page_url)
            for mpp_ in self.scrap_page(page_url):
                mpps.append(mpp_)
                if mpp_.po_post_url == post_url:
                    logging.info("po_post_url %s has been found", post_url)
                    stop = True
                    break
            if page_number % 5 == 0:
                logging.info("%s MPP(s) have been scraped in total", len(mpps))
            page_number += 1
        return mpps

    def run(self, args: argparse.Namespace) -> list[mpp.MissingPersonPoster]:
        if args.approach == "pages":
            if args.pages:
                logging.info(
                    "extracting MPPs from pages %s",
                    humanize_pages(args.pages),
                )
                page_urls = [self.make_url(page_number) for page_number in args.pages]
            else:
                logging.info(
                    "extracting MPPs from pages %s",
                    humanize_page_range(args.page_from, args.page_to),
                )
                page_urls = [
                    self.make_url(page_number)
                    for page_number in range(args.page_from, args.page_to + 1)
                ]
            return self.scrap_mpps_by_pages(page_urls)
        elif args.approach == "search":
            if args.po_post_url:
                logging.info(
                    "extracting MPPs until find URL %s or until %s page(s) have been "
                    "scraped",
                    args.po_post_url,
                    args.max_pages,
                )
            else:
                logging.info(
                    "extracting MPPs until %s page(s) have been scraped (no URL to "
                    "search was specified)",
                    args.max_pages,
                )
            return self.scrap_mpps_until_find_po_post_url(
                args.po_post_url,
                args.max_pages,
            )

    @classmethod
    def config_parser(cls, parser: argparse.ArgumentParser):
        parser.add_argument(
            "-a",
            "--approach",
            choices=["search", "pages"],
            help="What will be the approach the web scraper will take to extract MPPs? If "
            "you choose 'pages' you will need to specify --pages or --page-from and "
            "--page-to, if you choose 'search' you will need to specify --po-post-url and "
            "--max-mpps.",
            default="search",
        )
        parser.add_argument(
            "--po-post-url",
            help="The web scraper will stop until it finds the link provided in this "
            "argument, this link must refer to the missing person post URL in the "
            "prosecutor's office website.",
            type=str,
            default="",
        )
        parser.add_argument(
            "--max-pages",
            help="In case the web scraper cannot find the link provided in --po-post-url "
            "argument because the link was removed or by any other reason, the web scraper "
            "will stop until it retrieves a --max-pages amount of pages in the website.",
            type=int,
            default=5,
        )
        parser.add_argument(
            "--page-from",
            help="The first page number to extract MPPs.",
            type=int,
            default=1,
        )
        parser.add_argument(
            "--page-to",
            help="The last page number to extract MPPs (must be greater than --page-from).",
            type=int,
            default=10,
        )
        parser.add_argument(
            "--pages",
            help="A list with the page numbers you want to extract MPPs from. If you use "
            "--pages, --page-from and --page-to will be ignored.",
            nargs="+",
            type=int,
        )
        parser.set_defaults(func=cls().run)
