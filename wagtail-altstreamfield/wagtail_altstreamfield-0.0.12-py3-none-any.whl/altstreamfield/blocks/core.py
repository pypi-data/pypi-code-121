import collections
import collections.abc
import copy
import uuid

from django.core import checks, exceptions
from django.forms.widgets import Media, MediaDefiningClass
from django.template.loader import render_to_string
from django.utils.encoding import force_str
from django.utils.functional import cached_property
from django.utils.html import format_html, format_html_join
from django.utils.safestring import mark_safe
from django.utils.text import capfirst

from .fields import *

__all__ = [
    'BaseBlock',
    'DeclarativeFieldsMetaclass',
    'DeclarativeSubBlocksMetaclass',
    'BoundBlock',
    'Block',
    'UnknownBlock',
]

class BaseBlock(MediaDefiningClass):
    '''Note this was taken directly from wagtail's source code because we may need to modify it in the future.'''
    def __new__(mcs, name, bases, attrs):
        meta_class = attrs.pop('Meta', None)

        cls = super(BaseBlock, mcs).__new__(mcs, name, bases, attrs)

        # Get all the Meta classes from all the bases
        meta_class_bases = [meta_class] + [getattr(base, '_meta_class', None)
                                           for base in bases]
        meta_class_bases = tuple(filter(bool, meta_class_bases))
        cls._meta_class = type(str(name + 'Meta'), meta_class_bases, {})

        return cls


class DeclarativeFieldsMetaclass(BaseBlock):
    """Collect Fields declared on the base classes."""
    def __new__(mcs, name, bases, attrs):
        # Collect fields from current class.
        current_fields = []
        for key, value in list(attrs.items()):
            if isinstance(value, Field):
                value.name = key
                current_fields.append((key, value))
                attrs.pop(key)
        attrs['declared_fields'] = dict(current_fields)

        new_class = super(DeclarativeFieldsMetaclass, mcs).__new__(mcs, name, bases, attrs)

        # Walk through the MRO.
        declared_fields = {}
        for base in reversed(new_class.__mro__):
            # Collect fields from base class.
            if hasattr(base, 'declared_fields'):
                declared_fields.update(base.declared_fields)

            # Field shadowing.
            for attr, value in base.__dict__.items():
                if value is None and attr in declared_fields:
                    declared_fields.pop(attr)

        new_class.base_fields = declared_fields
        new_class.declared_fields = declared_fields

        return new_class


class DeclarativeSubBlocksMetaclass(BaseBlock):
    """
    Metaclass that collects sub-blocks declared on the base classes.
    (cheerfully stolen from https://github.com/django/django/blob/master/django/forms/forms.py)
    """
    def __new__(mcs, name, bases, attrs):
        # Collect sub-blocks declared on the current class.
        # These are available on the class as `declared_blocks`
        current_blocks = []
        for key, value in list(attrs.items()):
            if isinstance(value, Block):
                current_blocks.append((value.__class__.__name__, value))
                value.set_name(key)
                attrs.pop(key)
        current_blocks.sort(key=lambda x: x[1].creation_counter)
        attrs['declared_blocks'] = collections.OrderedDict(current_blocks)

        new_class = (super(DeclarativeSubBlocksMetaclass, mcs).__new__(
            mcs, name, bases, attrs))

        # Walk through the MRO, collecting all inherited sub-blocks, to make
        # the combined `base_blocks`.
        base_blocks = collections.OrderedDict()
        for base in reversed(new_class.__mro__):
            # Collect sub-blocks from base class.
            if hasattr(base, 'declared_blocks'):
                base_blocks.update(base.declared_blocks)

            # Field shadowing.
            for attr, value in base.__dict__.items():
                if value is None and attr in base_blocks:
                    base_blocks.pop(attr)
        new_class.base_blocks = base_blocks

        return new_class


class BoundBlock:
    def __init__(self, block, value, errors=None):
        self.block = block
        self.value = value
        self.errors = errors

    def render(self, context=None):
        return self.block.render(self.value, context=context)

    def render_as_block(self, context=None):
        '''TODO: Not sure I need this.'''
        return self.render(context=context)

    def __str__(self):
        return self.block.render(self.value)


