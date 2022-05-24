# -*- coding: UTF-8 -*-
# Copyright 2015-2021 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

"""Desktop UI for this plugin.

"""

from lino.modlib.users.desktop import *

from lino.api import _

from lino.core import actions
from lino_xl.lib.working.roles import Worker

from lino.modlib.users.actions import SendWelcomeMail
from lino.modlib.office.roles import OfficeUser
#from .models import VerifyUser

class UserDetail(UserDetail):
    """Layout of User Detail in Lino Noi."""

    main = "general #contact calendar dashboard.WidgetsByUser working.SummariesByUser comments.MentionsByOwner"

    general = dd.Panel("""
    general1:30 general2:30 general3:30 #working:15
    SocialAuthsByUser #tickets.SubscriptionsByUser groups.MembershipsByUser
    """, label=_("General"))

    # skills.OffersByEndUser

    # if dd.is_installed('working'):
    #     working = dd.Panel("""
    #
    #
    #     """, label=_("Clocking"), required_roles=dd.login_required(Worker))
    # else:
    #     working = dd.DummyPanel()

    calendar = dd.Panel("""
    event_type access_class
    cal.SubscriptionsByUser
    # cal.MembershipsByUser
    """, label=dd.plugins.cal.verbose_name, required_roles=dd.login_required(OfficeUser))

    general1 = """
    username user_type:20
    first_name last_name initials
    person partner #user_site
    """

    general2 = """
    language:10 dashboard_layout
    email mail_mode
    notify_myself open_session_on_new_ticket
    """

    general3 = """
    created:12 modified:12 id
    date_format time_zone
    github_username
    """

    # cal_left = """
    # event_type access_class
    # cal.SubscriptionsByUser
    # """

    # cal = dd.Panel("""
    # cal_left:30 cal.TasksByUser:60
    # """, label=dd.plugins.cal.verbose_name,
    #                required_roles=dd.login_required(OfficeUser))

    # contact = dd.Panel("""
    # address_box info_box
    # remarks:40 users.AuthoritiesGiven:20
    # """, label=_("Contact"))
    #
    # info_box = """
    # email:40
    # # url
    # phone
    # gsm
    # """
    # address_box = """
    # first_name last_name #initials
    # country region city zip_code:10
    # #addr1
    # #street_prefix street:25 street_no #street_box
    # # addr2
    # """


# Users.detail_layout = UserDetail()
