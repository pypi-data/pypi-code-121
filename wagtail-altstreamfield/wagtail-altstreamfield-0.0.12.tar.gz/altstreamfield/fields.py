import json
import uuid

from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.forms import Field, HiddenInput
from django.utils.translation import ugettext as _

from .blocks.streamblock import StreamBlock, StreamValue
from .utils import get_class_media


class StreamBlockInput(HiddenInput):
    '''A Django Form Widget for collecting StreamBlock data.'''
    template_name = 'altstreamfield/widgets/blockinput.html'

    def __init__(self, block, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not isinstance(block, StreamBlock):
            raise TypeError('"block" must be of type StreamBlock.')
        self.block = block

    def get_context(self, name, value, attrs):
        if isinstance(value, StreamValue):
            value = json.dumps(
                {
                    "id": str(uuid.uuid4()),
                    "type": self.block.__class__.__name__,
                    "value": value.to_json(),
                },
                cls=DjangoJSONEncoder
            )
        context = super().get_context(name, value, attrs)
        context['widget']['block'] = self.block
        return context

    @property
    def media(self):
        media = get_class_media(super().media, self)
        return media + self.block.media

    class Media:
        js = [
            'altstreamfield/altstreamfield.js'
        ]
        css = {
            'all': (
                'altstreamfield/streamfield.css',
                'wagtailadmin/css/panels/streamfield.css',
            ),
        }


class StreamBlockField(Field):
    '''A Django Form Field for collecting StreamBlock data.'''
    def __init__(self, block=None, **kwargs):
        if not isinstance(block, StreamBlock):
            raise TypeError("StreamBlockField requires a block that is an instance of StreamBlock.")
        self.block = block

        if 'widget' not in kwargs:
            kwargs['widget'] = StreamBlockInput(block)

        super().__init__(**kwargs)

    def to_python(self, value):
        try:
            value = json.loads(value)
            return json.dumps(value['value'], cls=DjangoJSONEncoder)
        except json.JSONDecodeError:
            return '[]'

'''
# This does not appear to be necessary for us.
# https://github.com/django/django/blob/64200c14e0072ba0ffef86da46b2ea82fd1e019a/django/db/models/fields/subclassing.py#L31-L44
class Creator:
    """
    A placeholder class that provides a way to set the attribute on the model.
    """
    def __init__(self, field):
        self.field = field

    def __get__(self, obj, type=None):
        if obj is None:
            return self
        return obj.__dict__[self.field.name]

    def __set__(self, obj, value):
        obj.__dict__[self.field.name] = self.field.to_python(value)
'''


class AltStreamField(models.Field):
    '''An alternate Django Model Field implementation of a Wagtail StreamField.'''
    def __init__(self, block_type, **kwargs):
        super().__init__(**kwargs)
        if isinstance(block_type, StreamBlock):
            self.stream_block = block_type
        elif issubclass(block_type, StreamBlock):
            self.stream_block = block_type(required=not self.blank)
        else:
            raise TypeError('"block_type" must be an instance of a StreamBlock or a class that inherits from StreamBlock.')

    def get_internal_type(self):
        return 'TextField'

    def get_panel(self):
        from wagtail.admin.edit_handlers import FieldPanel
        return FieldPanel

    def deconstruct(self):
        name, path, _, kwargs = super().deconstruct()
        block_type = self.stream_block.__class__
        args = [block_type]
        return name, path, args, kwargs

    def to_python(self, value):
        if value is None or value == '':
            return StreamValue(self.stream_block, [])
        elif isinstance(value, StreamValue):
            return value
        elif isinstance(value, str):
            try:
                unpacked_value = json.loads(value)
            except ValueError:
                raise ValidationError("Could not parse the value as a JSON string.")

            if unpacked_value is None:
                # Literal string value is null.
                return StreamValue(self.stream_block, [])
            elif isinstance(unpacked_value, (list, tuple)):
                return StreamValue(self.stream_block, unpacked_value)
            else:
                return StreamValue(self.stream_block, unpacked_value['value'])
        else:
            raise ValidationError("Unexpected value '{}' in AltStreamField.".format(value))

    def get_prep_value(self, value):
        return json.dumps(self.stream_block.to_json(value), cls=DjangoJSONEncoder)

    def from_db_value(self, value, expression, connection):
        return self.to_python(value)

    def formfield(self, **kwargs):
        defaults = {'form_class': StreamBlockField, 'block': self.stream_block}
        defaults.update(kwargs)
        return super().formfield(**defaults)

    def value_to_string(self, obj):
        value = self.value_from_object(obj)
        return self.get_prep_value(value)

    def get_searchable_content(self, value):
        return self.stream_block.get_searchable_content(value)

    def check(self, **kwargs):
        errors = super().check(**kwargs)
        errors.extend(self.stream_block.check(field=self, **kwargs))
        return errors

    #def contribute_to_class(self, cls, name, **kwargs):
    #    super().contribute_to_class(cls, name, **kwargs)

        # Add Creator descriptor to allow the field to be set from a list or a
        # JSON string.
    #    setattr(cls, self.name, Creator(self))