import uuid
from django.core.exceptions import NON_FIELD_ERRORS, ValidationError
from django.forms.utils import ErrorList
from django.forms.widgets import Media
from django.test import TestCase
from django.utils.html import format_html

from altstreamfield.blocks.core import Block, BoundBlock, UnknownBlock
from altstreamfield.blocks.fields import CharField
from altstreamfield.blocks.streamblock import StreamBlock, StreamBlockField, StreamBlockValidationError, StreamValue
from altstreamfield.blocks.structblock import StructBlock


class TestStructBlock(StructBlock):
    value = CharField()

    def __repr__(self):
        return '<TestStructBlock>'

    def render_basic(self, value, context=None):
        return format_html(
            '<div class="{}">{}</div>',
            self.__class__.__name__.lower(),
            value["value"],
        )


class TestingStreamBlock(StreamBlock):
    test = TestStructBlock()

    class Media:
        js = ['testing.js']


simple_value = [
    {
        "id":"a71848c8-b773-4ca1-b764-97f439da27ab",
        "type":"TestStructBlock",
        "value":{"value":"test"}
    }
]

class TestStreamValue(TestCase):

    def test_can_create(self):
        StreamValue(TestingStreamBlock(), [])
        StreamValue(TestingStreamBlock(), simple_value)
        StreamValue(TestingStreamBlock(), simple_value[0])

    def test_can_find_block_by_name(self):
        value = StreamValue(
            TestingStreamBlock(),
            [{
                "id": "2042b810-1d85-41cc-92bb-b056e36f47e9",
                "type": "test",
                "value": {"value": "some value"},
            }]
        )
        self.assertIsInstance(value[0], BoundBlock)
        self.assertIsInstance(value[0].block, TestStructBlock)

    def test_get_item(self):
        value = StreamValue(TestingStreamBlock(), simple_value)
        first_item = value[0]
        self.assertIsInstance(first_item, StreamValue.StreamChild)
        self.assertEqual(first_item.id, simple_value[0]['id'])

    def test_get_item_when_streamchild(self):
        block = TestStructBlock()
        child = StreamValue.StreamChild(block, block.to_python({'value': {"value": "some value"}}), id="2042b810-1d85-41cc-92bb-b056e36f47e9")
        value = StreamValue(TestingStreamBlock(), [child])
        self.assertIs(value[0], child)

    def test_get_item_bad_data(self):
        '''If we have some bad data in the raw value then we need to throw an error.'''
        value = StreamValue(TestingStreamBlock(), ["one"])
        with self.assertRaises(ValueError):
            value[0]

    def test_get_item_with_unknown_blocktype(self):
        value = StreamValue(TestingStreamBlock(), [{
            "id": str(uuid.uuid4()),
            "type": "MissingStructBlock",
            "value": {"one": 1, "two": 2}
        }])
        self.assertIsInstance(value[0].block, UnknownBlock)

    def test_get_item_with_missing_type(self):
        value = StreamValue(TestingStreamBlock(), [{
            "id": str(uuid.uuid4()),
            "value": {"one": "One", "two": 2}
        }])
        self.assertIsInstance(value[0].block, UnknownBlock)

    def test_get_item_with_missing_value(self):
        value = StreamValue(TestingStreamBlock(), [{
            "id": str(uuid.uuid4()),
            "type": "TestStructBlock",
        }])
        self.assertIsInstance(value[0].block, TestStructBlock)

    def test_get_item_without_dict_value(self):
        value = StreamValue(TestingStreamBlock(), [{
            "id": str(uuid.uuid4()),
            "type": "TestStructBlock",
            "value": "not a dict"
        }])
        self.assertIsInstance(value[0].block, TestStructBlock)

    def test_to_json(self):
        value = StreamValue(TestingStreamBlock(), simple_value)
        self.assertEqual(
            value.to_json(),
            [{
                "id":"a71848c8-b773-4ca1-b764-97f439da27ab",
                "type":"TestStructBlock",
                "value":{"value":"test"}
            }]
        )

    def test_len(self):
        value = StreamValue(TestingStreamBlock(), [])
        self.assertEqual(len(value), 0)

        value = StreamValue(TestingStreamBlock(), simple_value)
        self.assertEqual(len(value), 1)

    def test_repr(self):
        value = StreamValue(TestingStreamBlock(), [])
        self.assertEqual(repr(value), '[]')

        value = StreamValue(TestingStreamBlock(), simple_value)
        self.assertEqual(repr(value), "[<StreamChild id=a71848c8-b773-4ca1-b764-97f439da27ab block=<TestStructBlock> value=StructValue([('value', 'test')])>]")

    def test_str_html(self):
        value = StreamValue(TestingStreamBlock(), [])
        self.assertEqual(str(value), '')

        value = StreamValue(TestingStreamBlock(), simple_value)
        self.assertEqual(str(value), '<div class="block-TestStructBlock"><div class="teststructblock">test</div></div>')

    def test_render_as_block(self):
        value = StreamValue(TestingStreamBlock(), [])
        self.assertEqual(value.render_as_block(), '')

        value = StreamValue(TestingStreamBlock(), simple_value)
        self.assertEqual(value.render_as_block(), '<div class="block-TestStructBlock"><div class="teststructblock">test</div></div>')


