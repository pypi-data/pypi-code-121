from datetime import date
from unittest.mock import patch

import django
from django.test import TestCase

from pfx.pfxcore.test import APIClient, TestAssertMixin
from tests.models import Author


class TestTools(TestAssertMixin, TestCase):

    def setUp(self):
        self.client = APIClient(default_locale='en')

    @classmethod
    def setUpTestData(cls):
        cls.author1 = Author.objects.create(
            first_name='John Ronald Reuel',
            last_name='Tolkien',
            slug='jrr-tolkien')
        pass

    @patch('builtins.print')
    def test_key_error(self, mock_print):
        response = self.client.get('/api/authors/filters')
        self.assertRC(response, 200)
        with self.assertRaises(Exception):
            self.assertJE(response, 'items.@0.name-not-exists', 'not exists')

    @patch('builtins.print')
    def test_index_error(self, mock_print):
        response = self.client.get('/api/authors/filters')
        self.assertRC(response, 200)
        with self.assertRaises(Exception):
            self.assertJE(response, 'items.@99.name', 'gender')

    @patch('builtins.print')
    def test_print_response(self, mock_print):
        response = self.client.get(f'/api/authors/{self.author1.pk}')

        self.assertRC(response, 200)
        response.print()

        self.assertEqual(mock_print.call_count, 1)
        printed = mock_print.call_args.args[0]
        self.assertIn(
            '******************** http response ********************', printed)
        self.assertIn('Status : 200 OK', printed)
        self.assertIn('Headers : ', printed)
        if django.VERSION[0] >= 4:
            self.assertIn("""  Content-Type: application/json
  Content-Length: %s
  X-Content-Type-Options: nosniff
  Referrer-Policy: same-origin
  Cross-Origin-Opener-Policy: same-origin
  Vary: Accept-Language
  Content-Language: en
""" % (response.headers['Content-Length']), printed)
        else:
            self.assertIn("""  Content-Type: application/json
  Content-Length: %s
  X-Content-Type-Options: nosniff
  Referrer-Policy: same-origin
  Vary: Accept-Language
  Content-Language: en
""" % (response.headers['Content-Length']), printed)
        self.assertIn('Content : ', printed)
        self.assertIn('"books": []', printed)
        self.assertIn('"create_comment": null,', printed)
        self.assertIn(f'"created_at": "{date.today()}"', printed)
        self.assertIn('"first_name": "John Ronald Reuel",', printed)
        self.assertIn(""""gender": {
        "label": "Male",
        "value": "male"
    },""", printed)
        self.assertIn('"last_name": "Tolkien",', printed)
        self.assertIn('"name_length": 25,', printed)
        self.assertIn(f'"pk": {self.author1.pk},', printed)
        self.assertIn('"resource_name": "John Ronald Reuel Tolkien",', printed)
        self.assertIn('"slug": "jrr-tolkien",', printed)
        self.assertIn('"update_comment": null', printed)
        self.assertIn('"meta": {},', printed)
