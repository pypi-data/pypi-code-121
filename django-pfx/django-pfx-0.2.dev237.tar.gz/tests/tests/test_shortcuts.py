from django.test import TestCase

from pfx.pfxcore.exceptions import ModelNotFoundAPIError
from pfx.pfxcore.shortcuts import f, get_object, get_pk, parse_bool
from pfx.pfxcore.test import TestAssertMixin
from tests.models import Author, Book


class ShortcutTest(TestAssertMixin, TestCase):

    def test_f(self):
        text = f('Test {first}, {second}', first='first', second='second')
        self.assertEqual(text, 'Test first, second')

    def test_get_object(self):
        with self.assertRaises(ModelNotFoundAPIError):
            get_object(Book.objects.all(), pk=-99)
        author = Author.objects.create(
            first_name='John Ronald Reuel',
            last_name='Tolkien',
            slug='jrr-tolkien')
        a = get_object(Author.objects.all(), pk=author.pk)
        self.assertEqual(a.pk, author.pk)

    def test_get_pk(self):
        author = dict(
            pk=122,
            ressource_name='John Ronald Reuel Tolkien')
        pk = get_pk(122)
        self.assertEqual(pk, 122)
        pk = get_pk(author)
        self.assertEqual(pk, 122)

    def test_parse_bool(self):
        self.assertFalse(parse_bool('false'))
        self.assertFalse(parse_bool('False'))
        self.assertFalse(parse_bool('FALSE'))
        self.assertTrue(parse_bool('true'))
        self.assertTrue(parse_bool('True'))
        self.assertTrue(parse_bool('TRUE'))