class TestStreamBlockValidationError(TestCase):
    def test_init(self):
        error = StreamBlockValidationError()
        self.assertEqual(error.message, 'Validation error in StreamBlock')
        self.assertEqual(error.params, {})

        error = StreamBlockValidationError({"test": "error"})
        self.assertEqual(error.message, 'Validation error in StreamBlock')
        self.assertEqual(error.params, {"test": "error"})

        error = StreamBlockValidationError({"test": "error"}, {"non-field": "error"})
        self.assertEqual(error.message, 'Validation error in StreamBlock')
        self.assertEqual(error.params, {"test": "error", NON_FIELD_ERRORS: {"non-field": "error"}})


class TestStreamBlock(TestCase):

    def test_get_default(self):
        block = TestingStreamBlock()
        default_value = block.get_default()
        self.assertIsInstance(default_value, StreamValue)
        self.assertEqual(default_value.stream_data, [])

    def test_sorted_child_blocks(self):
        block = TestingStreamBlock()
        children = block.sorted_child_blocks()
        self.assertIsInstance(children[0], TestStructBlock)

        class T1Block(Block):
            class Meta:
                group = "Two"

        class T2Block(Block):
            class Meta:
                group = "One"

        class T3Block(Block):
            class Meta:
                group = "One"

        class TSBlock(StreamBlock):
            one = T1Block()
            two = T2Block()
            three = T3Block()

        block = TSBlock()
        children = block.sorted_child_blocks()
        self.assertIsInstance(children[0], T2Block)
        self.assertIsInstance(children[1], T3Block)
        self.assertIsInstance(children[2], T1Block)

    def test_named_child_blocks(self):
        block = TestingStreamBlock()
        self.assertEqual(len(block.named_blocks), 1)
        self.assertIn('test', block.named_blocks)

    def test_media(self):
        '''Ensure that media of this StreamBlock instance is merged with media of all child_blocks.'''

        class T1Block(Block):
            class Media:
                js = ['t1block.js']

        class T2Block(Block):
            class Media:
                js = ['t2block.js']

        class TSBlock(StreamBlock):
            one = T1Block()
            two = T2Block()

            class Media:
                js = ['tsblock.js']

        block = TSBlock()
        media = block.media
        self.assertIsInstance(media, Media)
        self.assertIn('t1block.js', media._js)
        self.assertIn('t2block.js', media._js)
        self.assertIn('tsblock.js', media._js)

    def test_required(self):
        class TSReqBlock(StreamBlock):
            class Meta:
                required = True

        self.assertTrue(TSReqBlock().required)

        class TSBlock(StreamBlock):
            class Meta:
                required = False

        self.assertFalse(TSBlock().required)

        # ensuring that the default is True
        self.assertTrue(TestingStreamBlock().required)

    def test_clean(self):
        block = TestingStreamBlock()
        value = block.clean(simple_value)
        self.assertEqual(value[0].value["value"], "test")
        self.assertEqual(value[0].value.block, block.child_blocks['TestStructBlock'])

        with self.assertRaises(ValidationError):
            block.clean([{"type": "TestStructBlock", "value": {"value": ""}}])

    def test_clean_with_too_many(self):
        class TooManyStreamBlock(StreamBlock):
            test = TestStructBlock()

            class Meta:
                max_num = 1

        block = TooManyStreamBlock()
        with self.assertRaises(ValidationError):
            block.clean([
                {
                    "id":str(uuid.uuid4()),
                    "type":"TestStructBlock",
                    "value":{"value":"test"}
                },
                {
                    "id":str(uuid.uuid4()),
                    "type":"TestStructBlock",
                    "value":{"value":"test"}
                }
            ])

    def test_clean_with_too_few(self):
        class TooFewStreamBlock(StreamBlock):
            test = TestStructBlock()

            class Meta:
                min_num = 2

        block = TooFewStreamBlock()
        with self.assertRaises(ValidationError):
            block.clean([
                {
                    "id":str(uuid.uuid4()),
                    "type":"TestStructBlock",
                    "value":{"value":"test"}
                }
            ])

    def test_clean_required(self):
        block = TestingStreamBlock()
        with self.assertRaises(ValidationError):
            value = block.clean([])

    def test_clean_with_block_counts(self):
        class T1StructBlock(StructBlock):
            name = CharField()

        class BlockCounts(StreamBlock):
            one = TestStructBlock()
            two = T1StructBlock()

            class Meta:
                block_counts = {
                    'TestStructBlock': {
                        'min_num': 1,
                        'max_num': 3,
                    },
                    'T1StructBlock': {
                        'min_num': 2,
                        'max_num': 3,
                    }
                }

        block = BlockCounts()

        with self.assertRaises(ValidationError):
            block.clean([
                {
                    "id":str(uuid.uuid4()),
                    "type":"TestStructBlock",
                    "value":{"value":"test"}
                }
            ])

        with self.assertRaises(ValidationError):
            block.clean([
                {
                    "id":str(uuid.uuid4()),
                    "type":"TestStructBlock",
                    "value":{"value":"test"}
                },
                {
                    "id":str(uuid.uuid4()),
                    "type":"TestStructBlock",
                    "value":{"value":"test"}
                },
                {
                    "id":str(uuid.uuid4()),
                    "type":"TestStructBlock",
                    "value":{"value":"test"}
                },
                {
                    "id":str(uuid.uuid4()),
                    "type":"TestStructBlock",
                    "value":{"value":"test"}
                },
                {
                    "id":str(uuid.uuid4()),
                    "type":"T1StructBlock",
                    "value":{"name":"test"}
                },
                {
                    "id":str(uuid.uuid4()),
                    "type":"T1StructBlock",
                    "value":{"name":"test"}
                }
            ])

        block.clean([
                {
                    "id":str(uuid.uuid4()),
                    "type":"TestStructBlock",
                    "value":{"value":"test"}
                },
                {
                    "id":str(uuid.uuid4()),
                    "type":"TestStructBlock",
                    "value":{"value":"test"}
                },
                {
                    "id":str(uuid.uuid4()),
                    "type":"T1StructBlock",
                    "value":{"name":"test"}
                },
                {
                    "id":str(uuid.uuid4()),
                    "type":"T1StructBlock",
                    "value":{"name":"test"}
                }
            ])

    def test_can_validate_with_errors(self):
        block = TestingStreamBlock()
        block.validate(StreamValue(block, simple_value))

        with self.assertRaises(ValidationError):
            block.validate(StreamValue(block, simple_value), {0: ErrorList([ValidationError('test error')])})

    def test_to_json(self):
        block = TestingStreamBlock()
        self.assertEqual(block.to_json(None), [])
        self.assertEqual(block.to_json(StreamValue(block, simple_value)), simple_value)
        with self.assertRaises(AttributeError):
            block.to_json("bad type")

    def test_render_basic(self):
        # see above: TestStreamValue.test_str_html
        pass

    def test_render_edit_js(self):
        block = TestingStreamBlock()
        script = block.render_edit_js()
        lines = [x for x in script.split('\n') if x != '']
        self.assertEqual(lines[0], 'var TestStructBlock = asf.create_structblock("TestStructBlock", [{"name": "value", "field_type": "CharField", "args": {"name": "value", "label": "Value", "required": true, "help_text": "", "strip": true, "min_length": null, "max_length": null}}]);')
        self.assertEqual(lines[1], 'TestStructBlock.icon = "placeholder";')
        self.assertEqual(lines[2], 'TestStructBlock.group = "";')
        self.assertEqual(lines[3], 'var TestingStreamBlock = asf.create_streamblock("TestingStreamBlock", { "TestStructBlock": TestStructBlock });')
        self.assertEqual(lines[4], 'TestingStreamBlock.icon = "placeholder";')
        self.assertEqual(lines[5], 'TestingStreamBlock.group = "";')

    def test_render_edit_js_with_label(self):
        class LabelTestingStreamBlock(StreamBlock):
            test = TestStructBlock()

            class Media:
                js = ['testing.js']

            class Meta:
                label = 'Label Test'

        block = LabelTestingStreamBlock()
        script = block.render_edit_js()
        lines = [x for x in script.split('\n') if x != '']
        self.assertEqual(lines[0], 'var TestStructBlock = asf.create_structblock("TestStructBlock", [{"name": "value", "field_type": "CharField", "args": {"name": "value", "label": "Value", "required": true, "help_text": "", "strip": true, "min_length": null, "max_length": null}}]);')
        self.assertEqual(lines[1], 'TestStructBlock.icon = "placeholder";')
        self.assertEqual(lines[2], 'TestStructBlock.group = "";')
        self.assertEqual(lines[3], 'var LabelTestingStreamBlock = asf.create_streamblock("LabelTestingStreamBlock", { "TestStructBlock": TestStructBlock });')
        self.assertEqual(lines[4], 'LabelTestingStreamBlock.icon = "placeholder";')
        self.assertEqual(lines[5], 'LabelTestingStreamBlock.group = "";')
        self.assertEqual(lines[6], 'LabelTestingStreamBlock.label = "Label Test";')

    def test_render_edit_js_with_group(self):
        class GroupTestingStreamBlock(StreamBlock):
            test = TestStructBlock()

            class Media:
                js = ['testing.js']

            class Meta:
                group = 'Test'

        block = GroupTestingStreamBlock()
        script = block.render_edit_js()
        lines = [x for x in script.split('\n') if x != '']
        self.assertEqual(lines[0], 'var TestStructBlock = asf.create_structblock("TestStructBlock", [{"name": "value", "field_type": "CharField", "args": {"name": "value", "label": "Value", "required": true, "help_text": "", "strip": true, "min_length": null, "max_length": null}}]);')
        self.assertEqual(lines[1], 'TestStructBlock.icon = "placeholder";')
        self.assertEqual(lines[2], 'TestStructBlock.group = "";')
        self.assertEqual(lines[3], 'var GroupTestingStreamBlock = asf.create_streamblock("GroupTestingStreamBlock", { "TestStructBlock": TestStructBlock });')
        self.assertEqual(lines[4], 'GroupTestingStreamBlock.icon = "placeholder";')
        self.assertEqual(lines[5], 'GroupTestingStreamBlock.group = "Test";')



    def test_get_searchable_content(self):
        block = TestingStreamBlock()
        content = block.get_searchable_content(StreamValue(block, simple_value))
        self.assertEqual(len(content), 1)
        self.assertEqual(content, ["test"])

    def test_check(self):
        block = TestingStreamBlock()
        errors = block.check()
        self.assertEqual(len(errors), 0)

        block.child_blocks['test-ing'] = Block()
        block.child_blocks['test-ing'].set_name('test-ing')
        errors = errors = block.check()
        self.assertEqual(len(errors), 1)


