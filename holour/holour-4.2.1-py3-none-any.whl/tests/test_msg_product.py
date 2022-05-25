from unittest import TestCase

from holour import json_encode, json_decode
from holour.msg import Product


class Test(TestCase):

    def test_product(self):
        product = Product('uuid_1', 'product_1', "No image", "test")
        product_string = json_encode(product)
        expected_string = '{"_type": "product", "uuid": "uuid_1", "name": "product_1", "image": "No image", ' \
                          '"category": "test", "process_uuid": "", "pick_pose": null, "agents": [], "tags": [], ' \
                          '"description": ""}'

        assert type(product_string) == str
        assert product_string == expected_string, f"Expected {expected_string}, got: {product_string}"

        product_decoded = json_decode(product_string)
        assert type(product_decoded) == Product, f"Got: {type(product_decoded)}. Expected {Product}"
        assert product_decoded == product, "The decoded object must be equal to the encoded"

    def test_product_equals(self):
        p1 = Product('uuid_1', 'product_1', "No image", "test")
        p2 = Product('uuid_1', 'product_1', "No image", "test")
        p3 = Product('uuid_2', 'product_1', "No image", "test")

        assert p1 == p2
        assert p1 != p3
        assert p1 != "not status"

    def test_product_repr(self):
        product = Product('uuid_1', 'product_1', "No image", "test")
        expected, got = 'No image', f'{product}'

        assert expected in got, f"Expected {expected} in got: {got}"
