# -*- coding:utf-8 -*-
from __future__ import unicode_literals
from rest_framework import viewsets, decorators, response, exceptions
from xyz_restful.decorators import register
from xyz_restful.mixins import UserApiMixin

from . import models, serializers


@register()
class PolicyViewSet(viewsets.ModelViewSet):
    queryset = models.Policy.objects.all()
    serializer_class = serializers.PolicySerializer

    @decorators.action(['POST'], detail=False)
    def appoint(self, request):
        rd = request.data
        policy = models.Policy.objects.filter(key=rd.get('key')).first()
        if not policy:
            raise exceptions.NotFound()
        appointment, created = models.Appointment.objects.get_or_create(
            policy=policy,
            user=request.user,
            is_active=True,
            defaults=dict(
                session_max_age=rd.get('session_max_age', '7d')
            )
        )
        from .helper import gen_appoint_token
        context = rd.get('context', {})
        context['ak'] = appointment.key
        token = gen_appoint_token(context)
        return response.Response(dict(token=token))


@register()
class AppointmentViewSet(UserApiMixin, viewsets.ModelViewSet):
    queryset = models.Appointment.objects.all()
    serializer_class = serializers.AppointmentSerializer

    @decorators.action(['POST'], detail=True)
    def gen_token(self, request, pk):
        rd = request.data
        from .helper import gen_appoint_token
        context = rd.get('context', {})
        context['ak'] = self.get_object().key
        token = gen_appoint_token(context)
        return response.Response(dict(token=token))
