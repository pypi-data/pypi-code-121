import collections
import copy
import json

from django.core.exceptions import ValidationError
from django.utils.html import format_html, format_html_join
from django.utils.translation import ugettext as _

from .core import Block, BoundBlock, DeclarativeFieldsMetaclass
from .fields import Field
from ..utils import get_class_media

__all__ = [
    'StructValue',
    'StructBlock',
    'StructBlockField',
]


class StructValue(collections.OrderedDict):
    '''A class that generates a StructBlock value from provided fields.'''

    def __init__(self, block, *args):
        super().__init__(*args)
        self.block = block

    def __html__(self):
        return self.block.render(self)

    def render_as_block(self, context=None):
        return self.block.render(self, context=context)


class StructBlock(Block, metaclass=DeclarativeFieldsMetaclass):
    '''A block that contains a "structure" of data.

    This class describes a Block that can contain a dictionary of values collected by it's fields that are used to render the block in various ways.
    '''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields = copy.deepcopy(self.base_fields)
        for field in self.fields.values():
            self.child_blocks.update(field.get_dependencies())

    @property
    def media(self):
        media = get_class_media(super().media, self)

        for field in self.fields.values():
            field_media = field.media
            if field_media != None:
                media += field_media

        return media

    def check(self, **kwargs):
        errors = super().check(**kwargs)
        for name, field in self.fields.items():
            errors.extend(field._check_name(name))

        return errors

    def clean(self, value):
        '''Cleans all the data of every field and returns the cleaned StructValue instance.'''
        cleaned_data = self._to_struct_value([])
        value = self.to_python(value)

        for name, field in self.fields.items():
            cleaned_data[name] = field.clean(value.get(name))

        return cleaned_data

    def to_python(self, value):
        '''Converts a JSON value in to a Python version of the value, in this case a StructValue.'''
        if not isinstance(value, dict):
            raise ValidationError('"value" must be an instance of a dict.', 'invalid')

        return self._to_struct_value([
            (name, field.to_python(value.get(name, None)))
            for name, field in self.fields.items()
        ])

    def _to_struct_value(self, items):
        '''Builds a struct value from a list of items.

        This allows us to override this in the future for custom StructValue classes.
        '''
        return self.meta.value_class(self, items)

    def to_json(self, value):
        '''Converts the StructValue to a dict for rendering to JSON.'''
        return dict([
            (name, field.to_json(value.get(name, None)))
            for name, field in self.fields.items()
        ])

    def render_basic(self, value, context=None):
        return format_html('<dl>\n{}\n</dl>', format_html_join(
            '\n',
            '    <dt>{}</dt>\n    <dd>{}</dd>',
            [(key, val) for key, val in value.items() if key in self.fields]
        ))

    def render_edit_js(self, rendered_blocks=None):
        '''Override this method do render custom JavaScript needed for editing this type of block.'''
        if rendered_blocks is None:
            rendered_blocks = set()

        fields = []
        for name, field in self.fields.items():
            fields.append(json.dumps({
                "name": name,
                "field_type": field.__class__.__name__,
                "args": field.get_args(),
            }))

        definition = [
            self.render_edit_js_prerequisites(rendered_blocks),
            'var {cls_name} = asf.create_structblock("{cls_name}", [{fields}]);'.format(
                cls_name=self.__class__.__name__,
                fields=",".join(fields),
            ),
            '{cls_name}.icon = "{meta_icon}";'.format(cls_name=self.__class__.__name__, meta_icon=self.meta.icon)
        ]

        if hasattr(self.meta, 'group') and self.meta.group:
            definition.append('{cls_name}.group = "{meta_group}";'.format(cls_name=self.__class__.__name__, meta_group=self.meta.group))
        else:
            definition.append('{cls_name}.group = "";'.format(cls_name=self.__class__.__name__))

        if hasattr(self.meta, 'label') and self.meta.label is not None:
            definition.append('{cls_name}.label = "{meta_label}";'.format(cls_name=self.__class__.__name__, meta_label=self.meta.label))

        return '\n'.join(definition)

    def get_searchable_content(self, value):
        content = []

        for name, field in self.fields.items():
            if hasattr(field, 'get_searchable_content'):
                content.extend(field.get_searchable_content(value.get(name, None)))

        return content

    class Meta:
        default = {}
        value_class = StructValue
        icon = 'placeholder'


class StructBlockField(Field):
    '''A field that allows for nesting StructBlocks.'''
    args_list = Field.args_list + [
        'block',
    ]
    default_error_messages = {
        'error': _('General error...'), # TODO: come up with a better message.
    }

    def __init__(self, block, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not isinstance(block, StructBlock):
            raise TypeError('"block" must be of type StructBlock.')
        self.block = block

    def to_python(self, value):
        '''Converts the JSON value to an equivalent Python value.'''
        if hasattr(value, 'get'):
            if hasattr(value.get('value'), 'get'):
                return self.block.to_python(value.get('value', {}))
            else:
                return self.block.to_python(value)
        else:
            raise ValidationError('"value" must be a dict like object.')

    def to_json(self, value):
        '''Converts the Python value to an equivalent JSON value (a value that can be passed to json.dump).'''
        return {'value': self.block.to_json(value)}

    def validate(self, value):
        '''Does basic validation that cannot be done with validators.

        Override this method to perform custom validation.
        '''
        if value in self.empty_values and self._required:
            raise ValidationError(self.error_messages['required'], code='required')

        self.block.clean(value)

    def get_args(self):
        args = super().get_args()
        args['block'] = self.block.__class__.__name__
        return args

    @property
    def media(self):
        return self.block.media

    def get_dependencies(self):
        '''Returns the dependent blocks as a dictionary.'''
        return {self.name: self.block}
