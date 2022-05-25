import json
import pathlib
from typing import Any, Iterator, Union


def _write_first_product_dict(file_path: Union[str, pathlib.Path], product: dict) -> None:
    with open(file_path, "w") as f:
        f.write(f"[{json.dumps(product)}")


def _write_non_first_product_dict(file_path: Union[str, pathlib.Path], product: dict) -> None:
    with open(file_path, "a") as f:
        f.write(f",{json.dumps(product)}")


def _write_final_bracket_to_json_file(file_path: Union[str, pathlib.Path]) -> None:
    with open(file_path, "a") as f:
        f.write("]")


def _manage_html(product: dict, include_html: bool) -> dict:
    if not include_html:
        product = product.copy()
        product["body_html"] = ""
    return product


def _write_individual_products_to_json(
    products: Iterator[dict],
    file_path: Union[str, pathlib.Path],
    include_html: bool,
) -> None:
    """writes product objects to json file

    Args:
        products: iterator of product objects
        file_path: path to json file
        include_html: whether to include body_html field in product objects if it exists in json file, default True
    """
    for i, product in enumerate(products):
        product = _manage_html(product, include_html)
        if i == 0:
            _write_first_product_dict(file_path, product)
        else:
            _write_non_first_product_dict(file_path, product)


def save_json(
    products: Iterator[dict],
    file_path: Union[str, pathlib.Path],
    include_html: bool,
) -> None:
    """writes product objects to json file with correct json formatting

    Args:
        products: iterator of product objects
        file_path: path to json file
        include_html: whether to include body_html field in product objects if it exists in json file, default True
    """
    _write_individual_products_to_json(products, file_path, include_html)
    _write_final_bracket_to_json_file(file_path)


def read_json_file(
    file_path: Union[str, pathlib.Path],
) -> Any:
    """creates and yields product objects from json file using write_products_to_json_file function

    Args:
        file_path: path to json file
    Yields:
        ShopifyProduct objects
    """
    with open(file_path, "r") as f:
        return json.load(f)
