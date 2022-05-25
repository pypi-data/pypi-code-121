from urllib.parse import urljoin
from typing import Optional

from django.conf import settings

import requests
from dnoticias_services.utils.request import get_headers

from .base import BaseSubscriptionRequest


class BaseProductRequest(BaseSubscriptionRequest):
    @staticmethod
    def get_url(uuid: Optional[str] = None) -> str:
        """Returns a product url

        :param uuid: Product UUID in case of update/delete
        :type uuid: str, optional
        ...
        :return: Product url
        :rtype: str
        """
        url = settings.PRODUCT_API_URL

        if uuid:
            url = urljoin(settings.PRODUCT_API_URL, str(uuid) + "/")

        return url


class ProductService(BaseProductRequest):
    @classmethod
    def create(
        cls,
        name: str,
        slug: str,
        price: int,
        remote_id: str,
        active: bool = True,
        extra_attrs: dict = dict(),
        description: str = "",
        shippable: bool = False,
        is_consumable: bool = False,
        is_product: bool = False,
        accounting_code: Optional[str] = None,
        api_key: Optional[str] = None,
        timeout: Optional[int] = None
    ) -> requests.Response:
        """Creates a new product/consumable on subscriptions system

        :param name: Product name
        :type name: str 
        :param slug: Product slug
        :type slug: str 
        :param price: Product price (must be int, if the price is 9.99, you need to pass 999)
        :type price: int
        :param remote_id: Product ID that will be saved in subscriptions as remote id (i.e:
            Edition id), defaults to False
        :type remote_id: str 
        :param active: Product active, defaults to True
        :type active: bool, optional
        :param extra_attrs: Extra attributes. Here can be additional information for internal use,
            defaults to dict()
        :type extra_attrs: dict, optional
        :param description: Product description, defaults to ""
        :type description: str, optional
        :param shippable: Is the product shippable? defaults to False
        :type shippable: bool, optional
        :param is_consumable: Is the product a consumable? defaults to False
        :type is_consumable: bool, optional
        :param is_product: Is the product a product(yup)? defaults to False
        :type is_product: bool, optional
        :param accounting_code: Code used for accounting purposes, defaults to None
        :type accounting_code: str, optional
        :param api_key: Custom API Key, defaults to None
        :type api_key: str, optional
        :param timeout: Seconds until the request return a timeout. Change this if the request
            for some reason the request lasts more than 5sec, defaults to None
        :type timeout: int, optional
        ...
        :return: Response from subscriptions
        :rtype: Response
        """
        url = cls.get_url()
        _api_key = api_key or cls.API_KEY
        _timeout = timeout or cls.TIMEOUT

        response = requests.post(
            url,
            headers=get_headers(_api_key),
            json={
                "name": name,
                "slug": slug,
                "extra_attrs": extra_attrs,
                "description": description,
                "price": price,
                "active": active,
                "shippable": shippable,
                "accounting_code": accounting_code,
                "is_consumable": is_consumable,
                "is_product": is_product,
                "remote_id": remote_id,
            },
            timeout=_timeout
        )
        response.raise_for_status()
        return response

    @classmethod
    def update(
        cls,
        uuid: str,
        name: Optional[str] = None,
        slug: Optional[str] = None,
        price: Optional[int] = None,
        active: Optional[bool] = None,
        extra_attrs: Optional[bool] = None,
        description: Optional[str] = None,
        shippable: Optional[bool] = None,
        accounting_code: Optional[str] = None,
        api_key: Optional[str] = None,
        timeout: Optional[int] = None
    ) -> requests.Response:
        """Updates product on subscriptions system

        :param uuid: Product uuid
        :type uuid: str
        :param name: Product name, defaults to None
        :type name: str, optiona
        :param slug: Product slug, defaults to None
        :type slug: str, optional
        :param price: Product price (must be int, if the price is 9.99, you need to pass 999), 
            defaults to None
        :type price: int, optional
        :param active: Product active, defaults to True
        :type active: bool, optional
        :param extra_attrs: Extra attributes. Here can be additional information for internal use,
            defaults to None
        :type extra_attrs: dict, optional
        :param description: Product description, defaults to None
        :type description: str, optional
        :param shippable: Is the product shippable? defaults to None
        :type shippable: bool, optional
        :param accounting_code: Code used for accounting purposes, defaults to None
        :type accounting_code: str, optional
        :param api_key: Custom API Key, defaults to None
        :type api_key: str, optional
        :param timeout: Seconds until the request return a timeout. Change this if the request
            for some reason the request lasts more than 5sec, defaults to None
        :type timeout: int, optional
        ...
        :return: Response from subscriptions
        :rtype: Response
        """
        assert uuid

        url = cls.get_url(uuid)
        _api_key = api_key or cls.API_KEY
        _timeout = timeout or cls.TIMEOUT

        context = {
            "name": name,
            "slug": slug,
            "extra_attrs": extra_attrs,
            "description": description,
            "price": price,
            "active": active,
            "shippable": shippable,
            "accounting_code": accounting_code,
        }

        # Will send on body only those the params with a value
        response = requests.patch(
            url,
            headers=get_headers(_api_key),
            json={key: context[key] for key in context.keys() if key is not None},
            timeout=_timeout
        )

        response.raise_for_status()
        return response

    @classmethod
    def delete(
        cls,
        uuid: str,
        api_key: Optional[str] = None,
        timeout: Optional[int] = None
    ) -> requests.Response:
        """Deletes a product on subscriptions system

        :param uuid: Product UUID
        :type uuid: str
        :param api_key: Custom API Key, defaults to None
        :type api_key: str, optional
        :param timeout: Seconds until the request return a timeout. Change this if the request
            for some reason the request lasts more than 5sec, defaults to None
        :type timeout: int, optional
        ...
        :return: Response from subscriptions
        :rtype: Response
        """
        _api_key = api_key or cls.API_KEY
        _timeout = timeout or cls.TIMEOUT

        response = requests.delete(
            cls.get_url(uuid),
            headers=get_headers(_api_key),
            timeout=_timeout
        )

        response.raise_for_status()
        return response
