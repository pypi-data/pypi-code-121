# -*- coding: UTF-8 -*-
# Copyright 2022 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

from django.contrib.contenttypes.fields import GenericRelation

from lino.core.signals import pre_analyze

from lino.api import dd, _
from .mixins import *

class Weight(Weighted):

    class Meta:
        app_label = 'measurements'
        verbose_name = _("Weight")
        verbose_name_plural = _("Weights")
        abstract = dd.is_abstract_model(__name__, 'Weight')

class Volume(Volumed):

    class Meta:
        app_label = 'measurements'
        verbose_name = _("Volume")
        verbose_name_plural = _("Volumes")
        abstract = dd.is_abstract_model(__name__, 'Volume')


class Distance(Distanced):

    class Meta:
        app_label = 'measurements'
        verbose_name = _("Distance")
        verbose_name_plural = _("Distances")
        abstract = dd.is_abstract_model(__name__, 'Distance')


class Area(Zoned):

    class Meta:
        app_label = 'measurements'
        verbose_name = _("Area")
        verbose_name_plural = _("Areas")
        abstract = dd.is_abstract_model(__name__, 'Area')


class Time(Timed):

    class Meta:
        app_label = 'measurements'
        verbose_name = _("Time")
        verbose_name_plural = _("Times")
        abstract = dd.is_abstract_model(__name__, 'Time')

@dd.receiver(pre_analyze)
def inject_generic_relations(sender, models_list=None, **kw):
    site = sender
    measurables = [c for c in Measurable.__subclasses__() if not c._meta.abstract]
    if len(measurables) == 0:
        return
    for c in (Volume, Weight, Distance, Time, Area):
        for k in c.__subclasses__() + [c]:
            if k._meta.abstract:
                continue
            for measurable in measurables:
                field = GenericRelation(measurable,
                    content_type_field='measurement_class',
                    object_id_field='measurement_object_id',
                    related_query_name=k.__name__.lower())
                field_name = measurable._meta.app_label + '_' + measurable.__name__.lower() + 's'
                dd.inject_field(k, field_name, field)
