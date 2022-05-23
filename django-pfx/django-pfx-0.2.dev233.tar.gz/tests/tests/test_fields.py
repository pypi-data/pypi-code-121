from datetime import date, timedelta

from django.core.exceptions import ValidationError
from django.db import connection
from django.test import TestCase

from pfx.pfxcore.fields import MinutesDurationField
from pfx.pfxcore.test import APIClient, TestAssertMixin
from tests.models import Author, Book


class FieldsTest(TestAssertMixin, TestCase):

    def setUp(self):
        self.client = APIClient(default_locale='en')
        with connection.cursor() as cursor:
            cursor.execute("create extension if not exists unaccent;")

    @classmethod
    def setUpTestData(cls):
        cls.author = Author.objects.create(
            first_name='John Ronald Reuel',
            last_name='Tolkien',
            slug='jrr-tolkien')
        cls.book = Book.objects.create(
            author=cls.author,
            name="The Hobbit",
            pub_date=date(1937, 1, 1)
        )

    def test_to_python(self):
        d = MinutesDurationField()
        self.assertIsNone(d.to_python(None))
        self.assertIsNone(d.to_python(''))
        self.assertEqual(d.to_python(0), timedelta(0))
        self.assertEqual(d.to_python('0'), timedelta(0))
        self.assertEqual(
            d.to_python(timedelta(hours=2, minutes=30)),
            timedelta(hours=2, minutes=30))
        self.assertEqual(d.to_python(3), timedelta(hours=3))
        self.assertEqual(d.to_python(2.5), timedelta(hours=2, minutes=30))
        self.assertEqual(d.to_python(0.5), timedelta(minutes=30))
        self.assertEqual(d.to_python("2h 30m"), timedelta(hours=2, minutes=30))
        self.assertEqual(d.to_python("0h 30m"), timedelta(minutes=30))
        self.assertEqual(d.to_python("4:30"), timedelta(hours=4, minutes=30))
        self.assertEqual(d.to_python("0:03"), timedelta(minutes=3))
        self.assertEqual(d.to_python(":03"), timedelta(minutes=3))
        self.assertEqual(d.to_python(":30"), timedelta(minutes=30))
        self.assertEqual(d.to_python("4.5h"), timedelta(hours=4, minutes=30))
        self.assertEqual(d.to_python("4.5"), timedelta(hours=4, minutes=30))
        self.assertEqual(d.to_python("4"), timedelta(hours=4))
        self.assertEqual(d.to_python("4.0"), timedelta(hours=4))
        with self.assertRaises(ValidationError):
            d.to_python(dict(wrong='value'))  # test invalid object type
            d.to_python('a wrong value')

    def test_to_json(self):
        d = MinutesDurationField()
        self.assertIsNone(d.to_json(None))
        self.assertEqual(d.to_json(timedelta(0)), dict(
            minutes=0,
            clock_format='0:00',
            human_format=''))
        self.assertEqual(
            d.to_json(timedelta(hours=2, minutes=30)), dict(
                minutes=150,
                clock_format='2:30',
                human_format='2h\xa030m'))

    def test_minutes_duration_field(self):
        self.book.read_time = timedelta(hours=2, minutes=30)
        self.book.save()
        response = self.client.get(f'/api/books/{self.book.pk}')
        self.assertRC(response, 200)
        self.assertJE(response, 'read_time.minutes', 150)
        self.assertJE(response, 'read_time.clock_format', "2:30")
        self.assertJE(response, 'read_time.human_format', "2h\xa030m")

        response = self.client.put(
            f'/api/books/{self.book.pk}', dict(read_time=""))
        self.assertRC(response, 200)
        self.assertJE(response, 'read_time', None)

        response = self.client.put(
            f'/api/books/{self.book.pk}', dict(read_time=None))
        self.assertRC(response, 200)
        self.assertJE(response, 'read_time', None)

        response = self.client.put(
            f'/api/books/{self.book.pk}', dict(read_time=0))
        self.assertRC(response, 200)
        self.assertJE(response, 'read_time.minutes', 0)
        self.assertJE(response, 'read_time.clock_format', "0:00")
        self.assertJE(response, 'read_time.human_format', "")

        response = self.client.put(
            f'/api/books/{self.book.pk}', dict(read_time="0"))
        self.assertRC(response, 200)
        self.assertJE(response, 'read_time.minutes', 0)
        self.assertJE(response, 'read_time.clock_format', "0:00")
        self.assertJE(response, 'read_time.human_format', "")

        response = self.client.put(
            f'/api/books/{self.book.pk}', dict(read_time="0:00"))
        self.assertRC(response, 200)
        self.assertJE(response, 'read_time.minutes', 0)
        self.assertJE(response, 'read_time.clock_format', "0:00")
        self.assertJE(response, 'read_time.human_format', "")

        response = self.client.put(
            f'/api/books/{self.book.pk}', dict(read_time=2.5))
        self.assertRC(response, 200)
        self.assertJE(response, 'read_time.minutes', 150)
        self.assertJE(response, 'read_time.clock_format', "2:30")
        self.assertJE(response, 'read_time.human_format', "2h\xa030m")

        response = self.client.put(
            f'/api/books/{self.book.pk}', dict(read_time="2.5"))
        self.assertRC(response, 200)
        self.assertJE(response, 'read_time.minutes', 150)
        self.assertJE(response, 'read_time.clock_format', "2:30")
        self.assertJE(response, 'read_time.human_format', "2h\xa030m")

        response = self.client.put(
            f'/api/books/{self.book.pk}', dict(read_time="2.5h"))
        self.assertRC(response, 200)
        self.assertJE(response, 'read_time.minutes', 150)
        self.assertJE(response, 'read_time.clock_format', "2:30")
        self.assertJE(response, 'read_time.human_format', "2h\xa030m")

        response = self.client.put(
            f'/api/books/{self.book.pk}', dict(read_time="2h 30m"))
        self.assertRC(response, 200)
        self.assertJE(response, 'read_time.minutes', 150)
        self.assertJE(response, 'read_time.clock_format', "2:30")
        self.assertJE(response, 'read_time.human_format', "2h\xa030m")

        response = self.client.put(
            f'/api/books/{self.book.pk}', dict(read_time="2:30"))
        self.assertRC(response, 200)
        self.assertJE(response, 'read_time.minutes', 150)
        self.assertJE(response, 'read_time.clock_format', "2:30")
        self.assertJE(response, 'read_time.human_format', "2h\xa030m")

        response = self.client.put(
            f'/api/books/{self.book.pk}', dict(read_time=2))
        self.assertRC(response, 200)
        self.assertJE(response, 'read_time.minutes', 120)
        self.assertJE(response, 'read_time.clock_format', "2:00")
        self.assertJE(response, 'read_time.human_format', "2h")

        response = self.client.put(
            f'/api/books/{self.book.pk}', dict(read_time="2"))
        self.assertRC(response, 200)
        self.assertJE(response, 'read_time.minutes', 120)
        self.assertJE(response, 'read_time.clock_format', "2:00")
        self.assertJE(response, 'read_time.human_format', "2h")

        response = self.client.put(
            f'/api/books/{self.book.pk}', dict(read_time="2h"))
        self.assertRC(response, 200)
        self.assertJE(response, 'read_time.minutes', 120)
        self.assertJE(response, 'read_time.clock_format', "2:00")
        self.assertJE(response, 'read_time.human_format', "2h")

        response = self.client.put(
            f'/api/books/{self.book.pk}', dict(read_time="2:00"))
        self.assertRC(response, 200)
        self.assertJE(response, 'read_time.minutes', 120)
        self.assertJE(response, 'read_time.clock_format', "2:00")
        self.assertJE(response, 'read_time.human_format', "2h")

        response = self.client.put(
            f'/api/books/{self.book.pk}', dict(read_time=0.5))
        self.assertRC(response, 200)
        self.assertJE(response, 'read_time.minutes', 30)
        self.assertJE(response, 'read_time.clock_format', "0:30")
        self.assertJE(response, 'read_time.human_format', "30m")

        response = self.client.put(
            f'/api/books/{self.book.pk}', dict(read_time="0.5"))
        self.assertRC(response, 200)
        self.assertJE(response, 'read_time.minutes', 30)
        self.assertJE(response, 'read_time.clock_format', "0:30")
        self.assertJE(response, 'read_time.human_format', "30m")

        response = self.client.put(
            f'/api/books/{self.book.pk}', dict(read_time="0.5h"))
        self.assertRC(response, 200)
        self.assertJE(response, 'read_time.minutes', 30)
        self.assertJE(response, 'read_time.clock_format', "0:30")
        self.assertJE(response, 'read_time.human_format', "30m")

        response = self.client.put(
            f'/api/books/{self.book.pk}', dict(read_time="30m"))
        self.assertRC(response, 200)
        self.assertJE(response, 'read_time.minutes', 30)
        self.assertJE(response, 'read_time.clock_format', "0:30")
        self.assertJE(response, 'read_time.human_format', "30m")

        response = self.client.put(
            f'/api/books/{self.book.pk}', dict(read_time=":30"))
        self.assertRC(response, 200)
        self.assertJE(response, 'read_time.minutes', 30)
        self.assertJE(response, 'read_time.clock_format', "0:30")
        self.assertJE(response, 'read_time.human_format', "30m")

        response = self.client.put(
            f'/api/books/{self.book.pk}', dict(read_time="INVALID"))
        self.assertRC(response, 422)
        self.assertJE(
            response, 'read_time.@0',
            "Invalid format, it can be a number in hours, “1:05”, “:05”, "
            "“1h 5m”, “1.5h” or “30m”.")
