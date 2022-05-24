# -*- coding: UTF-8 -*-
# Copyright 2022 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

from lino.api import rt, dd, _

from django.db import models
from django.contrib.contenttypes.models import *
from django.utils.text import format_lazy

from django_measurement.models import MeasurementField
from measurement.measures import Distance, Area, Volume, Mass, Time

from lino.modlib.gfks.fields import GenericForeignKey, GenericForeignKeyIdField

from .choicelists import *
from .choicelists import __all__ as CHOICELISTS
from .exceptions import DependencyError

__all__ = ['Weighted', 'Volumed', 'Distanced', 'Zoned', 'Timed', 'Measurable'] + CHOICELISTS

_UNITS = {
    'weight': WeightUnits,
    'volume': VolumeUnits,
    'distance': DistanceUnits,
    'area': AreaUnits,
    'time': TimeUnits
}

MIXINS = {
    'Weighted': {
        'measurement': Mass,
        'verbose_name': _('Weight'),
        'verbose_name_plural': _('Weights'),
        'unit_choices': WeightUnits,
        'default_unit': Mass.STANDARD_UNIT,
        'related_query_name': 'weight'
    },
    'Volumed': {
        'measurement': Volume,
        'verbose_name': _('Volume'),
        'verbose_name_plural': _('Volumes'),
        'unit_choices': VolumeUnits,
        'default_unit': Volume.STANDARD_UNIT,
        'related_query_name': 'volume'
    },
    'Timed': {
        'measurement': Time,
        'verbose_name': _('Time'),
        'verbose_name_plural': _('Times'),
        'unit_choices': TimeUnits,
        'default_unit': Time.STANDARD_UNIT,
        'related_query_name': 'time'
    },
    'Distanced': {
        'measurement': Distance,
        'verbose_name': _('Distance'),
        'verbose_name_plural': _('Distances'),
        'unit_choices': DistanceUnits,
        'default_unit': Distance.STANDARD_UNIT,
        'related_query_name': 'distance'
    },
    'Zoned': {
        'measurement': Area,
        'verbose_name': _('Area'),
        'verbose_name_plural': _('Areas'),
        'unit_choices': AreaUnits,
        'default_unit': Area.STANDARD_UNIT,
        'related_query_name': 'area'
    }
}

class Measurement(dd.Model):
    class Meta:
        abstract = True


for mixin, attrs in MIXINS.items():
    unit_class = attrs.pop('unit_choices')
    unit_default = attrs.pop('default_unit')
    mixins_dict = {

        # needed by django.db.models.base.ModelBase
        # the __module__ info is attacted to a class when creating it by (lower level) C.
        '__module__': Measurement.__dict__.get('__module__'),

        'Meta': type('Meta', (type, ), {
            'abstract': True,
            'verbose_name': attrs.pop('verbose_name'),
            'verbose_name_plural': attrs.pop('verbose_name_plural')
        }),
        'value': MeasurementField(measurement=attrs.pop('measurement')),
        'unit': unit_class.field(default=unit_default)
    }
    locals()[mixin] = type(mixin, (Measurement, ), mixins_dict)

class Measurable(dd.Model):
    """

    Usage
    =====

    When some model inherits from Measurable, the model must define a `unit`
    field like the example below::

        class Potato(Food, Measurable):
            unit = Measurable.units(['weight']).field(null=True, blank=True)

    In the above example, Measurable.units returns a :class:`ChoiceList
    <lino.core.choicelists.ChoiceList>` which in our case has only the units of
    weight measure. If you do NOT pass any value to the Measurable.units it will
    return a ChoiceList that includes all the units from the supported measures
    in the measurements plugin, which are ['weight', 'volume', 'mass', 'area',
    distance].

    In a ui layout, you can use the fields "unit value".

    WARNING: passing a value for the *value* field is invalid when a value for
    the *unit* is not given (or NOT set already)!

    You can access the measurement object by accessing the .m (dot em) property
    of the Measurable subclasses, like so::

        potato = Potato(**kwargs)
        measurement = potato.m

    """
    measurement_label = _("Measured as")
    unit_class = AllUnits

    @classmethod
    def on_analyze(cls, site):
        super().on_analyze(site)
        if cls.unit is None:
            raise NotImplementedError("'unit' field is not defined!")
        cls.unit_class = cls._meta.get_field('unit').choicelist

    @classmethod
    def units(cls, units=[]):
        if len(units) == 0:
            return AllUnits

        class MyMeasurablesUnits(MeasurablesUnits):
            pass

        add = MyMeasurablesUnits.add_item
        for key, value in _UNITS.items():
            if key in units:
                for item in value.choices:
                    item = item[0]
                    suffix = value.__name__[:-1].lower() + "_"
                    add(suffix + item.value, item.text, suffix + item.name, choicelist_class=value)
        return MyMeasurablesUnits

    class Meta:
        abstract = True

    limit = models.Q(
        models.Q(
            models.Q(model='volume') |
            models.Q(model='area') |
            models.Q(model='time') |
            models.Q(model='weight') |
            models.Q(model='distance')
        ),
        app_label='measurements'
    )

    measurement_class = dd.ForeignKey(
        ContentType,
        editable=True,
        limit_choices_to=limit,
        blank=True, null=True,
        verbose_name=format_lazy("{} {}", measurement_label, _('(type)')))

    measurement_object_id = GenericForeignKeyIdField(
        measurement_class,
        editable=True,
        blank=True, null=True,
        verbose_name=format_lazy(u"{} {}", measurement_label, _('(object)')))

    measurement = GenericForeignKey(
        'measurement_class', 'measurement_object_id',
        verbose_name=measurement_label)

    unit = None

    @dd.virtualfield(models.IntegerField(_("Value")), editable=True)
    def value(cls, ar):
        if ar is not None and ar.request.method in ('PUT', 'POST'):
            value = None
            unit = cls.unit
            unitHidden = None
            for k in ar.rqdata:
                if k.endswith('value'):
                    value = ar.rqdata.get(k)
                if k.endswith('unit'):
                    unit = ar.rqdata.get(k)
                if k.endswith('unitHidden'):
                    unitHidden = ar.rqdata.get(k)

            if value is not None and cls.measurement is None and unit is None and unitHidden is None: # Also add conditionals to check for unit is rqdata
                raise DependencyError("Specify a `unit` before submitting a value.")

            if value is not None:
                if unitHidden is None:
                    unitHidden = unit.value
                _u = unitHidden.split('_', 1)[1]
                if unit is None:
                    unit = unit_class.get_by_value(unitHidden)
                unit = unit.choicelist_class.get_by_value(_u)
                model_name = unit.measurement_name if unit.measurement_name != 'Mass' else 'Weight'
                model = getattr(rt.models.measurements, model_name)
                measurement = globals()[unit.measurement_name]
                value = measurement(**{unit.name: float(value)})
                measure, created = model.objects.get_or_create(unit=unit, value=value)
                if created:
                    measure.full_clean()
                    measure.save()
                cls.measurement = measure
                cls.full_clean()
                cls.save()

        if cls.measurement is not None:
            return getattr(cls.measurement.value, cls.measurement.unit.value)

    @property
    def m(self):
        if self.measurement is not None:
            return self.measurement.value.__class__(**{
                self.measurement.unit.value:
                    getattr(self.measurement.value, self.measurement.unit.value)
            })

    def __str__(self):
        return str(self.m)
