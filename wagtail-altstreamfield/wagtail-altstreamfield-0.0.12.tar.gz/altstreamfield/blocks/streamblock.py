import collections
import collections.abc
import json
import uuid

from django.core.exceptions import NON_FIELD_ERRORS, ValidationError
from django.forms.utils import ErrorList
from django.utils.html import format_html_join, mark_safe
from django.utils.translation import ugettext as _

from .core import Block, BoundBlock, DeclarativeSubBlocksMetaclass, UnknownBlock
from .fields import Field
from ..utils import get_class_media

__all__ = [
    'StreamBlock',
    'StreamBlockField',
    'StreamBlockValidationError',
    'StreamValue',
]


class StreamValue(collections.abc.Sequence):
    '''The default value type for a StreamBlock.

    This organizes the sub-blocks into an array and allows for the subblocks to handle their own values.
    '''


    class StreamChild(BoundBlock):
        '''Extends bound block with methods that make sense in the context of
        children of StreamField, but not necessarily elsewhere that BoundBlock
        is used.
        '''

        def __init__(self, *args, **kwargs):
            self.id = kwargs.pop('id')
            super().__init__(*args, **kwargs)

        def __repr__(self):
            return '<StreamChild id={} block={} value={}>'.format(
                self.id,
                repr(self.block),
                repr(self.value),
            )

        @property
        def block_type(self):
            '''Returns the block type of the block.'''
            return self.block.__class__.__name__


    def __init__(self, stream_block, stream_data):
        self.stream_block = stream_block
        self.stream_data = stream_data
        self._bound_blocks = {}
        if not isinstance(self.stream_data, (list, tuple)):
            self.stream_data = [self.stream_data]

    def __getitem__(self, i):
        '''Retrieve a single BoundBlock from this StreamValue's collection of BoundBlocks.'''
        if i not in self._bound_blocks:
            if isinstance(self.stream_data[i], dict):
                block_id = self.stream_data[i].get('id', uuid.uuid4())
                type_name = self.stream_data[i].get('type', 'UnknownBlock')
                value = self.stream_data[i].get('value', {})

                child_block = self._get_block_instance(type_name)
                try:
                    value = child_block.to_python(value)
                except ValidationError:
                    # if we get a validation error here then we should wipe out the data and try to preserve the field as much as possible.
                    value = child_block.to_python({})

                self._bound_blocks[i] = StreamValue.StreamChild(child_block, value, id=block_id)
            elif isinstance(self.stream_data[i], StreamValue.StreamChild):
                self._bound_blocks[i] = self.stream_data[i]
            else:
                raise ValueError('Bad data encountered: ' + repr(self.stream_data[i]))

        return self._bound_blocks[i]

    def _get_block_instance(self, block_type):
        '''Returns the instance of a block of the specified type. If that type
        is not avialable then we return an UnknownBlock instance.
        '''
        if block_type in self.stream_block.child_blocks:
            return self.stream_block.child_blocks[block_type]
        elif block_type in self.stream_block.named_blocks:
            return self.stream_block.named_blocks[block_type]
        else:
            return UnknownBlock()

    def to_json(self):
        '''Convert this StreamValue to a JSON representation.'''
        json_result = []
        for i, stream_data_item in enumerate(self.stream_data):
            child = self[i]
            child.id = child.id or str(uuid.uuid4())
            item = {
                'type': child.block_type,
                'value': child.block.to_json(child.value),
                'id': child.id,
            }

            json_result.append(item)

        return json_result

    def __len__(self):
        '''The number of blocks in this StreamValue.'''
        return len(self.stream_data)

    def __repr__(self):
        return repr(list(self))

    def __str__(self):
        return self.__html__()

    def __html__(self):
        return self.stream_block.render(self)

    def render_as_block(self, context=None):
        return self.stream_block.render(self, context=context)


class StreamBlockValidationError(ValidationError):
    '''Represents an error caused when validating a StreamBlock's value.'''
    def __init__(self, block_errors=None, non_block_errors=None):
        params = {}
        if block_errors:
            params.update(block_errors)
        if non_block_errors:
            params[NON_FIELD_ERRORS] = non_block_errors
        super().__init__(
            'Validation error in StreamBlock', params=params)



