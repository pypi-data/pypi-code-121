import copy

from django.core.exceptions import ValidationError
from django.core import validators
from django.forms import Media
from django.test import TestCase

from altstreamfield.blocks.fields import *


class MockValidator:
    def __init__(self):
        self.call_count = 0

    def __call__(self, value):
        self.call_count += 1


class InvalidMockValidator(MockValidator):
    def __call__(self, value):
        super().__call__(value)
        raise ValidationError('Mock invalid error.', 'invalid')


class TestField(TestCase):

    def test_init(self):
        f = Field(required=False, validators=(), help_text='testing help')
        self.assertFalse(f.required)
        self.assertEqual(len(f.validators), 0)
        self.assertEqual(f.help_text, 'testing help')

    def test_init_with_label(self):
        f = Field(label="Test Field")
        self.assertEqual(f.label, 'Test Field')

        f = Field()
        self.assertEqual(f.name, '')
        self.assertEqual(f.label, '')
        f.name = 'test'
        self.assertEqual(f.label, 'Test')

    def test_init_with_default(self):
        f = Field()
        self.assertIsNone(f.default)

        f = Field(default='test')
        self.assertEqual(f.default, 'test')

        f = Field(default=2)
        self.assertEqual(f.default, 2)

    def test_deepcopy(self):
        '''Ensure that all properties that might not be duplicated are duplicated.'''
        f = Field(help_text="Ensuring deep copy works.")
        f2 = copy.deepcopy(f)
        self.assertIsNot(f, f2)
        self.assertIsNot(f.error_messages, f2.error_messages)
        self.assertIsNot(f.validators, f2.validators)

    def test_get_args(self):
        '''Ensure that all arguments needed for JS are rendered out.'''
        f = Field(help_text='Some help.')
        args = f.get_args()
        for key in Field.args_list:
            if key != 'default':
                self.assertIn(key, args)

    def test_get_args_with_default(self):
        f = Field(help_text='Some help.', default='test')
        args = f.get_args()
        for key in Field.args_list:
            self.assertIn(key, args)

    def test_dependencies(self):
        '''Ensure that dependencies returns a dict.'''
        f = Field()
        self.assertIsInstance(f.get_dependencies(), dict)

    def test_media(self):
        f = Field()
        self.assertIsNone(f.media)

    def test_to_python(self):
        f = Field()
        vals = [
            'test',
            10,
            10.233,
            True,
        ]
        for val in vals:
            self.assertEqual(f.to_python(val), val)

    def test_to_json(self):
        f = Field()
        vals = [
            'test',
            10,
            10.233,
            True,
        ]
        for val in vals:
            self.assertEqual(f.to_json(val), val)

    def test_validate(self):
        '''Ensure that required validation runs appropriately.'''
        f = Field(required=True)
        with self.assertRaises(ValidationError):
            f.validate(None)
        with self.assertRaises(ValidationError):
            f.validate('')

        f = Field(required=False)
        f.validate(None)
        f.validate('')

    def test_run_validators(self):
        f = Field(validators=(
            MockValidator(),
            InvalidMockValidator()
        ))
        with self.assertRaises(ValidationError):
            f.run_validators('test')

        for validator in f.validators:
            self.assertEqual(validator.call_count, 1)

    def test_run_validators_with_empty_value(self):
        f = Field(validators=(InvalidMockValidator(),))
        self.assertIsNone(f.run_validators(None))
        for validator in f.validators:
            self.assertEqual(validator.call_count, 0)

    def test_run_validators_custom_error_messages(self):
        f = Field(validators=(InvalidMockValidator(),))
        f.error_messages['invalid'] = 'Invalid on Field'
        try:
            f.run_validators('a bad value')
        except ValidationError as ex:
            self.assertEqual(ex.error_list[0].message, 'Invalid on Field')

    def test_clean(self):
        f = Field(validators=(validators.integer_validator,))
        with self.assertRaises(ValidationError):
            f.clean(None)

        with self.assertRaises(ValidationError):
            f.clean('abc')

        self.assertEqual(f.clean('23'), '23')

    def test_check(self):
        f = Field()
        self.assertEqual(f.check(), [])

    def test_check_name(self):
        f = Field()
        self.assertEqual(len(f._check_name('test')), 0)

        errors = f._check_name('test ing')
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0].msg, "Field name 'test ing' is invalid")

        errors = f._check_name('')
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0].msg, "Field name '' is invalid")

        errors = f._check_name('test-ing')
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0].msg, "Field name 'test-ing' is invalid")

        errors = f._check_name('1testing')
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0].msg, "Field name '1testing' is invalid")

        errors = f._check_name('1-test ing')
        self.assertEqual(len(errors), 3)
        self.assertEqual(errors[0].msg, "Field name '1-test ing' is invalid")

    def test_name(self):
        f = Field()
        self.assertEqual(f.name, '')
        f.name = 'Orange Blossom'
        self.assertEqual(f.name, 'Orange Blossom')

    def test_label(self):
        f = Field()
        self.assertEqual(f.label, '')

        f.name = 'green_teas'
        self.assertEqual(f.label, 'Green teas')

        f.name = 'greenTeas'
        self.assertEqual(f.label, 'GreenTeas')

        f.label = 'Green Tea Packets'
        self.assertEqual(f.label, 'Green Tea Packets')


