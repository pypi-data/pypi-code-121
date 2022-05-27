import copy
import re

from django.core import checks, validators
from django.core.exceptions import ValidationError
from django.forms import Media
from django.utils.encoding import force_str
from django.utils.text import capfirst
from django.utils.translation import ugettext as _

from wagtail.core.models import Page, Site
from wagtail.core.utils import resolve_model_string
from wagtail.documents import get_document_model
from wagtail.images import get_image_model

__all__ = [
    'BooleanField',
    'CharField',
    'ChoiceField',
    'DocumentChooserField',
    'Field',
    'ImageChooserField',
    'IntegerField',
    'ModelChooserField',
    'PageChooserField',
    'ReadOnlyCharField',
    'RichTextField',
    'TextField',
]


class Field:
    '''Base class for all fields.'''
    args_list = [
        'name',
        'label',
        'required',
        'help_text',
        'default',
    ]
    empty_values = list(validators.EMPTY_VALUES)
    default_validators = []
    default_error_messages = {
        'required': _('This field is required.'),
    }
    default_value = None

    def __init__(self, required=True, validators=(), help_text='', error_messages=None, label=None, default=None):
        self._required = required
        self._name = ''
        self._label = None
        self._default = None
        self.help_text = help_text
        self.default = default

        if label is not None:
            self.label = label

        messages = {}
        for c in reversed(self.__class__.__mro__):
            messages.update(getattr(c, 'default_error_messages', {}))
        messages.update(error_messages or {})
        self.error_messages = messages

        self.validators = [*self.default_validators, *validators]

    def __deepcopy__(self, memo):
        result = copy.copy(self)
        memo[id(self)] = result
        result.error_messages = self.error_messages.copy()
        result.validators = self.validators[:]
        return result

    def get_args(self):
        '''Returns the arguments needed to reproduce this instance in JavaScript.'''
        args = {}
        for name in self.args_list:
            args[name] = getattr(self, name)

        if 'default' in args:
            if args.get('default', None) is None:
                # do not render a "default" argument if the default value is None.
                del args['default']
            else:
                # we have to convert to JSON to ensure that the output is valid JavaScript
                args['default'] = self.to_json(args['default'])
        return args

    def get_dependencies(self):
        '''If this field depends on any other blocks then override this method and return them here.'''
        return {}

    @property
    def media(self):
        '''Allow the field to pass Media objects out to the `altstreamfield.fields.BlockInput` widget.'''
        return None

    def to_python(self, value):
        '''Converts the JSON value to an equivalent Python value.'''
        return value

    def to_json(self, value):
        '''Converts the Python value to an equivalent JSON value (a value that can be passed to json.dump).'''
        return value

    def validate(self, value):
        '''Does basic validation that cannot be done with validators.

        Override this method to perform custom validation.
        '''
        if value in self.empty_values and self._required:
            raise ValidationError(self.error_messages['required'], code='required')

    def run_validators(self, value):
        '''Runs registered validators against the value and raises a ValidationError if any validators fail.'''
        if value in self.empty_values:
            return
        errors = []
        for v in self.validators:
            try:
                v(value)
            except ValidationError as e:
                if hasattr(e, 'code') and e.code in self.error_messages:
                    e.message = self.error_messages[e.code]
                errors.extend(e.error_list)
        if errors:
            raise ValidationError(errors)

    def clean(self, value):
        value = self.to_python(value)
        self.validate(value)
        self.run_validators(value)
        return value

    def check(self):
        return []

    def _check_name(self, name):
        """Helper method called as part of the system checks framework, to
        validate that the passed in name is a valid identifier.
        """
        errors = []
        if not name:
            errors.append(checks.Error(
                "Field name %r is invalid" % name,
                hint="Field name cannot be empty",
                obj=self,
                id='altstreamfield.E001',
            ))

        if ' ' in name:
            errors.append(checks.Error(
                "Field name %r is invalid" % name,
                hint="Field names cannot contain spaces",
                obj=self,
                id='altstreamfield.E001',
            ))

        if '-' in name:
            errors.append(checks.Error(
                "Field name %r is invalid" % name,
                "Field names cannot contain dashes",
                obj=self,
                id='altstreamfield.E001',
            ))

        if name and name[0].isdigit():
            errors.append(checks.Error(
                "Field name %r is invalid" % name,
                "Field names cannot begin with a digit",
                obj=self,
                id='altstreamfield.E001',
            ))

        return errors

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def label(self):
        if self._label is not None:
            return self._label
        else:
            return capfirst(self._name.replace('_', ' '))

    @label.setter
    def label(self, label):
        self._label = label

    @property
    def default(self):
        return self._default

    @default.setter
    def default(self, default):
        self._default = default

    @property
    def required(self):
        return self._required


