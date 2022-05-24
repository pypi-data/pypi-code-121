# -*- coding: UTF-8 -*-
# Copyright 2022 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

from lino.api import dd, _
from measurement.measures import Distance, Area, Volume, Mass, Time

__all__ = [
    'TimeUnits', 'WeightUnits', 'DistanceUnits', 'AreaUnits', 'VolumeUnits',
    'UnitTypes', 'AllUnits', 'MeasurablesUnits'
]

ALL_UNITS = dict(
    TimeUnits=Time,
    WeightUnits=Mass,
    DistanceUnits=Distance,
    AreaUnits=Area,
    VolumeUnits=Volume
)

class BaseUnit(dd.Choice):
    measurement_name = None

class Units(dd.ChoiceList):
    verbose_name = _("Unit")
    verbose_name_plural = _("Units")
    item_class = BaseUnit

class Unit(BaseUnit):
    choicelist_class = None

class MeasurablesUnits(Units):
    item_class = Unit

class AllUnits(Units):
    item_class = Unit
    verbose_name_plural = _("All units")

for choicelist_name, measurement in ALL_UNITS.items():
    choicelist = type(choicelist_name, (Units, ), {'app_label': 'measurements'})
    locals()[choicelist_name] = choicelist
    add = locals()[choicelist_name].add_item

    TEMP_DICT = dict()
    for alias, symbol in measurement.get_aliases().items():
        if symbol in TEMP_DICT and len(TEMP_DICT[symbol]) > len(alias):
                continue
        TEMP_DICT[symbol] = alias

    for symbol, alias in TEMP_DICT.items():
        add(symbol, _(alias), symbol, measurement_name=measurement.__name__)
        s = choicelist_name.lower()[:-1] + '_' + symbol
        AllUnits.add_item(s, _(alias), s, choicelist_class=choicelist)

    TEMP_DICT.clear()


class UnitTypes(dd.ChoiceList):
    verbose_name = _("Unit type")
    verbose_name_plural = _("Unit Types")

add = UnitTypes.add_item

add('100', _('Simple'), 'simple')
add('200', _('Compound'), 'compound')