class TestStreamBlockField(TestCase):
    def test_init(self):
        f = StreamBlockField(TestingStreamBlock())
        with self.assertRaises(TypeError):
            f = StreamBlockField(None)

    def test_to_python(self):
        f = StreamBlockField(TestingStreamBlock())
        value = f.to_python({"value": simple_value})
        self.assertEqual(len(value), 1)

        value = f.to_python({})
        self.assertEqual(len(value), 0)

        value = f.to_python(simple_value)
        self.assertEqual(len(value), 1)

        with self.assertRaises(ValidationError):
            value = f.to_python(None)

    def test_to_json(self):
        f = StreamBlockField(TestingStreamBlock())
        value = f.to_python(simple_value)
        self.assertEqual(f.to_json(value), {"value": simple_value})

    def test_validate(self):
        f = StreamBlockField(TestingStreamBlock())
        with self.assertRaises(ValidationError):
            f.validate([])

        with self.assertRaises(ValidationError):
            f.validate([{
                "id": str(uuid.uuid4()),
                "type": "TestStructBlock",
                "value": {"value": ""}
            }])

        with self.assertRaises(ValidationError):
            f.validate(None)

        f.validate(simple_value)

    def test_get_args(self):
        f = StreamBlockField(TestingStreamBlock())
        args = f.get_args()
        self.assertIn('block', args)
        self.assertEqual(args['block'], 'TestingStreamBlock')

    def test_get_dependencies(self):
        block = TestingStreamBlock()
        f = StreamBlockField(block)
        self.assertEqual(f.get_dependencies(), {'': block})

    def test_media(self):
        '''Ensure that the field collects the media the block it contains.'''
        block = TestingStreamBlock()
        f = StreamBlockField(block)
        self.assertIn('testing.js', f.media._js)