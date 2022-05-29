import logging
from typing import Any

import bs4

from ... import mpp
from .. import base, utils
from . import commons


class AmberAlertWebScraper(base.PaginatedContentWebScraper):

    BASE_URL = "https://fiscaliamorelos.gob.mx/category/alerta-amber/page"

    def make_url(self, page_number: int) -> str:
        return f"{self.BASE_URL}/{page_number}/"

    def extract_po_poster_url(self, po_post_url: str) -> str:
        try:
            soup = utils.retrieve_soup_from(po_post_url)
            div = soup.find("div", class_="post-thumb-img-content")
            return div.img.get("src", "").strip()
        except Exception:
            logging.info("unable to get the po_poster_url from %s", po_post_url)
            return ""

    def extract_mpp_data_from_html(self, soup: bs4.BeautifulSoup) -> dict[str, Any]:
        mpp_data = {}
        try:
            mpp_data["mp_name"] = soup.h2.get_text().strip().title()
        except AttributeError as e:
            logging.exception("unable to get the mp_name from the article: %s", soup)
            raise e

        try:
            mpp_data["po_post_url"] = soup.a.get("href", "").strip()
        except AttributeError as e:
            logging.exception("unable to get the po_post_url from the article: %s", soup)
            raise e

        try:
            datestr = soup.find("span", class_="published").get_text().strip()
            mpp_data["po_post_publication_date"] = commons.parsedate(datestr)
        except (AttributeError, ValueError) as e:
            logging.exception(
                "unable to get the po_post_publication_date from the article: %s",
                soup,
            )
            mpp_data["po_post_publication_date"] = ""

        try:
            mpp_data["po_poster_url"] = self.extract_po_poster_url(mpp_data["po_post_url"])
        except Exception as e:
            logging.exception(
                "unable to get the po_poster_url from the article: %s",
                soup,
            )
            mpp_data["po_poster_url"] = ""

        mpp_data["alert_type"] = mpp.AlertTypeChoices.AMBER.value
        mpp_data["po_state"] = mpp.StateChoices.MORELOS.value
        return mpp_data

    def extract_mpps_in_html(self, page_url: str) -> list[bs4.BeautifulSoup]:
        soup = utils.retrieve_soup_from(page_url)
        return soup.find_all("article")


class CustomAlertWebScraper(base.PaginatedContentWebScraper):

    BASE_URL = "https://fiscaliamorelos.gob.mx/cedulas"

    def make_url(self, page_number: int) -> str:
        return f"{self.BASE_URL}/{page_number}/"

    def extract_mpp_data_from_html(self, soup: bs4.BeautifulSoup) -> dict[str, Any]:
        mpp_data = {}
        try:
            mpp_data["mp_name"] = soup.h3.a.get_text().strip().title()
        except Exception as e:
            logging.exception("unable to get the mp_name from the article: %s", soup)
            raise e

        try:
            mpp_data["po_post_url"] = soup.h3.a.get("href", "").strip()
        except Exception as e:
            logging.exception("unable to get the po_post_url from the article: %s", soup)
            raise e

        try:
            datestr = soup.span.get_text().strip()
            mpp_data["po_post_publication_date"] = commons.parsedate(datestr)
        except Exception as e:
            logging.exception(
                "unable to get the po_post_publication_date from the article: %s",
                soup,
            )
            mpp_data["po_post_publication_date"] = ""

        try:
            mpp_data["po_poster_url"] = soup.img.get("src", "").strip()
            mpp_data["po_poster_url"] = mpp_data["po_poster_url"].replace("-300x225", "")
        except Exception as e:
            logging.exception(
                "unable to get the po_poster_url from the article: %s",
                soup,
            )
            mpp_data["po_poster_url"] = ""

        mpp_data["alert_type"] = mpp.AlertTypeChoices.OTHER.value
        mpp_data["po_state"] = mpp.StateChoices.MORELOS.value
        return mpp_data

    def extract_mpps_in_html(self, page_url: str) -> list[bs4.BeautifulSoup]:
        soup = utils.retrieve_soup_from(page_url)
        return soup.find_all("article")
