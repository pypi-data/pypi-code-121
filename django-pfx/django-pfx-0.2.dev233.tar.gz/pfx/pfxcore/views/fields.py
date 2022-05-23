import logging
import operator
from datetime import date

from django.db import models
from django.db.models.constants import LOOKUP_SEP
from django.utils.formats import date_format
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _

from pfx.pfxcore import fields as pfx_fields
from pfx.pfxcore.shortcuts import get_object

logger = logging.getLogger(__name__)


def setifnone(kwargs, k, default):
    if kwargs.get(k) is None:
        kwargs[k] = default


class FieldType:
    CharField = "CharField"
    TextField = "TextField"
    BooleanField = "BooleanField"
    IntegerField = "IntegerField"
    FloatField = "FloatField"
    DateField = "DateField"
    DateTimeField = "DateTimeField"
    MinutesDurationField = "MinutesDurationField"
    MediaField = "MediaField"
    ModelObject = "ModelObject"
    ModelObjectList = "ModelObjectList"
    JsonObject = "JsonObject"

    MODEL_FIELD_BINDING = [
        (pfx_fields.MinutesDurationField, MinutesDurationField),
        (models.BooleanField, BooleanField),
        (models.IntegerField, IntegerField),
        (models.FloatField, FloatField),
        (models.DateTimeField, DateTimeField),
        (models.DateField, DateField),
        (models.TextField, TextField),
        (models.CharField, CharField),
        (models.ForeignObject, ModelObject),
        (models.ForeignObjectRel, ModelObjectList),
        (models.JSONField, JsonObject)
    ]

    @classmethod
    def register_binding(cls, field_class, field_type):
        cls.MODEL_FIELD_BINDING.insert(0, (field_class, field_type))

    @classmethod
    def from_model_field(cls, field_class):
        for k, v in FieldType.MODEL_FIELD_BINDING:
            if issubclass(field_class, k):
                return v


class ViewField:
    def __init__(
            self, name, verbose_name=None, alias=None, field_type=None,
            readonly=False, readonly_create=False, readonly_update=False,
            choices=None, json_repr=None):
        self.name = name
        self.alias = alias or name
        self.readonly_create = readonly or readonly_create
        self.readonly_update = readonly or readonly_update
        self.verbose_name = verbose_name or name
        self.field_type = field_type
        self.choices = dict(choices or [])
        self.select = False
        self.json_repr = json_repr

    def is_readonly(self, created=False):
        return self.readonly_create if created else self.readonly_update

    def meta(self):
        res = dict(type=self.field_type, name=self.verbose_name)
        if self.choices:
            res['choices'] = [
                dict(label=_(v), value=k) for k, v in self.choices.items()]
        res['readonly'] = dict(
            post=self.readonly_create,
            put=self.readonly_update)
        return res

    def get_value(self, obj):
        dotstr = self.name.replace(LOOKUP_SEP, '.')
        if '.' in dotstr:
            path, name = dotstr.rsplit('.', 1)
            obj = operator.attrgetter(path)(obj)
        else:
            name = self.name
        return getattr(obj, name)

    def _json_repr(self, value):
        if not value:
            return None
        if self.json_repr:
            return self.json_repr(value)
        return value.json_repr()

    def to_json(self, obj, format_date):
        value = self.get_value(obj)
        if format_date and isinstance(value, date):
            return dict(
                value=value,
                formatted=date_format(
                    value, format='SHORT_DATE_FORMAT', use_l10n=True))
        if self.field_type == FieldType.MinutesDurationField:
            return pfx_fields.MinutesDurationField.to_json(value)
        if self.field_type == FieldType.ModelObject:
            return self._json_repr(value)
        if self.field_type == FieldType.ModelObjectList:
            return [self._json_repr(o) for o in value.all()]
        if self.choices:
            if value in self.choices:
                return dict(value=value, label=_(self.choices[value]))
            else:
                return None
        return value

    @classmethod
    def from_property(cls, name, prop, **kwargs):
        if hasattr(prop, 'fget'):
            verbose_name = getattr(
                prop.fget, 'short_description', prop.fget.__name__)
            field_type = getattr(prop.fget, 'field_type', None)
        else:
            verbose_name = (
                hasattr(prop, 'name') and prop.name or str(prop))
            field_type = None
        setifnone(kwargs, 'verbose_name', verbose_name)
        setifnone(kwargs, 'field_type', field_type)
        kwargs['readonly'] = True
        return ViewField(name, **kwargs)

    @classmethod
    def from_model_field(cls, name, field, **kwargs):
        setifnone(kwargs, 'verbose_name', cls._get_model_verbose_name(field))
        setifnone(
            kwargs, 'field_type', FieldType.from_model_field(field.__class__))
        return ViewModelField(
            name, model_field=field, **kwargs)

    @classmethod
    def from_name(cls, model, name, **kwargs):
        attr_model, attr_name = cls._resolve_lookup(model, name)
        try:
            attr = getattr(attr_model, attr_name)
        except AttributeError:
            kwargs['readonly'] = True
            return ViewField(name, **kwargs)
        if isinstance(attr, (property, cached_property)):
            return cls.from_property(name, attr, **kwargs)
        field = attr_model._meta.get_field(attr_name)
        if LOOKUP_SEP in name:
            kwargs['readonly'] = True
        return cls.from_model_field(name, field, **kwargs)

    @classmethod
    def _resolve_lookup(cls, model, name):
        path = name.split(LOOKUP_SEP)
        path, name = path[:-1], path[-1]
        for e in path:
            model = model._meta.get_field(e).related_model
        return model, name

    @classmethod
    def _get_model_verbose_name(cls, field):
        if hasattr(field, 'verbose_name'):
            return field.verbose_name
        elif hasattr(field, 'related_model'):
            if (hasattr(field, 'multiple') and field.multiple and
                    hasattr(field.related_model._meta, 'verbose_name_plural')):
                return field.related_model._meta.verbose_name_plural
            elif hasattr(field.related_model._meta, 'verbose_name'):
                return field.related_model._meta.verbose_name
        return field.name


