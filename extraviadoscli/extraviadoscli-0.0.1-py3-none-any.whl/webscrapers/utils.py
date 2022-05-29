import logging

import bs4
import requests


def retrieve_soup_from(page_url: str) -> bs4.BeautifulSoup:
    try:
        response = requests.get(page_url)
        response.raise_for_status()
    except requests.ConnectionError as e:
        logging.error(
            "unable to retrieve the content from %s due to connection error: %s",
            page_url,
            str(e),
        )
        raise e from e
    except requests.HTTPError as e:
        logging.error(
            "unable to retrieve the content from %s due to HTTP error: %s",
            page_url,
            str(e),
        )
        raise e from e
    except requests.Timeout as e:
        logging.error(
            "unable to retrieve the content from %s due to time out: %s",
            page_url,
            str(e),
        )
        raise e from e
    except requests.RequestException as e:
        logging.error(
            "unable to retrieve the content from %s due to an error: %s",
            page_url,
            str(e)
        )
        raise e from e
    except Exception as e:
        logging.error(
            "unable to retrieve the content from %s due to an error: %s",
            page_url,
            str(e)
        )
        raise e from e
    try:
        soup = bs4.BeautifulSoup(response.text, "html.parser")
    except Exception as e:
        logging.error("the HTML from %s cannot be parsed: %s", page_url, str(e))
        raise e from e

    return soup
