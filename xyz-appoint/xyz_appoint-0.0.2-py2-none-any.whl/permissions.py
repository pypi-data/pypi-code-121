# -*- coding:utf-8 -*-
from __future__ import unicode_literals
from rest_framework.permissions import DjangoModelPermissions

__author__ = 'denishuang'


class AppointPermissions(DjangoModelPermissions):
    def has_permission(self, request, view):
        if not hasattr(view, 'action'):
            return True
        if view.action == 'metadata':
            return True
        from .models import Appointment
        appointment = request.auth
        if not isinstance(appointment, Appointment):
            return True
        qs = self._queryset(view)
        policy = appointment.policy
        scope = policy.scope
        am = qs.model._meta.label_lower
        print(am, scope, view.action)
        if am not in scope:
            return False
        if view.action not in scope[am].get('actions', []):
            return False
        return True