class ViewModelField(ViewField):
    def __init__(
            self, name, model_field=None, select=None, **kwargs):
        super().__init__(name, **kwargs)
        self.model_field = model_field
        if select is None:
            self.select = self.field_type == FieldType.ModelObject
        else:
            self.select = select
        self.choices = self.choices or dict(
            hasattr(model_field, 'choices') and model_field.choices or [])
        if not self.field_type:
            self.readonly = True

    def meta(self):
        res = super().meta()
        res['required'] = not (
            getattr(self.model_field, 'null', False) or
            getattr(self.model_field, 'blank', False))
        return res

    def to_model_value(self, value, get_related_queryset):
        field = self.model_field
        if self.field_type == FieldType.ModelObject:
            pk = (value['pk'] if isinstance(value, dict) and 'pk' in value
                  else value)
            value = pk and get_object(
                get_related_queryset(self.model_field.related_model),
                related_field=self.name, pk=pk) or None
        if hasattr(field, 'choices') and field.choices:
            value = (value['value']
                     if isinstance(value, dict) and 'value' in value
                     else value)
        elif self.field_type == FieldType.DateField:
            value = (value['value']
                     if isinstance(value, dict) and 'value' in value
                     else value)
        elif self.field_type == FieldType.IntegerField:
            value = value if value != '' else None
        elif self.field_type == FieldType.FloatField:
            value = value if value != '' else None
        elif self.field_type == FieldType.MinutesDurationField:
            if value is None:
                pass
            elif value == '':
                value = None
            elif (isinstance(value, dict) and 'human_format' in value):
                value = value['human_format']
        return field.name, value


class VF:
    def __init__(
            self, name, verbose_name=None, field_type=None, alias=None,
            readonly=False, readonly_create=False, readonly_update=False,
            choices=None, select=None, json_repr=None):
        self.kwargs = dict(
            name=name, verbose_name=verbose_name, field_type=field_type,
            alias=alias,
            readonly=readonly, readonly_create=readonly_create,
            readonly_update=readonly_update, choices=choices,
            json_repr=json_repr
        )

    def to_field(self, model):
        return ViewField.from_name(model, **self.kwargs)