class CharField(Field):
    '''Represents a single line of text.'''
    args_list = Field.args_list + [
        'strip',
        'min_length',
        'max_length',
    ]

    def __init__(self, max_length=None, min_length=None, strip=True, **kwargs):
        super().__init__(**kwargs)
        self.strip = strip

        # prevent something dumb.
        if max_length and min_length and max_length < min_length:
            raise ValueError("Cannot have a max_length that is smaller than the min_length.")

        self.max_length = max_length
        self.min_length = min_length

        if max_length is not None:
            self.validators.append(validators.MaxLengthValidator(int(max_length)))
        if min_length is not None:
            self.validators.append(validators.MinLengthValidator(int(min_length)))
        self.validators.append(validators.ProhibitNullCharactersValidator())

    def to_python(self, value):
        '''Ensures that the JSON value is converted to a proper Python string.'''
        if value not in self.empty_values:
            value = str(value)
            if self.strip:
                value = value.strip()
        if value in self.empty_values:
            return ''
        return value

    def get_searchable_content(self, value):
        return [force_str(value)]


class ReadOnlyCharField(CharField):
    '''This is a field that never allows a user to set the value.

    This is useful where the value needs to be controlled by code but the user
    needs to be aware of the value.
    '''
    args_list = [
        item for item in CharField.args_list
        if item not in ['max_length', 'min_length', 'required']
    ]

    def __init__(self, max_length=None, min_length=None, strip=True, **kwargs):
        super().__init__(max_length=None, min_length=None, strip=strip, **kwargs)

    @property
    def required(self):
        '''Read only fields should never be required.'''
        return False


class TextField(CharField):
    '''Represents multiple lines of text.'''
    pass


class IntegerField(Field):
    '''Represents and integer value.'''
    args_list = Field.args_list + [
        'min_value',
        'max_value',
    ]
    default_error_messages = {
        'invalid': _('Enter a whole number.'),
    }
    re_decimal = re.compile(r'\.0*\s*$')

    def __init__(self, min_value=None, max_value=None, **kwargs):
        super().__init__(**kwargs)

        if min_value and max_value and max_value < min_value:
            raise ValueError('Cannot have a max_value that is less than the min_value.')

        self.min_value = min_value
        self.max_value = max_value

        if min_value is not None:
            self.validators.append(validators.MinValueValidator(min_value))
        if max_value is not None:
            self.validators.append(validators.MaxValueValidator(max_value))

    def to_python(self, value):
        '''Validate that int() can be called on the input. Return the result of int() or None for empty values.'''
        value = super().to_python(value)
        if value in self.empty_values:
            return None
        try:
            value = int(self.re_decimal.sub('', str(value)))
        except (ValueError, TypeError):
            raise ValidationError(self.error_messages['invalid'], code='invalid')
        return value


class BooleanField(Field):
    '''Represents a boolean value.'''

    def to_python(self, value):
        if isinstance(value, str) and value.lower() in ('false', '0'):
            value = False
        else:
            value = bool(value)
        return super().to_python(value)


class CallableChoiceIterator:
    def __init__(self, choices_func):
        self.choices_func = choices_func

    def __iter__(self):
        yield from self.choices_func()


