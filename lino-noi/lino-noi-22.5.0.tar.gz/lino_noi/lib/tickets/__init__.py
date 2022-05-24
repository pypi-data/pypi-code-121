# -*- coding: UTF-8 -*-
# Copyright 2016-2021 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)
"""Lino Noi extension of :mod:`lino_xl.lib.tickets`.

"""

from lino_xl.lib.tickets import *
from lino.api import _

class Plugin(Plugin):

    extends_models = ['Ticket', "Site"]

    needs_plugins = [
        'lino_xl.lib.excerpts',
        # 'lino_xl.lib.topics',
        'lino.modlib.comments', 'lino.modlib.changes',
        # 'lino_xl.lib.votes',
        'lino_noi.lib.noi']

    def setup_main_menu(self, site, user_type, m):
        super(Plugin, self).setup_main_menu(site, user_type, m)
        p = self.get_menu_group()
        m = m.add_menu(p.app_label, p.verbose_name)
        [m.add_action(s) for s in 'tickets.MyTicketsToWork '
                                  'tickets.TicketsNeedingMyFeedback '
                                  'tickets.MyTicketsNeedingFeedback'.split()]

    def get_dashboard_items(self, user):
        for i in super(Plugin, self).get_dashboard_items(user):
            yield i
        if user.is_authenticated:
            yield self.site.models.tickets.MyTicketsToWork
            yield self.site.models.tickets.TicketsNeedingMyFeedback
            yield self.site.models.tickets.MyTicketsNeedingFeedback
            # else:
            #     yield self.site.models.tickets.   PublicTickets

    def setup_quicklinks(self, tb):
        tb.add_action('tickets.RefTickets')
        tb.add_action('tickets.ActiveTickets')
        tb.add_action('tickets.AllTickets')
        tb.add_action("tickets.AllTickets.insert",
            label=_("Submit new ticket"), icon_name=None)