class TestCharField(TestCase):

    def test_init(self):
        '''Ensure that we can create the field with the appropriate validators.'''
        f = CharField()
        self.assertEqual(len(f.validators), 1)
        self.assertIsNone(f.max_length)
        self.assertIsNone(f.min_length)
        self.assertTrue(f.strip)
        self.assertTrue(f.required)

        f = CharField(max_length=100, min_length=10)
        self.assertEqual(len(f.validators), 3)
        self.assertEqual(f.max_length, 100)
        self.assertEqual(f.min_length, 10)

        f = CharField(max_length=100)
        self.assertEqual(len(f.validators), 2)

        f = CharField(min_length=100)
        self.assertEqual(len(f.validators), 2)

        with self.assertRaises(ValueError):
            CharField(min_length=100, max_length=10)

    def test_to_python(self):
        f = CharField()
        self.assertEqual(f.to_python('   a value   '), 'a value')
        self.assertEqual(f.to_python(None), '')

    def test_get_searchable_content(self):
        f = CharField()
        self.assertEqual(f.get_searchable_content('this is a test'), ['this is a test'])


class TestReadOnlyCharField(TestCase):
    def test_init(self):
        '''Ensure that we can create the field.'''
        f = ReadOnlyCharField()
        self.assertFalse(f.required)

    def test_to_python(self):
        f = ReadOnlyCharField()
        self.assertEqual(f.to_python('test'), 'test')
        self.assertEqual(f.to_python('  some spaces  '), 'some spaces')
        self.assertEqual(f.to_python(2), '2')
        self.assertEqual(f.to_python(None), '')

    def test_max_min_validators_are_always_excluded(self):
        f = ReadOnlyCharField(max_length=10, min_length=2)
        self.assertEqual(len(f.validators), 1)
        self.assertIsInstance(f.validators[0], validators.ProhibitNullCharactersValidator)

    def test_args_list(self):
        f = ReadOnlyCharField(max_length=10, min_length=2)
        self.assertEqual(
            set(f.args_list),
            set([
                'strip',
                'name',
                'label',
                'help_text',
                'default',
            ])
        )


class TestIntegerField(TestCase):

    def test_init(self):
        f = IntegerField()
        self.assertIsNone(f.min_value)
        self.assertIsNone(f.max_value)
        self.assertEqual(len(f.validators), 0)

        f = IntegerField(min_value=0, max_value=10)
        self.assertEqual(f.min_value, 0)
        self.assertEqual(f.max_value, 10)
        self.assertEqual(len(f.validators), 2)

        f = IntegerField(min_value=1)
        self.assertEqual(f.min_value, 1)
        self.assertEqual(len(f.validators), 1)

        f = IntegerField(max_value=10)
        self.assertEqual(f.max_value, 10)
        self.assertEqual(len(f.validators), 1)

        with self.assertRaises(ValueError):
            IntegerField(min_value=10, max_value=1)

    def test_to_python(self):
        f = IntegerField()
        self.assertEqual(f.to_python(10), 10)
        self.assertEqual(f.to_python('12'), 12)
        self.assertEqual(f.to_python(''), None)
        with self.assertRaises(ValidationError):
            f.to_python('abc')


class TestBooleanField(TestCase):
    def test_to_python(self):
        f = BooleanField()
        self.assertTrue(f.to_python(True))
        self.assertTrue(f.to_python(1))
        self.assertTrue(f.to_python('1'))
        self.assertTrue(f.to_python('true'))

        self.assertFalse(f.to_python(False))
        self.assertFalse(f.to_python(0))
        self.assertFalse(f.to_python('0'))
        self.assertFalse(f.to_python('false'))

        self.assertFalse(f.to_python(None))


