from datetime import date

from django.core.exceptions import FieldDoesNotExist
from django.db import models
from django.test import TestCase

from pfx.pfxcore import fields as pfx_fields
from pfx.pfxcore.test import TestAssertMixin
from pfx.pfxcore.views import VF, FieldType, ViewField, ViewModelField
from tests.models import Author, Book
from tests.views import AuthorRestView


class ViewFieldTest(TestAssertMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = Author.objects.create(
            first_name='Isaac',
            last_name='Asimov',
            science_fiction=True,
            slug='isaac-asimov')
        cls.author_book1 = Book.objects.create(
            author=cls.author,
            name="The Caves of Steel",
            pub_date=date(1954, 1, 1),
            pages=224,
            rating=4.6)
        cls.author_book2 = Book.objects.create(
            author=cls.author,
            name="The Naked Sun",
            pub_date=date(1957, 1, 1))
        cls.author_book3 = Book.objects.create(
            author=cls.author,
            name="The Robots of Dawn",
            pub_date=date(1983, 1, 1))

    def test_field_type_binding(self):
        self.assertEqual(
            FieldType.from_model_field(models.CharField),
            FieldType.CharField)
        self.assertEqual(
            FieldType.from_model_field(models.SlugField),
            FieldType.CharField)
        self.assertEqual(
            FieldType.from_model_field(models.EmailField),
            FieldType.CharField)
        self.assertEqual(
            FieldType.from_model_field(models.TextField),
            FieldType.TextField)
        self.assertEqual(
            FieldType.from_model_field(models.BooleanField),
            FieldType.BooleanField)
        self.assertEqual(
            FieldType.from_model_field(models.IntegerField),
            FieldType.IntegerField)
        self.assertEqual(
            FieldType.from_model_field(models.FloatField),
            FieldType.FloatField)
        self.assertEqual(
            FieldType.from_model_field(models.DateField),
            FieldType.DateField)
        self.assertEqual(
            FieldType.from_model_field(models.DateTimeField),
            FieldType.DateTimeField)
        self.assertEqual(
            FieldType.from_model_field(models.BooleanField),
            FieldType.BooleanField)
        self.assertEqual(
            FieldType.from_model_field(models.BooleanField),
            FieldType.BooleanField)
        self.assertEqual(
            FieldType.from_model_field(models.BooleanField),
            FieldType.BooleanField)
        self.assertEqual(
            FieldType.from_model_field(models.BooleanField),
            FieldType.BooleanField)
        self.assertEqual(
            FieldType.from_model_field(models.ForeignKey),
            FieldType.ModelObject)
        self.assertEqual(
            FieldType.from_model_field(models.ForeignObjectRel),
            FieldType.ModelObjectList)
        self.assertEqual(
            FieldType.from_model_field(models.JSONField),
            FieldType.JsonObject)
        self.assertEqual(
            FieldType.from_model_field(pfx_fields.MinutesDurationField),
            FieldType.MinutesDurationField)
        self.assertEqual(
            FieldType.from_model_field(pfx_fields.MediaField),
            FieldType.JsonObject)

    def test_field_by_name(self):
        field = ViewField.from_name(Book, 'name')
        self.assertTrue(isinstance(field, ViewModelField))
        self.assertEqual(
            field.get_value(self.author_book1), "The Caves of Steel")

        field = ViewField.from_name(Book, 'author__last_name')
        self.assertTrue(isinstance(field, ViewModelField))
        self.assertEqual(field.get_value(self.author_book1), "Asimov")

        # Test with object value
        field = ViewField.from_name(Book, 'author')
        self.assertTrue(isinstance(field, ViewModelField))
        res = field.get_value(self.author_book1)
        self.assertTrue(isinstance(res, Author))
        self.assertEqual(res.pk, self.author.pk)

        # Test with properties
        field = ViewField.from_name(Book, 'author__books_count')
        self.assertFalse(isinstance(field, ViewModelField))
        self.assertTrue(isinstance(field, ViewField))
        self.assertEqual(field.get_value(self.author_book1), 3)

        field = ViewField.from_name(Book, 'author__books_count_prop')
        self.assertFalse(isinstance(field, ViewModelField))
        self.assertTrue(isinstance(field, ViewField))
        self.assertEqual(field.get_value(self.author_book1), 3)

        # Test annotate field
        author = Author.objects.annotate(
            annotate_book_count=models.Count('books')).get(pk=self.author.pk)
        field = ViewField.from_name(Book, 'annotate_book_count')
        self.assertFalse(isinstance(field, ViewModelField))
        self.assertTrue(isinstance(field, ViewField))
        self.assertEqual(field.get_value(author), 3)

        # Check non existent field.
        field = ViewField.from_name(Book, 'doesnotexists')
        with self.assertRaisesRegex(
                AttributeError,
                "'Book' object has no attribute 'doesnotexists'$"):
            field.get_value(self.author_book1)

        # Check non existent object.
        with self.assertRaisesRegex(
                FieldDoesNotExist,
                "Book has no field named 'doesnotexists'$"):
            field = ViewField.from_name(Book, 'doesnotexists__name')

    def test_from_vf(self):
        field = VF('name').to_field(Book)
        self.assertTrue(isinstance(field, ViewModelField))
        self.assertEqual(field.name, 'name')
        self.assertFalse(field.readonly_create)
        self.assertFalse(field.readonly_update)
        self.assertEqual(
            field.get_value(self.author_book1), "The Caves of Steel")

    def test_from_vf_readonly(self):
        field = VF('name', readonly=True).to_field(Book)
        self.assertTrue(isinstance(field, ViewModelField))
        self.assertEqual(field.name, 'name')
        self.assertTrue(field.readonly_create)
        self.assertTrue(field.readonly_update)
        self.assertEqual(
            field.get_value(self.author_book1), "The Caves of Steel")

    def test_from_vf_readonly_create(self):
        field = VF('name', readonly_create=True).to_field(Book)
        self.assertTrue(isinstance(field, ViewModelField))
        self.assertEqual(field.name, 'name')
        self.assertTrue(field.readonly_create)
        self.assertFalse(field.readonly_update)
        self.assertEqual(
            field.get_value(self.author_book1), "The Caves of Steel")

    def test_from_vf_readonly_update(self):
        field = VF('name', readonly_update=True).to_field(Book)
        self.assertTrue(isinstance(field, ViewModelField))
        self.assertEqual(field.name, 'name')
        self.assertFalse(field.readonly_create)
        self.assertTrue(field.readonly_update)
        self.assertEqual(
            field.get_value(self.author_book1), "The Caves of Steel")

    def test_set_value(self):
        view = AuthorRestView()
        view.set_values(self.author_book1, name="The Caves of Steel UPDATED")
        self.assertEqual(
            self.author_book1.name, "The Caves of Steel UPDATED")