class ChoiceField(Field):
    '''Represents a selection from a list of choices.'''
    args_list = Field.args_list + [
        'choices',
    ]
    default_error_messages = {
        'invalid_choice': _('Select a valid choice. %(value)s is not one of the available choices.'),
    }

    def __init__(self, choices=(), **kwargs):
        super().__init__(**kwargs)
        self.choices = choices

    def __deepcopy__(self, memo):
        result = super().__deepcopy__(memo)
        result._choices = copy.deepcopy(self._choices, memo)
        return result

    @property
    def choices(self):
        return self._choices

    @choices.setter
    def choices(self, value):
        if callable(value):
            value = CallableChoiceIterator(value)
        else:
            value = list(value)

        self._choices = value

    def to_python(self, value):
        '''Ensure that the value is a string or empty string.'''
        if value in self.empty_values:
            return ''
        return str(value)

    def validate(self, value):
        '''Custom validation to ensure that the value is in the list of choices.'''
        super().validate(value)
        if value and not self.valid_value(value):
            raise ValidationError(
                self.error_messages['invalid_choice'],
                code='invalid_choice',
                params={'value': value},
            )

    def valid_value(self, value):
        """Check to see if the provided value is a valid choice."""
        text_value = str(value)
        for k, v in self.choices:
            if isinstance(v, (list, tuple)):
                # This is an optgroup, so look inside the group for options
                for k2, v2 in v:
                    if value == k2 or text_value == str(k2):
                        return True
            else:
                if value == k or text_value == str(k):
                    return True
        return False


class RichTextField(Field):
    '''Represents rich text.'''

    @property
    def media(self):
        return Media(
            js=[
                'wagtailadmin/js/draftail.js',
                'wagtailadmin/js/page-chooser-modal.js',
                'wagtaildocs/js/document-chooser-modal.js',
                'wagtailembeds/js/embed-chooser-modal.js',
                'wagtailimages/js/image-chooser-modal.js',
            ],
            css={
                'all': ['wagtailadmin/css/panels/draftail.css']
            }
        )


class ModelChooserField(Field):
    '''Base class for Model based chooser fields.'''
    model = None

    def to_python(self, value):
        '''Converts the JSON value to an equivalent Python value.'''
        if value is None:
            return None

        try:
            return self.model.objects.get(pk=value)
        except:
            raise ValidationError('Document with primary key {} does not exist.'.format(value))

    def to_json(self, value):
        '''Converts the Python value to an equivalent JSON value (a value that can be passed to json.dump).'''
        if isinstance(value, self.model):
            return value.pk
        elif str(value).isdigit():
            return int(value)
        else:
            return None


class DocumentChooserField(ModelChooserField):
    '''Represents a selection of a Wagtail document.'''
    @property
    def model(self):
        return get_document_model()

    @property
    def media(self):
        '''Allow the field to pass Media objects out to the `altstreamfield.fields.BlockInput` widget.'''
        return Media(
            js=['wagtaildocs/js/document-chooser-modal.js',],
            css={
                'all': []
            }
        )


class ImageChooserField(ModelChooserField):
    '''Represents a selection of a Wagtail Image.'''
    @property
    def model(self):
        return get_image_model()

    @property
    def media(self):
        '''Allow the field to pass Media objects out to the `altstreamfield.fields.BlockInput` widget.'''
        return Media(
            js=[
                'wagtailimages/js/image-chooser-modal.js',
            ],
            css={
                'all': []
            }
        )

class PageChooserField(ModelChooserField):
    '''Represents a selection of a Wagtail Page.'''
    args_list = ModelChooserField.args_list + [
        'target_model',
        'can_choose_root',
    ]
    default_error_messages = {
        'invalid-page': _('This page may not be chosen.'),
    }

    def __init__(self, target_model=None, can_choose_root=False, **kwargs):
        super().__init__(**kwargs)
        self._target_model = None
        if target_model:
            self._target_model = target_model

        self.can_choose_root = can_choose_root

    def validate(self, value):
        super().validate(value)

        if value and isinstance(value, Page):
            specific = value.specific
            if self.target_model and not isinstance(specific, self.target_model):
                raise ValidationError(self.error_messages['invalid-page'], code='invalid-page')

            if not self.can_choose_root and Site.objects.filter(root_page=value).exists():
                raise ValidationError(self.error_messages['invalid-page'], code='invalid-page')

    def get_args(self):
        args = super().get_args()
        if 'target_model' in args and args['target_model']:
            args['target_model'] = args['target_model']._meta.label
        return args

    @property
    def target_model(self):
        if isinstance(self._target_model, str):
            return resolve_model_string(self._target_model)
        return self._target_model

    @property
    def model(self):
        return Page

    @property
    def media(self):
        return Media(
            js=[
                'wagtailadmin/js/page-chooser-modal.js',
            ]
        )