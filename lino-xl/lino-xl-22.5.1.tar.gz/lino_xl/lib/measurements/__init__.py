# -*- coding: UTF-8 -*-
# Copyright 2022 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

from lino.api import ad, _

class Plugin(ad.Plugin):

    verbose_name = _("Measurements")

    def get_requirements(self, site):
        yield 'django-measurement'
