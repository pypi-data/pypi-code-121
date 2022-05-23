# -*- coding: utf-8 -*-
from rest_framework import serializers

from dvadmin.utils.serializers import CustomModelSerializer
from dvadmin.utils.viewset import CustomModelViewSet
from dvadmin_upgrade_center.models import DeviceUpgrade


class DeviceUpgradeSerializer(CustomModelSerializer):
    """
    设备升级-序列化器
    """
    version_number = serializers.CharField(source='app_version.version_number', default="")
    device_id = serializers.CharField(source='app_device_manage.device_id', default="")

    class Meta:
        model = DeviceUpgrade
        fields = "__all__"
        read_only_fields = ["id"]


class DeviceUpgradeViewSet(CustomModelViewSet):
    """
    设备升级后台接口
    """
    queryset = DeviceUpgrade.objects.all()
    serializer_class = DeviceUpgradeSerializer
