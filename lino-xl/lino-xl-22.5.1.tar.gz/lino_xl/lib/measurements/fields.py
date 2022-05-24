# -*- coding: UTF-8 -*-
# Copyright 2022 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)


from importlib.util import find_spec
if find_spec('django_measurement') is not None:
    from django_measurement.models import MeasurementField
else:
    class MeasurementField:
        pass
