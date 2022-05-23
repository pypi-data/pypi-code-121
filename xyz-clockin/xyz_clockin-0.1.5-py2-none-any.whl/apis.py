# -*- coding:utf-8 -*-
from __future__ import division, unicode_literals
from xyz_restful.mixins import UserApiMixin, BatchActionMixin
from rest_framework.response import Response

__author__ = 'denishuang'

from . import models, serializers, helper
from rest_framework import viewsets, decorators, status
from xyz_restful.decorators import register, register_raw


@register()
class ProjectViewSet(UserApiMixin, viewsets.ModelViewSet):
    queryset = models.Project.objects.all()
    serializer_class = serializers.ProjectSerializer
    filter_fields = {
        'id': ['in', 'exact'],
    }
    search_fields = ('name',)
    user_field_name = 'creator'

@register()
class GroupViewSet(BatchActionMixin, viewsets.ModelViewSet):
    queryset = models.Group.objects.all()
    serializer_class = serializers.GroupSerializer
    filter_fields = {
        'id': ['in', 'exact'],
        'project': ['exact'],
    }
    search_fields = ('name',)

    @decorators.action(['GET'], detail=False)
    def current(self, request):
        group = self.filter_queryset(self.get_queryset()).first()
        if not group:
            return Response(dict())
        from datetime import datetime
        now = datetime.now()
        session = group.sessions.filter(begin_time__lt=now).last()
        return Response(dict(
            group=serializers.ProjectSerializer(group).data,
            session=serializers.SessionSerializer(session).data
        ))

    @decorators.action(['post'], detail=True)
    def add_membership(self, request, pk):
        from django.apps.registry import apps
        group = self.get_object()
        model = apps.get_model(*request.data.get('model').split('.'))
        ids = request.data.get('ids')
        c = 0
        for m in model.objects.filter(id__in=ids):
            membership, created = group.memberships.get_or_create(
                user=m.user,
                defaults=dict(
                    user_name=m.name,
                    is_free=group.is_free
                ))
            if created:
                c += 1
        return Response(dict(rows=c))


    @decorators.action(['POST'], detail=False)
    def batch_reload_items(self, request):
        return self.do_batch_action(lambda group: group.reload_items_names())

@register()
class SessionViewSet(BatchActionMixin, viewsets.ModelViewSet):
    queryset = models.Session.objects.all()
    serializer_class = serializers.SessionSerializer
    filter_fields = {
        'id': ['in', 'exact'],
        'is_active': ['exact'],
        'group': ['exact']
    }
    search_fields = ('name',)
    ordering_fields = ('group', 'number')

    @decorators.action(['get'], detail=True)
    def get_items(self, request, pk):
        session = self.get_object()
        return Response(dict(items=helper.gen_session_items(session)))

    @decorators.action(['POST'], detail=False)
    def batch_reload_items(self, request):
        return self.do_batch_action(lambda session: session.reload_items_names())


@register()
class PointViewSet(viewsets.ModelViewSet):
    queryset = models.Point.objects.all()
    serializer_class = serializers.PointSerializer
    filter_fields = {
        'id': ['in', 'exact'],
        'user': ['in']
    }


@register()
class MemberShipViewSet(BatchActionMixin, viewsets.ModelViewSet):
    queryset = models.MemberShip.objects.all()
    serializer_class = serializers.MemberShipSerializer
    filter_fields = {
        'id': ['in', 'exact'],
        'is_active': ['exact'],
        'is_free': ['exact'],
        'group': ['exact']
    }
    search_fields = ('user_name',)

    @decorators.action(['POST'], detail=False)
    def batch_is_free(self, request):
        return self.do_batch_action('is_free', default=True)
