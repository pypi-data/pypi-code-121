# -*- coding:utf-8 -*-
from rest_framework.authentication import   TokenAuthentication
__author__ = 'denishuang'

from .models import Appointment

class AppointAuthentication(TokenAuthentication):
    model = Appointment

    def authenticate_credentials(self, key):
        from .helper import check_appoint_token
        context = check_appoint_token(key)
        user, policy = super(AppointAuthentication, self).authenticate_credentials(context['ak'])
        return user, policy