class TestChoiceField(TestCase):
    def test_init(self):
        choices = [('one', 'One'), ('two', 'Two')]
        f = ChoiceField(choices=choices)
        self.assertEqual(f.choices, choices)

        def choices_func():
            return choices

        f = ChoiceField(choices=choices_func)
        for idx, item in enumerate(f.choices):
            self.assertEqual(item, choices[idx])

    def test_deepcopy(self):
        choices = [('one', 'One'), ('two', 'Two')]
        f = ChoiceField(choices=choices)
        copy.deepcopy(f)
        self.assertIsNot(f.choices, choices)

    def test_to_python(self):
        choices = [('one', 'One'), ('two', 'Two')]
        f = ChoiceField(choices=choices)
        self.assertEqual(f.to_python('one'), 'one')
        self.assertEqual(f.to_python(None), '')
        self.assertEqual(f.to_python('bad'), 'bad') # this is allowed here because validation should be taking care of invalid values.

    def test_validate(self):
        choices = [('one', 'One'), ('two', 'Two')]
        f = ChoiceField(choices=choices)
        f.validate('one')
        with self.assertRaises(ValidationError):
            f.validate('three')

        choices = [
            ['Numbers', [
                ('one', 'One'),
                ('two', 'Two'),
            ]],
            ['Colors', [
                ('red', 'Red'),
                ('orange', 'Orange'),
            ]]
        ]
        f = ChoiceField(choices=choices)
        f.validate('one')
        f.validate('red')
        with self.assertRaises(ValidationError):
            f.validate('four')


class TestRichTextField(TestCase):
    def test_media(self):
        f = RichTextField()
        self.assertIsInstance(f.media, Media)


class MockManager:
    def get(self, **kwargs):
        if kwargs['pk'] == 1:
            return MockModel(1)
        else:
            from django.core.exceptions import ObjectDoesNotExist
            raise ObjectDoesNotExist()

class MockModel:
    objects = MockManager()

    def __init__(self, pk):
        self.pk = pk
        self.id = pk

class TestModelChooserField(TestCase):
    def test_to_python(self):
        f = ModelChooserField()
        f.model = MockModel

        self.assertIsNone(f.to_python(None))
        self.assertIsInstance(f.to_python(1), MockModel)
        with self.assertRaises(ValidationError):
            f.to_python(2)

    def test_to_json(self):
        f = ModelChooserField()
        f.model = MockModel

        self.assertEqual(f.to_json(MockModel(1)), 1)
        self.assertEqual(f.to_json(3), 3)
        self.assertEqual(f.to_json('test'), None)


class TestDocumentChooserField(TestCase):
    def test_media(self):
        f = DocumentChooserField()
        self.assertIsInstance(f.media, Media)


class TestImageChooserField(TestCase):
    def test_model(self):
        from wagtail.images import get_image_model
        f = ImageChooserField()
        self.assertEqual(f.model, get_image_model())

    def test_media(self):
        f = ImageChooserField()
        self.assertIsInstance(f.media, Media)


class TestPageChooserField(TestCase):
    def test_model(self):
        from wagtail.core.models import Page
        f = PageChooserField()
        self.assertEqual(f.model, Page)

    def test_media(self):
        f = PageChooserField()
        self.assertIsInstance(f.media, Media)

    def test_limit_page_types(self):
        '''Need to make sure that the PageChooserField can specify a type of page to choose.'''
        from wagtail.core.models import Page
        f = PageChooserField(target_model='wagtailcore.Page')
        self.assertEqual(f.target_model, Page)

    def test_validate(self):
        from wagtail.core.models import Page

        class TestPage(Page):
            pass

        p = Page(title='Test')

        field = PageChooserField(target_model='wagtailcore.Page')
        field.validate(p)

        with self.assertRaises(ValidationError):
            field = PageChooserField(target_model=TestPage)
            field.validate(p)

        p = Page.objects.get(id=2) # this is a root page (apparently)
        field = PageChooserField(target_model='wagtailcore.Page')
        with self.assertRaises(ValidationError):
            field.validate(p)

        field = PageChooserField(can_choose_root=True)
        field.validate(p)

    def test_get_args(self):
        '''We need to make sure that the target_model is converted to a string that can be recognized by `resolve_model_string()`.'''
        from wagtail.core.models import Page
        field = PageChooserField(target_model='wagtailcore.Page')
        args = field.get_args()
        self.assertEqual(args['target_model'], 'wagtailcore.Page')
