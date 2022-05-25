# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

import jwt
import time

from unittest import TestCase, mock
from dicom_client.token import TokenCache


def make_get_token_func():
    count = 0

    def get_token_func():
        nonlocal count
        count += 1
        return jwt.encode({"exp": 1606360460.985007, "count": count}, key="secret")

    return get_token_func


class TokenCacheTest(TestCase):
    def setUp(self):
        self.token_cache = TokenCache(make_get_token_func())

    @mock.patch("time.time", mock.MagicMock(return_value=1606360480.985007))
    def test_expired_jwt(self):
        self.assertTrue(self.token_cache.should_refresh())
        token1 = self.token_cache.get_token()
        self.assertIsNotNone(token1)
        self.assertTrue(self.token_cache.should_refresh())
        token2 = self.token_cache.get_token()
        self.assertIsNotNone(token2)
        self.assertNotEqual(token1, token2)

    @mock.patch("time.time", mock.MagicMock(return_value=1606360400.985007))
    def test_expired_jwt_copy(self):
        token1 = self.token_cache.get_token()
        self.assertIsNotNone(token1)
        self.assertFalse(self.token_cache.should_refresh())
        token2 = self.token_cache.get_token()
        self.assertIsNotNone(token2)
        self.assertEqual(token1, token2)
