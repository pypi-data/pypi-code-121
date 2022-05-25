from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class Image(BaseModel):
    """image object

    Attributes:
        id (int): image id
        created_at (datetime.datetime): datetime object of when image was created
        position (int): position of image in product
        updated_at (datetime.datetime): datetime object of when image was last updated
        product_id (int): product id associated with the image
        variant_ids (list[int]): list of variant ids associated with the image
        src (str): url to image
        width (int): width of image in pixels
        height (int): height of image in pixels
    """

    id: int
    created_at: datetime
    position: int
    updated_at: str
    product_id: int
    variant_ids: list[int]
    src: str
    width: int
    height: int


class Options(BaseModel):

    """
    Options object

    Attributes:
        name (str): name of option
        position (int): position of option in product
        values (list[Any]): list of values for option
    """

    name: str
    position: int
    values: list[str]


class Variant(BaseModel):
    """
    Variant object

    Attributes:
        id (int): variant id
        title (str): title of variant
        option1 (str): first option of variant
        option2 (str): second option of variant
        option3 (str): third option of variant
        sku (str): sku of variant
        requires_shipping (bool): whether variant requires shipping
        taxable (bool): whether variant is taxable
        featured_image (Image): featured image of variant
        price (float): price of variant
        grams (int): weight of variant in grams
        compare_at_price (Optional(float)): compare at price of variant
        position (int): position of variant in product
        product_id (int): product id associated with the variant
        created_at (datetime.datetime): datetime object of when variant was created
        updated_at (datetime.datetime): datetime object of when variant was last updated
    """

    id: int
    title: str
    option1: Optional[str]
    option2: Optional[str]
    option3: Optional[str]
    sku: Optional[str]
    requires_shipping: bool
    taxable: bool
    featured_image: Optional[Image]
    available: bool
    price: float
    grams: int
    compare_at_price: Optional[float]
    position: int
    product_id: int
    created_at: datetime
    updated_at: datetime


class Product(BaseModel):
    """
    Object representing a product from a Shopify webshop

    Attributes:
        id (int): product id
        title (str): name of product
        handle (str): url safe name of product
        body_html (str): description of product (html)
        published_at (datetime.datetime): date product was published
        created_at (datetime.datetime): date product was created
        updated_at (datetime.datetime): date product was last updated
        vendor (str): name of product vendor
        product_type (str): type of product
        tags (list[str]): tags associated with product
        variants (list[Variants]): list of variants for product
        images (list[Image]): list of images for product
        options (list[Options]): list of options for product
    """

    id: int
    title: str
    handle: str
    body_html: Optional[str]
    published_at: datetime
    created_at: datetime
    updated_at: datetime
    vendor: str
    product_type: str
    tags: list[str]
    variants: list[Variant]
    images: list[Image]
    options: list[Options]


def product_factory(
    product_dict: dict,
    include_html: bool = True,
) -> Product:
    """create Title objects from list of dicts

    Args:
        product_dict: list of dicts of product info
        include_html: whether to include body_html field in product objects, default True
    Returns:
        list of ShopifyProducts objects
    """
    if not include_html:
        product_dict = product_dict.copy()
        product_dict["body_html"] = ""
    return Product(**product_dict)
