import json
import uuid

from django.core.exceptions import ValidationError
from django.test import TestCase
from wagtail.admin.edit_handlers import FieldPanel

from ..blocks.fields import CharField
from ..blocks.streamblock import StreamBlock, StreamValue
from ..blocks.structblock import StructBlock
from ..fields import AltStreamField, StreamBlockField, StreamBlockInput

class TestStructBlock(StructBlock):
    value = CharField()

    class Media:
        js = ['struct.js']


class TestStreamBlock(StreamBlock):
    test = TestStructBlock()

    class Media:
        js = ['stream.js']


simple_value = {
    "id":"a8b5e919-8518-49ec-9302-fa33fa266d65",
    "type":"TestStreamBlock",
    "value":[
        {
            "id":"a71848c8-b773-4ca1-b764-97f439da27ab",
            "type":"TestStructBlock",
            "value":{"value":"test"}
        }
    ]
}


class TestBlockInput(TestCase):
    def test_init(self):
        block = TestStreamBlock()
        widget = StreamBlockInput(block)
        self.assertIs(widget.block, block)

        with self.assertRaises(TypeError):
            StreamBlockInput(TestStructBlock())

    def test_get_context(self):
        block = TestStreamBlock()
        widget = StreamBlockInput(block)
        context = widget.get_context(
            "field_name",
            StreamValue(block, [
                {
                    "id":"a71848c8-b773-4ca1-b764-97f439da27ab",
                    "type":"TestStructBlock",
                    "value":{"value":"test"}
                }
            ]),
            {},
        )
        self.assertIs(context['widget']['block'], block)
        self.assertIsInstance(context['widget']['value'], str)

    def test_media(self):
        '''Make sure we include the block media as well.'''
        widget = StreamBlockInput(TestStreamBlock())
        media = widget.media
        self.assertIn('struct.js', media._js)
        self.assertIn('stream.js', media._js)
        self.assertIn('altstreamfield/altstreamfield.js', media._js)



class TestBlockField(TestCase):
    def test_init(self):
        block = TestStreamBlock()
        field = StreamBlockField(block)
        self.assertIs(field.block, block)

        with self.assertRaises(TypeError):
            StreamBlockField(None)

    def test_clean(self):
        block = TestStreamBlock()
        field = StreamBlockField(block)

        value = field.clean(json.dumps(simple_value))
        self.assertEqual(value, json.dumps(simple_value['value']))

    def test_clean_bad_json(self):
        block = TestStreamBlock()
        field = StreamBlockField(block)

        self.assertEqual(field.clean('{garbage}'), '[]')


class TestAltStreamField(TestCase):

    def test_init(self):
        f = AltStreamField(TestStreamBlock)
        self.assertIsInstance(f.stream_block, TestStreamBlock)

        block = TestStreamBlock()
        f = AltStreamField(block)
        self.assertIs(f.stream_block, block)

        with self.assertRaises(TypeError):
            AltStreamField(TestStructBlock)

    def test_get_internal_type(self):
        self.assertEqual(
            AltStreamField(TestStreamBlock).get_internal_type(),
            'TextField'
        )

    def test_get_panel(self):
        f = AltStreamField(TestStreamBlock)
        self.assertIs(f.get_panel(), FieldPanel)

    def test_deconstruct(self):
        f = AltStreamField(TestStreamBlock)
        name, path, args, kwargs = f.deconstruct()
        self.assertEqual(args, [TestStreamBlock])

    def test_to_python(self):
        f = AltStreamField(TestStreamBlock)

        self.assertEqual(len(f.to_python(None)), 0)

        value = StreamValue(f.stream_block, simple_value['value'])
        self.assertIs(f.to_python(value), value)

        with self.assertRaises(ValidationError):
            f.to_python("{bad JSON}")

        self.assertEqual(len(f.to_python("null")), 0)
        self.assertEqual(len(f.to_python("[]")), 0)

        self.assertIsInstance(f.to_python(json.dumps(simple_value)), StreamValue)

        with self.assertRaises(ValidationError):
            f.to_python(True)

    def test_get_prep_value(self):
        f = AltStreamField(TestStreamBlock)
        value = f.to_python(json.dumps(simple_value))
        self.assertEqual(json.loads(f.get_prep_value(value)), simple_value['value'])

    def test_from_db_value(self):
        f = AltStreamField(TestStreamBlock)
        value = f.from_db_value(json.dumps(simple_value['value']), None, None)
        self.assertIsInstance(value, StreamValue)
        self.assertEqual(len(value), 1)

    def test_formfield(self):
        f = AltStreamField(TestStreamBlock)
        field = f.formfield()
        self.assertIsInstance(field, StreamBlockField)
        self.assertIs(f.stream_block, field.block)

    def test_value_to_string(self):
        f = AltStreamField(TestStreamBlock)
        f.attname = 'test'
        class X:
            test = StreamValue(f.stream_block, simple_value['value'])

        str_val = f.value_to_string(X)
        self.assertEqual(json.loads(str_val), simple_value['value'])

    def test_get_searchable_content(self):
        f = AltStreamField(TestStreamBlock)
        value = f.to_python(json.dumps(simple_value['value']))
        content = f.get_searchable_content(value)
        self.assertEqual(len(content), 1)
        self.assertEqual(content[0], 'test')

    def test_check(self):
        class MockModel:
            class _meta:
                app_label = 'test'
                model_name = 'MockModel'

        f = AltStreamField(TestStreamBlock)
        f.attname = 'test'
        f.name = 'test'
        f.model = MockModel
        self.assertEqual(len(f.check()), 0)