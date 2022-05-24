# -*- coding: UTF-8 -*-
# Copyright 2016-2021 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

from lino.modlib.system.choicelists import DashboardLayouts
from lino.api import _

DashboardLayouts.clear()
add = DashboardLayouts.add_item
add("default", _("Default dashboard"), """
welcome_messages
working.WorkedHours
tickets.MyTicketsToWork
comments.RecentComments notify.MyMessages
""")
add("simple", _("Simple dashboard"), """
welcome_messages
working.WorkedHours
comments.RecentComments
""")