class StreamBlock(Block, metaclass=DeclarativeSubBlocksMetaclass):
    '''Represents a stream of sub-blocks.

    This Block type specifies what kinds of blocks that it can contain and then stores those values in a StreamValue.
    '''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.child_blocks = self.base_blocks.copy()
        self.named_blocks = {block.name: block for block in self.child_blocks.values()}
        self.dependencies = [block.__class__ for block in self.child_blocks.values()]

    def get_default(self):
        '''Default values set on StreamBlock should be a list of (type_name,
        value) tuples - we can't use StreamValue directly because that would
        require a reference back to the StreamBlock that hasn't been built yet.
        '''
        return StreamValue(self, self.meta.default)

    def sorted_child_blocks(self):
        '''Child blocks, sorted into their groups.'''
        return sorted(self.child_blocks.values(), key=lambda child_block: child_block.meta.group)

    @property
    def media(self):
        media = get_class_media(super().media, self)

        for b in self.child_blocks.values():
            media += b.media

        return media

    @property
    def required(self):
        return self.meta.required

    def validate(self, value, errors=None):
        '''Performs validation of the StreamBlock.'''
        if errors is None:
            errors = {}
        non_block_errors = ErrorList()

        if self.meta.min_num is not None and self.meta.min_num > len(value):
            non_block_errors.append(ValidationError(
                _('The minimum number of items is %d') % self.meta.min_num
            ))
        elif self.required and len(value) == 0:
            non_block_errors.append(ValidationError(_('This field is required.')))

        if self.meta.max_num is not None and self.meta.max_num < len(value):
            non_block_errors.append(ValidationError(
                _('The maximum number of items is %d') % self.meta.max_num
            ))

        if self.meta.block_counts:
            block_counts = collections.defaultdict(int)
            for item in value:
                block_counts[item.block_type] += 1

            for block_name, min_max in self.meta.block_counts.items():
                block = self.child_blocks[block_name]
                max_num = min_max.get('max_num', None)
                min_num = min_max.get('min_num', None)
                block_count = block_counts[block_name]
                if min_num is not None and min_num > block_count:
                    non_block_errors.append(ValidationError(
                        '{}: {}'.format(block.label, _('The minimum number of items is %d') % min_num)
                    ))
                if max_num is not None and max_num < block_count:
                    non_block_errors.append(ValidationError(
                        '{}: {}'.format(block.label, _('The maximum number of items is %d') % max_num)
                    ))

        if errors or non_block_errors:
            # The message here is arbitrary - outputting error messages is delegated to the child blocks,
            # which only involves the 'params' list
            raise StreamBlockValidationError(block_errors=errors, non_block_errors=non_block_errors)

    def clean(self, value):
        cleaned_data = []
        errors = {}
        value = self.to_python(value)

        # clean all subblock values
        for i, child in enumerate(value):  # child is a StreamChild instance
            try:
                cleaned_data.append(
                    {
                        'type': child.block_type,
                        'value': child.block.clean(child.value),
                        'id': child.id,
                    }
                )
            except ValidationError as e:
                errors[i] = ErrorList([e])

        self.validate(value, errors)

        return StreamValue(self, cleaned_data)

    def to_python(self, value):
        '''Converts the JSON representation to a Python Representation.'''
        return StreamValue(self, value)

    def to_json(self, value):
        if not value:
            return []
        else:
            return value.to_json()

    def render_basic(self, value, context=None):
        '''Very simple rendering of the stream block.'''
        return format_html_join(
            '\n', '<div class="block-{1}">{0}</div>',
            [
                (child.render(context=context), child.block_type)
                for child in value
            ]
        )

    def render_edit_js(self, rendered_blocks=None):
        if rendered_blocks is None:
            rendered_blocks = set()

        definition = [
            self.render_edit_js_prerequisites(rendered_blocks),
            'var {cls_name} = asf.create_streamblock("{cls_name}", {{ {child_blocks} }});'.format(
                cls_name=self.__class__.__name__,
                child_blocks=", ".join(['"{0}": {0}'.format(block.__class__.__name__) for block in self.child_blocks.values()])
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
        '''Gets all searchable content from the child blocks in this StreamBlock.'''
        content = []

        for child in value:
            content.extend(child.block.get_searchable_content(child.value))

        return content

    def check(self, **kwargs):
        errors = super().check(**kwargs)
        for name, child_block in self.child_blocks.items():
            errors.extend(child_block.check(**kwargs))
            errors.extend(child_block._check_name())
        return errors

    class Meta:
        icon = 'placeholder'
        default = []
        required = True
        min_num = None
        max_num = None
        block_counts = {}


class StreamBlockField(Field):
    '''A field that allows for nesting StreamBlocks.'''
    args_list = Field.args_list + [
        'block',
    ]
    default_error_messages = {
        'error': _('General error...'), # TODO: come up with a better message.
    }

    def __init__(self, block, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not isinstance(block, StreamBlock):
            raise TypeError('"block" must be of type StreamBlock.')
        self.block = block

    def to_python(self, value):
        '''Converts the JSON value to an equivalent Python value.'''
        if hasattr(value, 'get'):
            return self.block.to_python(value.get('value', []))
        elif isinstance(value, (list, tuple)):
            return self.block.to_python(value)
        else:
            raise ValidationError('"value" must be a dict like object or a list/tuple.')

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