class Block(metaclass=BaseBlock):
    '''Base class for all blocks.'''
    name = ''
    creation_counter = 0

    TEMPLATE_VAR = 'value'

    def __init__(self, *args, **kwargs):
        self.meta = self._meta_class()
        self.creation_counter = Block.creation_counter
        Block.creation_counter += 1
        self.label = self.meta.label or ''
        self.child_blocks = {}

    @property
    def js_type(self):
        '''Allows retriving the class name from a template.'''
        return self.__class__.__name__

    def set_name(self, name):
        self.name = name
        if not self.meta.label:
            self.label = capfirst(force_str(name).replace('_', ' '))

    def validate(self, value):
        '''To perform validation, override this method. Throw a ValidationError if validation fails.

        Note: this validation should be done on the value returned from `to_python()`.
        '''
        pass

    def clean(self, value):
        '''Validate value and return a cleaned version or throw a ValidationError if validation fails.'''
        value = self.to_python(value)
        self.validate(value)
        return value

    def to_python(self, value):
        '''Converts a JSON value to a Python version of the value.'''
        return value

    def to_json(self, value):
        '''Converts the Python value to an equivalent JSON value (a value that can be passed to json.dump).'''
        return value

    def get_context(self, value, parent_context=None):
        """
        Return a dict of context variables (derived from the block value and combined with the parent_context)
        to be used as the template context when rendering this value through a template.
        """

        context = parent_context or {}
        context.update({
            'self': value,
            self.TEMPLATE_VAR: value,
        })
        return context

    def get_template(self, context=None):
        """
        Return the template to use for rendering the block if specified on meta class.
        This extraction was added to make dynamic templates possible if you override this method
        """
        return getattr(self.meta, 'template', None)

    def render(self, value, context=None):
        """
        Return a text rendering of 'value', suitable for display on templates. By default, this will
        use a template (with the passed context, supplemented by the result of get_context) if a
        'template' property is specified on the block, and fall back on render_basic otherwise.
        """
        template = self.get_template(context=context)
        if not template:
            return self.render_basic(value, context=context)

        if context is None:
            new_context = self.get_context(value)
        else:
            new_context = self.get_context(value, parent_context=dict(context))

        return mark_safe(render_to_string(template, new_context))

    def render_basic(self, value, context=None):
        """
        Return a text rendering of 'value', suitable for display on templates. render() will fall back on
        this if the block does not define a 'template' property.
        """
        return force_str(value)

    def render_edit_js(self, rendered_blocks=None):
        '''Override this method do render custom JavaScript needed for editing this type of block.'''
        return ''

    def render_edit_js_prerequisites(self, rendered_blocks=None):
        pre_requisites = []
        if rendered_blocks is None:
            rendered_blocks = set()

        for block in self.child_blocks.values():
            if block.__class__ not in rendered_blocks:
                pre_requisites.append(block.render_edit_js(rendered_blocks))
                rendered_blocks.add(block.__class__)

        return "\n".join(pre_requisites)

    def bind(self, value, errors=None):
        return BoundBlock(self, value, errors=errors)

    def check(self, **kwargs):
        """
        Hook for the Django system checks framework -
        returns a list of django.core.checks.Error objects indicating validity errors in the block
        """
        return []

    def _check_name(self):
        """Helper method called as part of the system checks framework, to
        validate that the passed in name is a valid identifier.
        """
        errors = []
        if not self.name:
            errors.append(checks.Error(
                "Block name %r is invalid" % self.name,
                hint="Block name cannot be empty",
                obj=self,
                id='altstreamfield.E001',
            ))

        if ' ' in self.name:
            errors.append(checks.Error(
                "Block name %r is invalid" % self.name,
                hint="Block names cannot contain spaces",
                obj=self,
                id='altstreamfield.E001',
            ))

        if '-' in self.name:
            errors.append(checks.Error(
                "Block name %r is invalid" % self.name,
                "Block names cannot contain dashes",
                obj=self,
                id='altstreamfield.E001',
            ))

        if self.name and self.name[0].isdigit():
            errors.append(checks.Error(
                "Block name %r is invalid" % self.name,
                "Block names cannot begin with a digit",
                obj=self,
                id='altstreamfield.E001',
            ))

        return errors

    @property
    def required(self):
        """
        Flag used to determine whether labels for this block should display a 'required' asterisk.
        False by default, since Block does not provide any validation of its own - it's up to subclasses
        to define what required-ness means.
        """
        return False

    class Meta:
        label = None
        icon = "placeholder"
        classname = None
        group = ''


class UnknownBlock(Block):
    '''This is a block that should be used when the block type cannot be found.'''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = 'unknown'
