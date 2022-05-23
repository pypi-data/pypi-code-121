# -*- coding:utf-8 -*-
from __future__ import unicode_literals, print_function
from django.dispatch import receiver
from django.db.models.signals import post_save
from xyz_auth.signals import to_get_user_profile
from xyz_saas.signals import to_get_party_settings
from . import models, helper, serializers
from django.conf import settings
from xyz_util.datautils import access
import logging

log = logging.getLogger("django")

@receiver(to_get_user_profile)
def get_membership_setting(sender, **kwargs):
    user = kwargs['user']
    if hasattr(user, 'as_clockin_member'):
        return serializers.MemberShipSerializer(user.as_clockin_membership, context=dict(request=kwargs['request']))
