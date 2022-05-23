from datetime import date
from unittest.mock import MagicMock, patch

from django.db import connection
from django.test import TestCase, override_settings

from pfx.pfxcore.test import APIClient, MockBoto3Client, TestAssertMixin
from tests.models import Author, Book, BookType


class BasicAPITest(TestAssertMixin, TestCase):

    def setUp(self):
        self.client = APIClient(default_locale='en')
        with connection.cursor() as cursor:
            cursor.execute("create extension if not exists unaccent;")

    @classmethod
    def setUpTestData(cls):
        cls.author1 = Author.objects.create(
            first_name='John Ronald Reuel',
            last_name='Tolkien',
            slug='jrr-tolkien')
        cls.author1_book1 = Book.objects.create(
            author=cls.author1,
            name="The Hobbit",
            pub_date=date(1937, 1, 1)
        )
        cls.author1_book2 = Book.objects.create(
            author=cls.author1,
            name="The Fellowship of the Ring",
            pub_date=date(1954, 1, 1)
        )
        cls.author1_book3 = Book.objects.create(
            author=cls.author1,
            name="The Two Towers",
            pub_date=date(1954, 1, 1)
        )
        cls.author1_book4 = Book.objects.create(
            author=cls.author1,
            name="The Return of the King",
            pub_date=date(1955, 1, 1)
        )
        cls.author2 = Author.objects.create(
            first_name='Philip Kindred',
            last_name='Dick',
            science_fiction=True,
            slug='philip-k-dick')
        cls.author3 = Author.objects.create(
            first_name='Isaac',
            last_name='Asimov',
            science_fiction=True,
            slug='isaac-asimov')
        cls.author3_book1 = Book.objects.create(
            author=cls.author3,
            name="The Caves of Steel",
            pub_date=date(1954, 1, 1),
            pages=224,
            rating=4.6,
        )
        cls.author3_book2 = Book.objects.create(
            author=cls.author3,
            name="The Naked Sun",
            pub_date=date(1957, 1, 1),
        )
        cls.author3_book3 = Book.objects.create(
            author=cls.author3,
            name="The Robots of Dawn",
            pub_date=date(1983, 1, 1),
        )
        cls.author4 = Author.objects.create(
            first_name='Joanne',
            last_name='Rowling',
            science_fiction=False,
            gender='female',
            slug='j-k-rowling')

    def test_get_list(self):
        response = self.client.get('/api/authors')

        self.assertRC(response, 200)
        self.assertJE(response, 'meta.count', 4)

    def test_get_list_order_options(self):
        response = self.client.get('/api/books')
        self.assertRC(response, 200)
        self.assertJIn(response, 'meta.order_options', 'pk')
        self.assertJIn(response, 'meta.order_options', 'name')
        self.assertJIn(response, 'meta.order_options', 'author')
        self.assertJIn(response, 'meta.order_options', 'author__pk')
        self.assertJIn(response, 'meta.order_options', 'author__first_name')

    def test_get_list_order_asc(self):
        response = self.client.get('/api/authors?order=last_name')

        names = [i['last_name'] for i in response.json_content['items']]
        self.assertEqual(names, ['Asimov', 'Dick', 'Rowling', 'Tolkien'])

    def test_get_list_order_desc(self):
        response = self.client.get('/api/authors?order=-last_name')

        names = [i['last_name'] for i in response.json_content['items']]
        self.assertEqual(names, ['Tolkien', 'Rowling', 'Dick', 'Asimov'])

    def test_get_list_order_multi(self):
        response = self.client.get('/api/authors?order=gender,last_name')

        names = [i['last_name'] for i in response.json_content['items']]
        self.assertEqual(names, ['Rowling', 'Asimov', 'Dick', 'Tolkien'])

    def test_get_list_order_multi_desc(self):
        response = self.client.get('/api/authors?order=gender,-last_name')

        names = [i['last_name'] for i in response.json_content['items']]
        self.assertEqual(names, ['Rowling', 'Tolkien', 'Dick', 'Asimov'])

    def test_search_list(self):
        response = self.client.get('/api/authors?search=isaac')

        self.assertRC(response, 200)
        self.assertJE(response, 'meta.count', 1)
        self.assertJE(response, 'items.@0.first_name', 'Isaac')
        self.assertJE(response, 'items.@0.last_name', 'Asimov')
        self.assertJE(response, 'items.@0.gender.value', 'male')
        self.assertJE(response, 'items.@0.gender.label', 'Male')

    def test_filter_get(self):
        response = self.client.get('/api/authors/filters')
        self.assertRC(response, 200)
        self.assertJE(response, 'items.@0.name', 'book_gender')
        self.assertJE(response, 'items.@0.items.@0.name', 'science_fiction')

        response = self.client.get('/api/books/filters')
        self.assertRC(response, 200)

    def test_filter_func_bool(self):
        response = self.client.get('/api/authors?heroic_fantasy=true')
        self.assertRC(response, 200)
        self.assertJE(response, 'meta.count', 1)
        self.assertJE(response, 'items.@0.resource_name',
                                'John Ronald Reuel Tolkien')

        response = self.client.get('/api/authors?heroic_fantasy=false')
        self.assertRC(response, 200)
        self.assertJE(response, 'meta.count', 3)

        response = self.client.get(
            '/api/authors?heroic_fantasy=false&heroic_fantasy=true')
        self.assertRC(response, 200)
        self.assertJE(response, 'meta.count', 4)

    def test_filter_func_date(self):
        response = self.client.get('/api/books?pub_date_gte=1955-01-01')
        self.assertRC(response, 200)
        self.assertJE(response, 'meta.count', 3)

    def test_filter_func_char_choices(self):
        response = self.client.get('/api/authors?last_name_choices=Tolkien')
        self.assertRC(response, 200)
        self.assertJE(response, 'meta.count', 1)

    def test_model_filter_bool(self):
        response = self.client.get('/api/authors?science_fiction=true')

        self.assertRC(response, 200)
        self.assertJE(response, 'meta.count', 2)

    def test_model_filter_char(self):
        response = self.client.get('/api/authors?first_name=Isaac')

        self.assertRC(response, 200)
        self.assertJE(response, 'meta.count', 1)
        self.assertJE(response, 'items.@0.first_name', "Isaac")

    def test_model_filter_integer(self):
        response = self.client.get('/api/books?pages=224')

        self.assertRC(response, 200)
        self.assertJE(response, 'meta.count', 1)
        self.assertJE(response, 'items.@0.name', "The Caves of Steel")

    def test_model_filter_float(self):
        response = self.client.get('/api/books?rating=4.6')

        self.assertRC(response, 200)
        self.assertJE(response, 'meta.count', 1)
        self.assertJE(response, 'items.@0.name', "The Caves of Steel")

    def test_model_filter_date(self):
        response = self.client.get('/api/books?pub_date=1954-01-01')

        self.assertRC(response, 200)
        self.assertJE(response, 'meta.count', 3)

    def test_model_filter_decimal(self):
        # TODO: Wait Decimal implementation
        pass

    def test_model_filter_foreign_key(self):
        response = self.client.get(f'/api/books?author={self.author3.pk}')

        self.assertRC(response, 200)
        self.assertJE(response, 'meta.count', 3)
        for item in response.json_content['items']:
            self.assertEqual(item['author']['pk'], self.author3.pk)

    def test_model_filter_foreign_key_null(self):
        book_type = BookType.objects.create(
            name="Epic Fantasy",
            slug="epic-fantasy")
        self.author1_book1.type = book_type
        self.author1_book1.save()

        response = self.client.get(
            f'/api/books?author={self.author1.pk}&type={book_type.pk}')
        self.assertRC(response, 200)
        self.assertJE(response, 'meta.count', 1)

        response = self.client.get(
            f'/api/books?author={self.author1.pk}&type=null')
        self.assertRC(response, 200)
        self.assertJE(response, 'meta.count', 3)
        for item in response.json_content['items']:
            self.assertEqual(item['type'], None)
        response = self.client.get(
            f'/api/books?author={self.author1.pk}&type=0')
        self.assertRC(response, 200)
        self.assertJE(response, 'meta.count', 3)
        for item in response.json_content['items']:
            self.assertEqual(item['type'], None)
        response = self.client.get(
            f'/api/books?author={self.author1.pk}&type=')
        self.assertRC(response, 200)
        self.assertJE(response, 'meta.count', 3)
        for item in response.json_content['items']:
            self.assertEqual(item['type'], None)

        response = self.client.get(
            f'/api/books?author={self.author1.pk}&'
            f'type={book_type.pk}&type=null')
        self.assertRC(response, 200)
        self.assertJE(response, 'meta.count', 4)
        for item in response.json_content['items']:
            self.assertTrue(
                item['type'] is None or item['type']['pk'] == book_type.pk)

    def test_model_filter_char_choices(self):
        response = self.client.get('/api/authors?gender=male')

        self.assertRC(response, 200)
        self.assertJE(response, 'meta.count', 3)

    def test_model_filter_func_bool(self):
        response = self.client.get('/api/authors?last_name=true')

        self.assertRC(response, 200)
        self.assertJE(response, 'meta.count', 4)

    def test_get_list_without_pagination(self):
        response = self.client.get('/api/authors?meta=count')

        self.assertRC(response, 200)
        self.assertJE(response, 'meta.count', 4)

    def test_get_list_with_subset(self):
        for i in range(1, 11):
            Author.objects.create(
                first_name='Vladimir',
                last_name=f'Ottor {i}',
                science_fiction=True,
                slug=f'vald-ottor-{i}')

        response = self.client.get('/api/authors?meta=subset&limit=5')
        self.assertRC(response, 200)
        self.assertJE(response, 'meta.subset.offset', 0)
        self.assertJE(response, 'meta.subset.count', 14)
        item4_pk = response.json_content['items'][3]['pk']

        response = self.client.get('/api/authors?meta=subset&offset=3&limit=5')
        self.assertRC(response, 200)
        # With offset 3 the first item must be the same as the 4th
        # in the request with offest 0.
        self.assertJE(response, 'items.@0.pk', item4_pk)
        self.assertJE(response, 'meta.subset.count', 14)

    def test_wrong_meta(self):
        response = self.client.get('/api/authors?meta=qwertz')

        self.assertRC(response, 400)

    def test_meta_service(self):
        response = self.client.get('/api/authors/meta')
        self.assertRC(response, 200)
        self.assertJE(response, 'first_name.type', 'CharField')
        self.assertJE(response, 'first_name.name', 'First Name')
        self.assertJE(response, 'last_name.type', 'CharField')
        self.assertJE(response, 'last_name.name', 'Last Name')
        self.assertJE(response, 'books.type', 'ModelObjectList')
        self.assertJE(response, 'books.name', 'Books')
        self.assertJE(response, 'created_at.type', 'DateField')
        self.assertJE(response, 'created_at.name', 'Created at')
        self.assertJE(response, 'name_length.type', 'IntegerField')
        self.assertJE(response, 'name_length.name', 'Name Length')
        response = self.client.get('/api/books/meta')
        self.assertJE(response, 'read_time.type', 'MinutesDurationField')
        self.assertJE(response, 'read_time.name', 'Read Time')

    def test_get_detail_by_id(self):
        response = self.client.get(f'/api/authors/{self.author1.pk}')
        self.assertRC(response, 200)
        self.assertJE(response, 'first_name', self.author1.first_name)
        self.assertJE(response, 'last_name', self.author1.last_name)
        self.assertJE(response, 'name_length', 25)
        self.assertJE(response, 'gender.value', 'male')
        self.assertJE(response, 'gender.label', 'Male')

    def test_get_detail_by_slug(self):
        response = self.client.get(f'/api/authors/slug/{self.author1.slug}')
        self.assertRC(response, 200)
        self.assertJE(response, 'first_name', self.author1.first_name)
        self.assertJE(response, 'last_name', self.author1.last_name)
        self.assertJE(response, 'name_length', 25)
        self.assertJE(response, 'gender.value', 'male')
        self.assertJE(response, 'gender.label', 'Male')

    def test_get_date_format(self):
        response = self.client.get(f'/api/books/{self.author1_book1.pk}')
        self.assertRC(response, 200)
        self.assertJE(response, 'pub_date', '1937-01-01')
        response = self.client.get(
            f'/api/books/{self.author1_book1.pk}?date_format=0')
        self.assertRC(response, 200)
        self.assertJE(response, 'pub_date', '1937-01-01')
        response = self.client.get(
            f'/api/books/{self.author1_book1.pk}?date_format=1')
        self.assertRC(response, 200)
        self.assertJE(response, 'pub_date.value', '1937-01-01')
        self.assertJE(response, 'pub_date.formatted', '01/01/1937')

    def test_get_detail_with_rel_object(self):
        response = self.client.get(f'/api/books/{self.author3_book1.pk}')

        self.assertRC(response, 200)
        self.assertJE(response, 'author.pk', self.author3.pk)
        self.assertJE(response, 'author.resource_name', "Isaac Asimov")
        self.assertJE(response, 'author.resource_slug', "isaac-asimov")
        self.assertJEExists(response, 'author.resource_slug')
        self.assertJENotExists(response, 'author.hello')
        self.assertJENotExists(response, 'author.last_name')

    def test_get_detail_with_rel_object_custom(self):
        response = self.client.get(
            f'/api/books-custom-author/{self.author3_book1.pk}')

        self.assertRC(response, 200)
        self.assertJE(response, 'author.pk', self.author3.pk)
        self.assertJE(response, 'author.resource_name', "Isaac Asimov")
        self.assertJE(response, 'author.resource_slug', "isaac-asimov")
        self.assertJE(response, 'author.hello', "World")
        self.assertJE(response, 'author.last_name', "Asimov")

    def test_get_non_existant_record(self):
        response = self.client.get('/api/authors/999999')
        self.assertRC(response, 404)

    def test_get_non_existant_record_by_slug(self):
        response = self.client.get('/api/authors/slug/not-existent')
        self.assertRC(response, 404)

    def test_create(self):
        response = self.client.post(
            '/api/authors', {
                'first_name': 'Arthur Charles',
                'last_name': 'Clarke',
                'name_length': 1,
                'gender': 'male',
                'create_comment': 'CREATE COMMENT',
                'update_comment': 'UPDATE COMMENT',
                'slug': 'arthur-c-clarke'})

        self.assertRC(response, 200)
        self.assertJE(response, 'first_name', 'Arthur Charles')
        self.assertJE(response, 'last_name', 'Clarke')
        self.assertJE(response, 'gender.value', 'male')
        self.assertJE(response, 'gender.label', 'Male')
        self.assertJE(response, 'create_comment', 'CREATE COMMENT')
        self.assertNJE(response, 'update_comment', 'UPDATE COMMENT')

    def test_create_null_values(self):
        response = self.client.post(
            '/api/books', dict(
                name="Test Book",
                author=self.author1.pk,
                type=None,
                pub_date='2000-01-01',
                pages=None,
                rating=None,
                reference=None,
                read_time=None))
        self.assertRC(response, 200)

    def test_create_enum(self):
        response = self.client.post(
            '/api/authors', {
                'first_name': 'Arthur Charles',
                'last_name': 'Clarke',
                'name_length': 1,
                'gender': {'value': 'male'},
                'slug': 'arthur-c-clarke'})

        self.assertRC(response, 200)
        self.assertJE(response, 'first_name', 'Arthur Charles')
        self.assertJE(response, 'last_name', 'Clarke')
        self.assertJE(response, 'gender.value', 'male')
        self.assertJE(response, 'gender.label', 'Male')

    def test_create_unique_custom_message(self):
        response = self.client.post(
            '/api/books', dict(
                name="The Hobbit",
                author=self.author1.pk))
        self.assertRC(response, 422)
        self.assertJE(
            response, '__all__.@0',
            'The Hobbit already exists for John Ronald Reuel Tolkien')

    def test_update(self):
        response = self.client.put(
            f'/api/authors/{self.author1.pk}',
            {'pk': self.author2.pk,  # pk and id must be ignored
             'created_at': '2021-01-01',  # created_at must be ignored because
                                          # it is a readonly field.
             'first_name': 'J. R. R.',
             'name_length': 1,
             'gender': 'female',
             'create_comment': 'CREATE COMMENT UPDATED',
             'update_comment': 'UPDATE COMMENT UPDATED',
             'slug': 'j-r-r-tolkien'})  # slug must be updated})

        self.assertRC(response, 200)
        self.author1.refresh_from_db()
        self.assertEqual(self.author1.first_name, 'J. R. R.')
        self.assertEqual(self.author1.last_name, 'Tolkien')
        self.assertEqual(self.author1.slug, 'j-r-r-tolkien')
        self.assertEqual(self.author1.gender, 'female')
        self.assertNotEqual(self.author1.created_at, '2021-01-01 11:30:00')
        self.assertNotEqual(
            self.author1.create_comment, 'CREATE COMMENT UPDATED')
        self.assertEqual(
            self.author1.update_comment, 'UPDATE COMMENT UPDATED')

        response = self.client.put(
            f'/api/authors/{self.author1.pk}', {'gender': {'value': 'male'}})
        self.assertRC(response, 200)
        self.author1.refresh_from_db()
        self.assertEqual(self.author1.gender, 'male')

    def test_empty_number_fields(self):
        response = self.client.post(
            '/api/books', {
                'name': 'The Fellowship of the Ring, Deluxe Edition',
                'author': self.author1.pk,
                'pub_date': '1954-07-29',
                'pages': '',
                'rating': '',
            })
        self.assertRC(response, 200)
        self.assertJE(response, 'pages', None)
        self.assertJE(response, 'rating', None)

        response = self.client.post(
            '/api/books', {
                'name': 'The Two Towers, Deluxe Edition',
                'author': self.author1.pk,
                'pub_date': '1954-07-29',
                'pages': 500,
                'rating': 5.35,
            })

        self.assertRC(response, 200)
        self.assertJE(response, 'pages', 500)
        self.assertJE(response, 'rating', 5.35)

        response = self.client.put(
            f"/api/books/{response.json_content['pk']}", {
                'pages': '',
                'rating': '',
            })
        self.assertRC(response, 200)
        self.assertJE(response, 'pages', None)
        self.assertJE(response, 'rating', None)

        response = self.client.put(
            f"/api/books/{response.json_content['pk']}", {
                'pages': 600,
                'rating': 6.34,
            })
        self.assertRC(response, 200)
        self.assertJE(response, 'pages', 600)
        self.assertJE(response, 'rating', 6.34)

    def test_delete(self):
        response = self.client.delete(
            f'/api/authors/{self.author2.pk}')

        self.assertRC(response, 200)

        author = Author.objects.filter(pk=self.author2.pk)
        self.assertEqual(author.count(), 0)

    def test_delete_with_wrong_key(self):
        response = self.client.delete(
            '/api/authors/99999')
        self.assertRC(response, 404)

    def test_create_with_foreignkey(self):
        response = self.client.post(
            '/api/books', {
                'name': 'The Fellowship of the Ring, Deluxe Edition',
                'author': self.author1.pk,
                'pub_date': '1954-07-29',
                'created_at': '1954-07-29',
            })
        self.assertRC(response, 200)
        self.assertJE(
            response, 'name', 'The Fellowship of the Ring, Deluxe Edition')
        self.assertJE(response, 'author.pk', self.author1.pk)
        self.assertJE(response, 'pub_date', '1954-07-29')
        self.assertNJE(response, 'created_at', '1954-07-29')

    def test_create_with_foreignkey_resource(self):
        response = self.client.post(
            '/api/books', {
                'name': 'The Fellowship of the Ring, Deluxe Edition',
                'author': {
                    'pk': self.author1.pk,
                    'resource_name': "Author One"},
                'pub_date': '1954-07-29',
                'created_at': '1954-07-29',
            })

        self.assertRC(response, 200)
        self.assertJE(response, 'author.pk', self.author1.pk)

    def test_create_with_wrong_foreignkey(self):
        response = self.client.post(
            '/api/books', {
                'name': 'The Fellowship of the Ring, Deluxe Edition',
                'author': 999999,
                'pub_date': '1954-07-29',
                'created_at': '1954-07-29',
            })
        self.assertRC(response, 422)
        self.assertJE(response, 'author', ['Author not found.'])

    def test_update_with_foreignkey(self):
        response = self.client.put(
            f'/api/books/{self.author1_book2.pk}', {
                'name': 'The Two Towers, Deluxe Edition',
                'pub_date': '1954-11-11',
            })

        self.assertRC(response, 200)
        self.assertJE(response, 'name', 'The Two Towers, Deluxe Edition')
        self.assertJE(response, 'author.pk', self.author1.pk)
        self.assertJE(response, 'pub_date', '1954-11-11')

        response = self.client.put(
            f'/api/books/{self.author1_book2.pk}', {
                'name': 'The Man in the High Castle',
                'author': self.author2.pk,
                'author_id': self.author3.pk,  # must be ignored
                'pub_date': '1962-10-01',
            })

        self.assertRC(response, 200)
        self.assertJE(response, 'name', 'The Man in the High Castle')
        self.assertJE(response, 'author.pk', self.author2.pk)
        self.assertJE(response, 'pub_date', '1962-10-01')

        response = self.client.put(
            f'/api/books/{self.author1_book2.pk}', {
                'name': 'A Scanner Darkly',
                'author': {
                    'pk': self.author2.pk,
                    'resource_name': 'Philip Kindred Dick'},
                'pub_date': '1977-01-01',
            })

        self.assertRC(response, 200)
        self.assertJE(response, 'name', 'A Scanner Darkly')
        self.assertJE(response, 'author.pk', self.author2.pk)
        self.assertJE(response, 'pub_date', '1977-01-01')

    def test_update_with_wrong_key_and_foreignkey(self):
        response = self.client.put(
            '/api/books/99999', {
                'name': 'The Two Towers',
                'pub_date': '1954-11-11'})
        self.assertRC(response, 404)

        response = self.client.put(
            f'/api/books/{self.author1_book2.pk}', {
                'name': 'The Two Towers',
                'author': 999999,
                'pub_date': '1954-11-11'})
        self.assertRC(response, 422)
        self.assertJE(response, 'author', ['Author not found.'])

    def test_delete_with_foreignkey(self):
        response = self.client.delete(
            f'/api/authors/{self.author1.pk}')

        self.assertRC(response, 400)
        self.author1_book2.refresh_from_db()

    def test_create_validation(self):
        response = self.client.post(
            '/api/books', {
                'name': '',
                'pub_date': '1954-07-29',
                'created_at': '1954-07-29',
            })

        self.assertRC(response, 422)
        self.assertJE(response, 'name',
                      ['This field cannot be blank.'])
        self.assertJE(response, 'author',
                      ['This field cannot be null.'])

    def test_update_validation(self):
        response = self.client.put(
            f'/api/books/{self.author1_book2.pk}', {
                'name': '',
                'pub_date': '1954-11-11',
            })

        self.assertRC(response, 422)
        self.assertJE(response, 'name',
                      ['This field cannot be blank.'])

    def test_create_related_field(self):
        response = self.client.post(
            '/api/books', {
                'name': 'The Fellowship of the Ring, Deluxe Edition',
                'author': self.author1.pk,
                'author__last_name': "Teulkien",
                'pub_date': '1954-07-29',
                'created_at': '1954-07-29',
            })
        self.assertRC(response, 200)
        self.assertJE(
            response, 'name', 'The Fellowship of the Ring, Deluxe Edition')
        self.assertJE(response, 'author.pk', self.author1.pk)
        self.assertJE(response, 'pub_date', '1954-07-29')
        self.assertNJE(response, 'created_at', '1954-07-29')
        self.author1.refresh_from_db()
        self.assertEqual(self.author1.last_name, "Tolkien")

    def test_update_related_field(self):
        response = self.client.put(
            f'/api/books/{self.author1_book2.pk}', {
                'name': 'The Two Towers, Deluxe Edition',
                'author__last_name': "Teulkien",
            })
        self.assertRC(response, 200)
        self.assertJE(response, 'name', 'The Two Towers, Deluxe Edition')
        self.assertJE(response, 'author.pk', self.author1.pk)
        self.author1.refresh_from_db()
        self.assertEqual(self.author1.last_name, "Tolkien")

    def test_custom_repr(self):
        book_type = BookType.objects.create(
            name="Epic Fantasy",
            slug="epic-fantasy",
        )
        self.author1_book2.type = book_type
        self.author1_book2.save()

        response = self.client.get(f'/api/books/{self.author1_book2.pk}')
        self.assertRC(response, 200)
        self.assertJE(response, 'type.resource_name', book_type.name)
        self.assertJE(response, 'type.resource_slug', book_type.slug)

        response = self.client.get(f'/api/book-types/{book_type.pk}')
        self.assertRC(response, 200)
        self.assertJE(response, 'resource_name', book_type.name)
        self.assertJE(response, 'resource_slug', book_type.slug)
        self.assertJE(response, 'name', book_type.name)
        self.assertJE(response, 'slug', book_type.slug)

    @override_settings(
        STORAGE_S3_AWS_REGION="fake-region",
        STORAGE_S3_AWS_ACCESS_KEY="FAKE",
        STORAGE_S3_AWS_SECRET_KEY="FAKE-SECRET",
        STORAGE_S3_AWS_S3_BUCKET="dragonfly.fake",
        STORAGE_S3_AWS_GET_URL_EXPIRE=300,
        STORAGE_S3_AWS_PUT_URL_EXPIRE=300)
    @patch("boto3.client", MagicMock(return_value=MockBoto3Client()))
    def test_media_field(self):
        response = self.client.get(
            f'/api/books/{self.author1_book1.pk}/cover/upload-url/'
            'cover.png?content-type=image/png')
        self.assertRC(response, 200)
        self.assertJE(response, 'file.key', "Book/1/cover.png")
        self.assertJE(response, 'file.name', "cover.png")
        self.assertJE(
            response, 'url', "http://dragonfly.fake/Book/1/cover.png")

        response = self.client.put(f'/api/books/{self.author1_book1.pk}', dict(
            cover=response.json_content['file']))
        self.assertRC(response, 200)
        self.assertJE(response, 'cover.key', "Book/1/cover.png")
        self.assertJE(response, 'cover.name', "cover.png")
        self.assertJE(response, 'cover.content-length', 1000)
        self.assertJE(response, 'cover.content-type', "image/png")

        response = self.client.get(
            f'/api/books/{self.author1_book1.pk}/cover')
        self.assertRC(response, 200)
        self.assertJE(
            response, 'url', "http://dragonfly.fake/Book/1/cover.png")

        response = self.client.get(
            f'/api/books/{self.author1_book1.pk}/cover?redirect=false')
        self.assertRC(response, 200)
        self.assertJE(
            response, 'url', "http://dragonfly.fake/Book/1/cover.png")

        response = self.client.get(
            f'/api/books/{self.author1_book1.pk}/cover?redirect')
        self.assertRedirects(
            response, "http://dragonfly.fake/Book/1/cover.png",
            fetch_redirect_response=False)

        with patch.object(
                MockBoto3Client, 'delete_object',
                return_value=None) as mock_delete:
            response = self.client.delete(
                f'/api/books/{self.author1_book1.pk}')
            mock_delete.assert_called_with(
                Bucket='dragonfly.fake',
                Key=f'Book/{self.author1_book1.pk}/cover.png')

    def test_annotate_meta_service(self):
        response = self.client.get('/api/authors-annotate/meta')
        self.assertRC(response, 200)
        self.assertJE(response, 'first_name.type', 'CharField')
        self.assertJE(response, 'first_name.name', 'First Name')
        self.assertJE(response, 'books_count.type', None)
        self.assertJE(response, 'books_count.name', 'books_count')
        self.assertJE(response, 'books_count.readonly.post', True)
        self.assertJE(response, 'books_count.readonly.put', True)
        self.assertJE(response, 'books_count_annotate.type', None)
        self.assertJE(
            response, 'books_count_annotate.name', 'books_count_annotate')
        self.assertJE(response, 'books_count_annotate.readonly.post', True)
        self.assertJE(response, 'books_count_annotate.readonly.put', True)
        self.assertJE(response, 'books_count_prop.type', None)
        self.assertJE(response, 'books_count_prop.name', 'books_count_prop')
        self.assertJE(response, 'books_count_prop.readonly.post', True)
        self.assertJE(response, 'books_count_prop.readonly.put', True)

    def test_annotate_detail_service(self):
        response = self.client.get(f'/api/authors-annotate/{self.author1.pk}')
        self.assertRC(response, 200)
        self.assertJE(response, 'books_count', 4)
        self.assertJE(response, 'books_count_annotate', 4)
        self.assertJE(response, 'books_count_prop', 4)

    def test_annotate_list_service(self):
        response = self.client.get('/api/authors-annotate')
        self.assertRC(response, 200)
        self.assertJE(response, 'meta.count', 4)
        self.assertJE(response, 'items.@0.books_count', 4)
        self.assertJE(response, 'items.@0.books_count_annotate', 4)
        self.assertJE(response, 'items.@0.books_count_prop', 4)
        self.assertJE(response, 'items.@1.books_count', 0)
        self.assertJE(response, 'items.@1.books_count_annotate', 0)
        self.assertJE(response, 'items.@1.books_count_prop', 0)

    def test_annotate_create_service(self):
        response = self.client.post(
            '/api/authors-annotate', {
                'first_name': 'Arthur Charles',
                'last_name': 'Clarke',
                'slug': 'arthur-c-clarke'})
        self.assertRC(response, 200)
        self.assertJE(response, 'books_count', 0)
        self.assertJE(response, 'books_count_annotate', 0)
        self.assertJE(response, 'books_count_prop', 0)

    def test_annotate_update_service(self):
        response = self.client.put(
            f'/api/authors-annotate/{self.author1.pk}', dict(
                first_name='J. R. R.',
                books_count=999,
                books_count_annotate=999,
                books_count_prop=999))

        self.assertRC(response, 200)
        self.assertJE(response, 'first_name', 'J. R. R.')
        self.assertJE(response, 'books_count', 4)
        self.assertJE(response, 'books_count_annotate', 4)
        self.assertJE(response, 'books_count_prop', 4)
        self.author1.refresh_from_db()
        self.assertEqual(self.author1.first_name, 'J. R. R.')

    def test_fields_props_meta_service(self):
        response = self.client.get('/api/authors-fields-props/meta')
        self.assertRC(response, 200)
        self.assertJE(response, 'first_name.type', 'CharField')
        self.assertJE(response, 'first_name.name', 'First Name')
        self.assertJE(response, 'books_count.type', 'IntegerField')
        self.assertJE(response, 'books_count.name', 'Books Count')
        self.assertJE(response, 'books_count.readonly.post', True)
        self.assertJE(response, 'books_count.readonly.put', True)
        self.assertJE(response, 'books_count_annotate.type', 'IntegerField')
        self.assertJE(
            response, 'books_count_annotate.name', 'Books Count (annotate)')
        self.assertJE(response, 'books_count_annotate.readonly.post', True)
        self.assertJE(response, 'books_count_annotate.readonly.put', True)
        self.assertJE(response, 'books_count_prop.type', 'IntegerField')
        self.assertJE(
            response, 'books_count_prop.name', 'Books Count (property)')
        self.assertJE(response, 'books_count_prop.readonly.post', True)
        self.assertJE(response, 'books_count_prop.readonly.put', True)

    def test_fields_props_detail_service(self):
        response = self.client.get(
            f'/api/authors-fields-props/{self.author1.pk}')
        self.assertRC(response, 200)
        self.assertJE(response, 'books_count', 4)
        self.assertJE(response, 'books_count_annotate', 4)
        self.assertJE(response, 'books_count_prop', 4)

    def test_fields_props_list_service(self):
        response = self.client.get('/api/authors-fields-props')
        self.assertRC(response, 200)
        self.assertJE(response, 'meta.count', 4)
        self.assertJE(response, 'items.@0.books_count', 4)
        self.assertJE(response, 'items.@0.books_count_annotate', 4)
        self.assertJE(response, 'items.@0.books_count_prop', 4)
        self.assertJE(response, 'items.@1.books_count', 0)
        self.assertJE(response, 'items.@1.books_count_annotate', 0)
        self.assertJE(response, 'items.@1.books_count_prop', 0)

    def test_fields_props_create_service(self):
        response = self.client.post(
            '/api/authors-fields-props', {
                'first_name': 'Arthur Charles',
                'last_name': 'Clarke',
                'slug': 'arthur-c-clarke'})
        self.assertRC(response, 200)
        self.assertJE(response, 'books_count', 0)
        self.assertJE(response, 'books_count_annotate', 0)
        self.assertJE(response, 'books_count_prop', 0)

    def test_fields_props_update_service(self):
        response = self.client.put(
            f'/api/authors-fields-props/{self.author1.pk}', dict(
                first_name='J. R. R.',
                books_count=999,
                books_count_annotate=999,
                books_count_prop=999))

        self.assertRC(response, 200)
        self.assertJE(response, 'first_name', 'J. R. R.')
        self.assertJE(response, 'books_count', 4)
        self.assertJE(response, 'books_count_annotate', 4)
        self.assertJE(response, 'books_count_prop', 4)
        self.author1.refresh_from_db()
        self.assertEqual(self.author1.first_name, 'J. R. R.')

    def test_alias_field(self):
        response = self.client.get(
            f'/api/books-custom-author/{self.author3_book1.pk}')
        self.assertRC(response, 200)
        self.assertJE(response, 'book_name', "The Caves of Steel")
        self.assertJE(response, 'author_last_name', "Asimov")

        response = self.client.get(
            f'/api/books-custom-author?author={self.author3.pk}')
        self.assertRC(response, 200)
        self.assertJE(response, 'items.@0.author_last_name', "Asimov")
        self.assertJEExists(response, 'items.@0.book_name')

        response = self.client.post(
            '/api/books-custom-author', dict(
                author=self.author3.pk,
                book_name="A New Book",
                pub_date='2020-01-01'
            ))
        new_book_pk = response.json_content['pk']
        self.assertRC(response, 200)
        self.assertJE(response, 'book_name', "A New Book")
        self.assertJE(response, 'author_last_name', "Asimov")

        response = self.client.put(
            f'/api/books-custom-author/{new_book_pk}', dict(
                book_name="A New Book UPDATED"))
        self.assertRC(response, 200)
        self.assertJE(response, 'book_name', "A New Book UPDATED")
        self.assertJE(response, 'author_last_name', "Asimov")
