import unittest
import random
import string
from urllib.parse import urljoin, urlparse, unquote

from rebotics_sdk.providers import FVMProvider


class GenerateTokenTestCase(unittest.TestCase):
    def test_success(self):
        codename = 'retailer_x'
        secret_key = 'secret_key_x'
        file_url = 'file_url'
        path = '/api/previews/'
        barcode = '21152'
        scheme = 'https'
        netloc = 'r3dev-fvm.rebotics.net'
        allowed_chars = ''.join((string.ascii_letters, string.digits))
        unique_id = ''.join(random.choice(allowed_chars) for _ in range(44))
        fvm_provider = FVMProvider(f'{scheme}://{netloc}/')
        fvm_provider.set_retailer_identifier(codename, secret_key)
        token = fvm_provider.generate_token(file_url)
        self.assertNotEqual(token, unique_id)
        permalink = fvm_provider.get_preview_permalink(barcode)
        parsed_permalink = urlparse(permalink)
        self.assertEqual(permalink, unquote(permalink))
        self.assertEqual(parsed_permalink.scheme, scheme)
        self.assertEqual(parsed_permalink.netloc, netloc)
        self.assertEqual(parsed_permalink.path, f'{path}{barcode}/')
        self.assertEqual(parsed_permalink.query.split("codename=")[1].split("&")[0], codename)

    def test_raise_exception(self):
        fvm_provider = FVMProvider('host')
        with self.assertRaises(AttributeError):
            fvm_provider.generate_token('file_url')
