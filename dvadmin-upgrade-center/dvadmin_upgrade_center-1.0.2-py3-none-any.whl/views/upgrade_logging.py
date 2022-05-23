# -*- coding: utf-8 -*-
import django_filters
from rest_framework import serializers

from dvadmin.utils.serializers import CustomModelSerializer
from dvadmin.utils.viewset import CustomModelViewSet
from dvadmin_upgrade_center.models import UpgradeLogging


class UpgradeLoggingManageFilter(django_filters.FilterSet):
    version_number = django_filters.CharFilter(field_name='app_version__version_number', lookup_expr='icontains')
    before_version_number = django_filters.CharFilter(field_name='before_app_version__version_number',
                                                      lookup_expr='icontains')
    device_id = django_filters.CharFilter(field_name='app_device_manage__device_id', lookup_expr='icontains')
    logging_type = django_filters.CharFilter(lookup_expr='exact')
    ip = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = UpgradeLogging
        fields = ('version_number', 'before_version_number', 'device_id', 'logging_type', 'ip',)


class UpgradeLoggingSerializer(CustomModelSerializer):
    """
    升级日志-序列化器
    """
    version_number = serializers.CharField(source='app_version.version_number', default="")
    before_version_number = serializers.CharField(source='before_app_version.version_number', default="")
    device_id = serializers.CharField(source='app_device_manage.device_id', default="")

    class Meta:
        model = UpgradeLogging
        exclude = ("error_content",)
        read_only_fields = ["id"]


class UpgradeLoggingViewSet(CustomModelViewSet):
    """
    升级日志后台接口
    """
    queryset = UpgradeLogging.objects.all()
    serializer_class = UpgradeLoggingSerializer
    filterset_class = UpgradeLoggingManageFilter
