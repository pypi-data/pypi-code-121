# -*- coding:utf-8 -*-
from __future__ import unicode_literals
from . import serializers, models
from rest_framework import viewsets, decorators
from xyz_restful.decorators import register
from xyz_restful.helper import register_urlpatterns
from . import urls
__author__ = 'denishuang'



from django.contrib.contenttypes import models as ctmodels

@register()
class ContenttypeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ctmodels.ContentType.objects.all().order_by('app_label')
    serializer_class = serializers.ContenttypeSerializer
    permission_classes = []
    search_fields = ('app_label', 'model')
    filter_fields = {
        'id': ['exact', 'in']
    }

    def filter_queryset(self, queryset):
        if self.action == 'all':
            return self.queryset
        from xyz_auth.helper import get_user_model_permissions
        from django.db.models import Q
        user = self.request.user
        qset = super(ContenttypeViewSet, self).filter_queryset(queryset)
        mps = get_user_model_permissions(user)
        ms = [m.split('.') for m in mps.keys()]
        lookup = None
        for m in ms:
            q = Q(**dict(app_label=m[0], model=m[1]))
            lookup = (lookup | q) if lookup else q
        return qset.filter(lookup) if lookup else qset

    @decorators.action(['GET'], detail=False)
    def all(self, request):
        return self.list(request)

from .apps import Config
register_urlpatterns(Config.label, urls)



@register()
class EventViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.Event.objects.all()
    serializer_class = serializers.EventSerializer
    filter_fields = {
        'name': ['exact'],
        'owner_type_id': ['exact'],
        'owner_id': ['exact', 'in'],
    }