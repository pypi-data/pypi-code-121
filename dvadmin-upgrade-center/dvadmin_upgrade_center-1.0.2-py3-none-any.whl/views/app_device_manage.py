# -*- coding: utf-8 -*-
import django_filters
from rest_framework import serializers

from dvadmin.utils.serializers import CustomModelSerializer
from dvadmin.utils.viewset import CustomModelViewSet
from dvadmin_upgrade_center.models import AppDeviceManage


class AppDeviceManageFilter(django_filters.FilterSet):
    application = django_filters.CharFilter(lookup_expr='exact')
    device_id = django_filters.CharFilter(lookup_expr='icontains')
    platform_type = django_filters.CharFilter(lookup_expr='exact')
    version_number = django_filters.CharFilter(field_name='app_version__version_number', lookup_expr='icontains')
    before_version_number = django_filters.CharFilter(field_name='before_app_version__version_number',
                                                      lookup_expr='icontains')

    class Meta:
        model = AppDeviceManage
        fields = ('application', 'device_id', 'platform_type', 'version_number', 'before_version_number')


class AppDeviceManageSerializer(CustomModelSerializer):
    """
    应用设备管理-序列化器
    """
    version_number = serializers.CharField(source='app_version.version_number', default="")
    before_version_number = serializers.CharField(source='before_app_version.version_number', default="")

    class Meta:
        model = AppDeviceManage
        fields = "__all__"
        read_only_fields = ["id"]


class AppDeviceManageViewSet(CustomModelViewSet):
    """
    应用设备管理后台接口
    """
    queryset = AppDeviceManage.objects.all()
    serializer_class = AppDeviceManageSerializer
    filterset_class = AppDeviceManageFilter
