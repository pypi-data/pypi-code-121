#!/usr/bin/python
# -*- coding: utf-8 -*-

import json

from . import utils

class ShopifyCommons(object):

    PRODUCT_TYPE = "Platforme"
    """ The type to use when creating a custom product,
    should properly identify it from the remaining products
    in the catalog (dummy product) """

    PRODUCT_TAGS = "platforme"
    """ The comma-separated tags to use when creating
    a customizable product """

    @classmethod
    def build_shopify_product(cls, **kwargs):
        """
        Generates a product payload (dictionary) ready to be used for the
        creation of an equivalent Shopify product.

        The structure of the payload must respect the equivalent structure
        of the product under the Shopify API.
        """

        # computes the values for the shopify product payload using the appropriate
        # 3DB business logic overrides or the default implementations
        title = utils.try_execute_method("build_shopify_title", fallback = cls.build_shopify_title, **kwargs)
        price = utils.try_execute_method("build_shopify_price", fallback = cls.build_shopify_price, **kwargs)
        size_scaled = utils.try_execute_method("build_shopify_size", fallback = cls.build_shopify_size, **kwargs)
        scale = utils.try_execute_method("build_shopify_scale", fallback = cls.build_shopify_scale, **kwargs)
        gender = utils.try_execute_method("build_shopify_gender", fallback = cls.build_shopify_gender, **kwargs)
        sku = utils.try_execute_method("build_shopify_sku", fallback = cls.build_shopify_sku, **kwargs)
        customized_variant = utils.try_execute_method("build_shopify_variant", fallback = cls.build_shopify_variant, **kwargs)

        # builds the options and customized variant dictionary to
        # use in the returned payload
        options = []

        if size_scaled:
            options.append(dict(name = "Size"))
            customized_variant["option%d" % len(options)] = size_scaled

        if scale:
            options.append(dict(name = "Scale"))
            customized_variant["option%d" % len(options)] = scale

        if gender:
            options.append(dict(name = "Gender"))
            customized_variant["option%d" % len(options)] = gender

        if price and not "price" in customized_variant:
            customized_variant["price"] = price

        if sku and not "sku" in customized_variant:
            customized_variant["sku"] = sku

        return dict(
            title = title,
            options = options,
            variants = [customized_variant],
            metafields = [
                dict(
                    namespace = "seo",
                    key = "hidden",
                    value = 1,
                    value_type = "integer"
                ),
                dict(
                    namespace = "platforme",
                    key = "context",
                    value = json.dumps(dict(
                        brand = kwargs.get("brand"),
                        model = kwargs.get("model"),
                        variant = kwargs.get("variant"),
                        version = kwargs.get("version"),
                        parts = kwargs.get("parts"),
                        initials_extra = kwargs.get("initials_extra"),
                        size = kwargs.get("size"),
                        scale = scale,
                        gender = gender,
                        size_scaled = size_scaled,
                        currency = kwargs.get("currency"),
                        country = kwargs.get("country"),
                        flag = kwargs.get("flag")
                    )),
                    value_type = "json_string"
                )
            ],
            product_type = cls.PRODUCT_TYPE,
            tags = cls.PRODUCT_TAGS
        )

    @classmethod
    def build_shopify_title(cls, product_title = None, original_product = None, **kwargs):
        if product_title: return product_title
        if original_product: return original_product["title"]
        return None

    @classmethod
    def build_shopify_price(
        cls,
        ripe_api = None,
        brand = None,
        model = None,
        parts = None,
        variant = None,
        version = None,
        initials_extra = None,
        currency = None,
        country = None,
        flag = None,
        **kwargs
    ):
        price = ripe_api.price_config(
            brand = brand,
            model = model,
            p = parts,
            variant = variant,
            version = version,
            initials_extra = initials_extra,
            currency = currency,
            country = country,
            flag = flag
        )
        return price["total"]["price_final"]

    @classmethod
    def build_shopify_size(
        cls,
        ripe_api = None,
        size = None,
        scale = None,
        gender = None,
        size_scaled = None,
        **kwargs
    ):
        if size_scaled: return size_scaled
        if scale == "one_size": return "One Size"
        if not scale or not size or not gender or not ripe_api: return None
        size_scaled = ripe_api.native_to_size(scale, size, gender)["value"]
        is_decimal = not size_scaled % 1 == 0
        return size_scaled if is_decimal else int(size_scaled)

    @classmethod
    def build_shopify_scale(
        cls,
        scale = None,
        **kwargs
    ):
        if not scale: return None
        return scale.upper()

    @classmethod
    def build_shopify_gender(
        cls,
        gender = None,
        **kwargs
    ):
        if not gender: return None
        return gender.capitalize()

    @classmethod
    def build_shopify_sku(
        cls,
        ripe_api = None,
        brand = None,
        model = None,
        variant = None,
        parts = None,
        initials_extra = None,
        size = None,
        gender = None,
        **kwargs
    ):
        try:
            sku_config = ripe_api.sku_config(
                brand = brand,
                model = model,
                variant = variant,
                p = parts,
                initials_extra = initials_extra,
                size = size,
                gender = gender
            )
            sku = sku_config.get("sku")
            return sku
        except Exception as err:
            if not err.code == 400: raise
            return None

    @classmethod
    def build_shopify_variant(cls, **kwargs):
        return dict()
