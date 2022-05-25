import pathlib
from typing import Iterator, Union

from shopscraper import json_handler, prod_objs, scraper
from shopscraper.prod_objs import Product


def scrape(
    domain_name: str,
    *,
    include_html: bool = True,
    items_per_page: int = 250,
    max_pages: int = 999,
) -> Iterator[Product]:
    """download products from shopify api and returns product objects

    Args:
        domain_name: fully qualified domain name to webshop (e.g., www.myshopify.com)
        include_html: whether to include body_html field in product objects, default True
        items_per_page: number of items per page. maximum 250, default 250
        max_pages: max number of pages to request, default 999
    Yields:
        ShopifyProduct objects
    """
    n_items = min(items_per_page, 250)
    products = scraper.yield_product_dicts(
        domain_name,
        items_per_page=n_items,
        max_pages=max_pages,
    )
    for product in products:
        yield prod_objs.product_factory(product, include_html)


def read_json(
    file_path: Union[str, pathlib.Path],
    *,
    include_html: bool = True,
) -> Iterator[Product]:
    """creates and yields product objects from json file using write_products_to_json_file function

    Args:
        file_path: path to json file
        include_html: whether to include body_html field in product objects if it exists in json file, default True
    Yields:
        Product objects
    """
    products = json_handler.read_json_file(file_path)
    for product in products:
        yield prod_objs.product_factory(product, include_html)


def scrape_to_json(
    domain_name: str,
    file_path: Union[str, pathlib.Path],
    *,
    include_html: bool = True,
    items_per_page: int = 250,
    max_pages: int = 999,
) -> pathlib.Path:
    """download products from shopify api and write products to json file

    Args:
        domain_name: fully qualified domain name to webshop (e.g., www.myshopify.com)
        file_path: path to file to write products to
        include_html: whether to include body_html field in product objects, default True
        items_per_page: number of items per page, default 250
        max_pages: max number of pages to request, default 999
    Returns:
        pathlib.Path object to json file
    """
    n_items = min(items_per_page, 250)
    products = scraper.yield_product_dicts(
        domain_name,
        items_per_page=n_items,
        max_pages=max_pages,
    )
    file_path = pathlib.Path(file_path)
    json_handler.save_json(products, file_path, include_html)
    return file_path
