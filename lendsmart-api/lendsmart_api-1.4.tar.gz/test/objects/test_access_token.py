import time
import unittest
from lendsmart_api import LendsmartClient

from test.base import ClientBaseCase
from datetime import datetime

from lendsmart.jwt.access_token import AccessToken

ACCOUNT_SID = 'AC123'
SIGNING_KEY_SID = 'SK123'


# python2.6 support
def assert_is_not_none(obj):
    assert obj is not None, '%r is None' % obj


def assert_in(obj1, obj2):
    assert obj1 in obj2, '%r is not in %r' % (obj1, obj2)


def assert_greater_equal(obj1, obj2):
    assert obj1 > obj2, '%r is not greater than or equal to %r' % (obj1, obj2)


class AccessTokenTest(unittest.TestCase, ClientBaseCase):
    def _validate_claims(self, payload):
        assert_equal(SIGNING_KEY_SID, payload['iss'])
        assert_equal(ACCOUNT_SID, payload['sub'])

        assert_is_not_none(payload['exp'])
        assert_is_not_none(payload['jti'])
        assert_is_not_none(payload['grants'])

        assert_greater_equal(payload['exp'], int(time.time()))

        assert_in(payload['iss'], payload['jti'])

    def test_empty_grants(self):
        scat = AccessToken(ACCOUNT_SID, SIGNING_KEY_SID, 'secret')
        token = scat.to_jwt()

        assert_is_not_none(token)
        decoded_token = AccessToken.from_jwt(token, 'secret')
        self._validate_claims(decoded_token.payload)
        assert_equal({}, decoded_token.payload['grants'])
