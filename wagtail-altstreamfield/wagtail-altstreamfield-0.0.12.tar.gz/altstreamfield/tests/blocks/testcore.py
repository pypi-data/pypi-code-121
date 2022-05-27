from django.test import TestCase

from altstreamfield.blocks.core import *
from altstreamfield.blocks.fields import CharField

class TestBaseBlock(TestCase):

    def test_basic_case(self):
        class ParentBlock(metaclass=BaseBlock):

            class Meta:
                icon = 'placeholder'
                title = 'Test Title'

        class ChildBlock(ParentBlock):

            class Meta:
                icon = 'image'

        self.assertEqual(ChildBlock._meta_class.__name__, 'ChildBlockMeta')
        self.assertEqual(ChildBlock._meta_class.icon, 'image')
        self.assertEqual(ChildBlock._meta_class.title, 'Test Title')
        self.assertEqual(ParentBlock._meta_class.__name__, 'ParentBlockMeta')
        self.assertEqual(ParentBlock._meta_class.icon, 'placeholder')
        self.assertEqual(ParentBlock._meta_class.title, 'Test Title')


class TestDeclarativeFieldsMetaclass(TestCase):

    def test_basic_case(self):
        class BasicBlock(metaclass=DeclarativeFieldsMetaclass):
            first_name = CharField()
            last_name = CharField()
            middle_initial = CharField(max_length=1)

        self.assertEqual(len(BasicBlock.declared_fields), 3)

        class ChildBlock(BasicBlock):
            age = CharField()

        self.assertEqual(len(ChildBlock.declared_fields), 4)


class TestDeclarativeSubBlocksMetaclass(TestCase):

    def test_basic_case(self):
        class NameBlock(Block):
            pass

        class AgeBlock(Block):
            pass

        class ContainerBlock(metaclass=DeclarativeSubBlocksMetaclass):
            name = NameBlock()
            age = AgeBlock()

        self.assertEqual(len(ContainerBlock.base_blocks), 2)


class TestBoundBlock(TestCase):
    def test_init(self):
        b = BoundBlock(Block(), 10)
        self.assertIsInstance(b.block, Block)
        self.assertEqual(b.value, 10)
        self.assertIsNone(b.errors)

    def test_render(self):
        b = BoundBlock(Block(), 10)
        self.assertEqual(b.render(), '10')

    def test_render_as_block(self):
        b = BoundBlock(Block(), 10)
        self.assertEqual(b.render_as_block(), '10')

    def test_str(self):
        b = BoundBlock(Block(), 10)
        self.assertEqual(str(b), '10')


class TestBlock(TestCase):
    def test_init(self):
        temp_counter = Block.creation_counter
        b = Block()
        self.assertEqual(Block.creation_counter, temp_counter + 1)
        self.assertEqual(b.creation_counter, temp_counter)
        self.assertTrue(hasattr(b, 'meta'))
        self.assertEqual(b.label, '')
        self.assertEqual(b.child_blocks, {})

    def test_js_type(self):
        b = Block()
        self.assertEqual(b.js_type, 'Block')

    def test_set_name(self):
        b = Block()
        self.assertEqual(b.name, '')
        b.set_name('test')
        self.assertEqual(b.name, 'test')

    def test_clean(self):
        b = Block()
        self.assertEqual(b.clean(1), 1)
        self.assertEqual(b.clean('test'), 'test')

    def test_to_python(self):
        b = Block()
        self.assertEqual(b.to_python('value'), 'value')

    def test_to_json(self):
        b = Block()
        self.assertEqual(b.to_json('test'), 'test')

    def test_get_context(self):
        b = Block()
        self.assertEqual(b.get_context(10), {'self': 10, 'value': 10})

    def test_render(self):
        b = Block()
        self.assertEqual(b.render(10), '10')

        class TemplateBlock(Block):
            class Meta:
                template = 'altstreamfield/blocks/blocktest.html'

        b = TemplateBlock()
        self.assertEqual(b.render('test'), '<div>test</div>')

        self.assertEqual(b.render('test', {'test': 'context'}), '<div>test</div>')

    def test_render_edit_js(self):
        b = Block()
        self.assertEqual(b.render_edit_js(), '')

    def test_render_edit_js_prerequisites(self):
        b = Block()
        self.assertEqual(b.render_edit_js_prerequisites(), '')

        class SubBlock(Block):
            def render_edit_js(self, rendered_blocks=None):
                return 'var SubBlock = null;'

        class DependentBlock(Block, metaclass=DeclarativeSubBlocksMetaclass):
            block = SubBlock()

            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.child_blocks = self.base_blocks.copy()

        b = DependentBlock()
        self.assertEqual(b.render_edit_js_prerequisites(), 'var SubBlock = null;')

    def test_bind(self):
        b = Block()
        bound_block = b.bind(10)
        self.assertIsInstance(bound_block, BoundBlock)
        self.assertEqual(bound_block.block, b)
        self.assertEqual(bound_block.value, 10)

    def test_check(self):
        b = Block()
        self.assertEqual(b.check(), [])

    def test_check_name(self):
        b = Block()
        b.set_name('test')
        self.assertEqual(len(b._check_name()), 0)

        b.set_name('test ing')
        errors = b._check_name()
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0].msg, "Block name 'test ing' is invalid")

        b.set_name('')
        errors = b._check_name()
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0].msg, "Block name '' is invalid")

        b.set_name('test-ing')
        errors = b._check_name()
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0].msg, "Block name 'test-ing' is invalid")

        b.set_name('1testing')
        errors = b._check_name()
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0].msg, "Block name '1testing' is invalid")

        b.set_name('1-test ing')
        errors = b._check_name()
        self.assertEqual(len(errors), 3)
        self.assertEqual(errors[0].msg, "Block name '1-test ing' is invalid")

    def test_required(self):
        b = Block()
        self.assertFalse(b.required)


class TestUnknownBlock(TestCase):
    def test_init(self):
        b = UnknownBlock()
        self.assertEqual(b.name, 'unknown')
