from datetime import date

from django.test import TestCase

from pfx.pfxcore.test import APIClient, TestAssertMixin
from tests.models import Author, Book, BookType


class TestCache(TestAssertMixin, TestCase):

    def setUp(self):
        self.client = APIClient(default_locale='en')

    @classmethod
    def setUpTestData(cls):
        cls.author1 = Author.objects.create(
            first_name='John Ronald Reuel',
            last_name='Tolkien',
            slug='jrr-tolkien')
        cls.heroic_fantasy = BookType.objects.create(
            name="Heroic Fantasy")
        cls.author1_book1 = Book.objects.create(
            author=cls.author1,
            name="The Fellowship of the Ring",
            pub_date=date(1954, 1, 1),
            type=cls.heroic_fantasy)
        cls.author1_book2 = Book.objects.create(
            author=cls.author1,
            name="The Two Towers",
            pub_date=date(1954, 1, 1),
            type=cls.heroic_fantasy)
        cls.author1_book3 = Book.objects.create(
            author=cls.author1,
            name="The Return of the King",
            pub_date=date(1955, 1, 1),
            type=cls.heroic_fantasy)

    def test_cache_author_updated(self):
        Author.CACHE.clear()

        response = self.client.get(f'/api/authors/cache/{self.author1.pk}')
        self.assertRC(response, 200)
        self.assertJE(response, 'meta.from_cache', False)

        response = self.client.get(f'/api/authors/cache/{self.author1.pk}')
        self.assertRC(response, 200)
        self.assertJE(response, 'meta.from_cache', True)

        response = self.client.put(f'/api/authors/{self.author1.pk}', dict(
            last_name="Updated"))
        self.assertRC(response, 200)

        response = self.client.get(f'/api/authors/cache/{self.author1.pk}')
        self.assertRC(response, 200)
        self.assertJE(response, 'meta.from_cache', False)
        self.assertJE(response, 'last_name', "Updated")

    def test_cache_author_book_updated(self):
        Author.CACHE.clear()

        response = self.client.get(f'/api/authors/cache/{self.author1.pk}')
        self.assertRC(response, 200)
        self.assertJE(response, 'meta.from_cache', False)

        response = self.client.get(f'/api/authors/cache/{self.author1.pk}')
        self.assertRC(response, 200)
        self.assertJE(response, 'meta.from_cache', True)

        response = self.client.put(f'/api/books/{self.author1_book1.pk}', dict(
            name="Book Updated"))
        self.assertRC(response, 200)

        response = self.client.get(f'/api/authors/cache/{self.author1.pk}')
        self.assertRC(response, 200)
        self.assertJE(response, 'meta.from_cache', False)

    def test_cache_author_book_type_updated(self):
        Author.CACHE.clear()

        response = self.client.get(f'/api/authors/cache/{self.author1.pk}')
        self.assertRC(response, 200)
        self.assertJE(response, 'meta.from_cache', False)

        response = self.client.get(f'/api/authors/cache/{self.author1.pk}')
        self.assertRC(response, 200)
        self.assertJE(response, 'meta.from_cache', True)

        response = self.client.put(
            f'/api/book-types/{self.heroic_fantasy.pk}', dict(
                name="Type Updated", slug="updated"))
        self.assertRC(response, 200)

        response = self.client.get(f'/api/authors/cache/{self.author1.pk}')
        self.assertRC(response, 200)
        self.assertJE(response, 'meta.from_cache', False)

    def test_cache_author_book_type_deleted(self):
        Author.CACHE.clear()

        response = self.client.get(f'/api/authors/cache/{self.author1.pk}')
        self.assertRC(response, 200)
        self.assertJE(response, 'meta.from_cache', False)

        response = self.client.get(f'/api/authors/cache/{self.author1.pk}')
        self.assertRC(response, 200)
        self.assertJE(response, 'meta.from_cache', True)

        response = self.client.delete(
            f'/api/book-types/{self.heroic_fantasy.pk}')
        self.assertRC(response, 200)

        response = self.client.get(f'/api/authors/cache/{self.author1.pk}')
        self.assertRC(response, 200)
        self.assertJE(response, 'meta.from_cache', False)
