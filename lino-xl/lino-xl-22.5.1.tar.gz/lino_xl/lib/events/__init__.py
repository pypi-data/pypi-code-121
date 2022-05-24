# -*- coding: UTF-8 -*-
# Copyright 2013-2022 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

"""
A rather specialized plugin used only by :mod:`lino_book.projects.events`.
See :ref:`book.specs.events`
"""

from lino import ad, _


class Plugin(ad.Plugin):
    "See :doc:`/dev/plugins`."

    verbose_name = _("Events")

    def setup_config_menu(self, site, user_type, m):
        m = m.add_menu(self.app_label, self.verbose_name)
        m.add_action('events.Types')
        m.add_action('events.Places')
        m.add_action('events.Features')

    def setup_main_menu(self, site, user_type, m):
        m = m.add_menu(self.app_label, self.verbose_name)
        m.add_action('events.Events')
