import logging
import time
from typing import Any, Iterator, Optional

import requests

from shopscraper import headers

log = logging.getLogger(__name__)


def _validate_integer_arg(arg: Any) -> int:
    """validate integer argument

    Args:
        arg: argument to validate
    Returns:
        validated argument
    """
    try:
        return int(arg)
    except ValueError as e:
        raise ValueError("Argument must be an integer") from e


def _request_json(url: str, headers: Optional[dict[str, str]] = None) -> Any:
    """
    download json product page from bjjfanatics.com

    Args:
        page_number: page number to download
    Returns:
        list of dicts
    """
    try:
        page = requests.get(url, headers=headers)
    except (requests.exceptions.RequestException, requests.exceptions.ConnectionError) as e:
        log.error(f"Error accessing page: {e}")
        raise e
    try:
        return page.json()
    except requests.JSONDecodeError as e:
        log.error(f"Error decoding json: {e.args[0]}")
        raise e


def _construct_url(domain_name: str, items_per_page: int, page_number: int) -> str:
    """construct url for shopify api request

    Args:
        items_per_page: number of items per page
        page_number: page number to request
    Returns:
        url for shopify api request
    """
    return f"https://{domain_name}/products.json?limit={items_per_page}&page={page_number}"


def yield_product_dicts(
    domain_name: str,
    items_per_page: int = 250,
    max_pages: int = 999,
) -> Iterator[dict]:
    """control data download from api

    Args:
        items_per_page: number of items per page, default 250
        max_pages: max number of pages to request, default 999
    Yields:
        dicts of product info
    """
    page_number = 1
    [_validate_integer_arg(i) for i in (items_per_page, max_pages)]
    request_headers = headers.get_headers()
    while True:
        log.info(f"Fetching page number: {page_number}")
        url = _construct_url(domain_name, items_per_page, page_number)
        data = _request_json(url, headers=request_headers)
        products = data["products"]
        yield from products
        if not products or page_number == max_pages:
            break
        page_number += 1
        time.sleep(1)
