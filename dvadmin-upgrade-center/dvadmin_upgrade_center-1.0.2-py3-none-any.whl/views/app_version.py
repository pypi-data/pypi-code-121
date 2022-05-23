# -*- coding: utf-8 -*-

from dvadmin.utils.json_response import DetailResponse, ErrorResponse
from dvadmin.utils.serializers import CustomModelSerializer
from dvadmin.utils.viewset import CustomModelViewSet
from dvadmin_upgrade_center.models import AppVersion, AppDeviceManage, DeviceUpgrade


class AppVersionSerializer(CustomModelSerializer):
    """
    应用版本管理-序列化器
    """

    class Meta:
        model = AppVersion
        fields = "__all__"
        read_only_fields = ["id"]


class AppVersionCreateSerializer(CustomModelSerializer):
    """
    应用版本管理-新增序列化器
    """

    class Meta:
        model = AppVersion
        fields = "__all__"
        read_only_fields = ["id"]


class AppVersionUpdateSerializer(CustomModelSerializer):
    """
    应用版本管理-修改序列化器
    """

    class Meta:
        model = AppVersion
        fields = "__all__"
        read_only_fields = ["id"]


class AppVersionResponseSerializer(CustomModelSerializer):
    """
    应用版本管理-序列化器
    """

    class Meta:
        model = AppVersion
        fields = "__all__"
        read_only_fields = ["id"]


class AppVersionViewSet(CustomModelViewSet):
    """
    应用版本管理接口
    """
    queryset = AppVersion.objects.all()
    serializer_class = AppVersionSerializer
    create_serializer_class = AppVersionCreateSerializer
    update_serializer_class = AppVersionUpdateSerializer

    def release_online(self, request, *args, **kwargs):
        """
        发布上线
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        app_version_id = self.request.data.get('id')
        instance = self.queryset.get(id=app_version_id)
        if instance.status == 1:
            return ErrorResponse(data=[], msg="已是正式版本，无需再上线!")
        instance.status = 1
        # 更新当前版本发布平台的其他正式发布为下线状态
        self.queryset.filter(application_id=instance.application_id, platform=instance.platform, status=1).exclude(
            id=instance.id).update(status=4)
        instance.save()
        return DetailResponse(data=[], msg="上线成功!")

    def version_rollback(self, request, *args, **kwargs):
        """
        版本回滚
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        app_version_id = self.request.data.get('id')
        rollback_version_id = self.request.data.get('rollback_version_id')
        if app_version_id == rollback_version_id:
            return ErrorResponse(data=[], msg="回滚失败，当前版本和回滚版本不可一致!")
        instance = self.queryset.get(id=app_version_id)
        rollback_version_instance = self.queryset.get(id=rollback_version_id)
        if rollback_version_instance.platform != instance.platform:
            return ErrorResponse(data=[], msg="回滚失败，版本发布平台不一致!")

        instance.status = 3
        instance.save()
        rollback_version_instance.status = 1
        rollback_version_instance.save()
        # 并把当前版本下所有设备添加到回滚列表，把需要回滚的数据进行取消
        all_manage_ids = AppDeviceManage.objects.filter(app_version=instance).values_list('id', flat=True)
        # 把该所有设备中，有升级任务的全部改为失效
        DeviceUpgrade.objects.filter(app_device_manage_id__in=all_manage_ids, status=0).update(status=2)
        # 旧版本的所有设备，添加新更新版本进到回滚任务中
        device_upgrade_list = []
        for device_id in all_manage_ids:
            device_upgrade_list.append(DeviceUpgrade(app_version=rollback_version_instance,
                                                     app_device_manage_id=device_id,
                                                     upgrade_type=3,
                                                     is_coerce_upgrade=rollback_version_instance.is_coerce_upgrade))
        DeviceUpgrade.objects.bulk_create(device_upgrade_list)

        return DetailResponse(data=[], msg="回滚成功!")

    def cancel_update(self, request, *args, **kwargs):
        """
        取消更新
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        device_upgrade_id = self.request.data.get('id')
        instance = DeviceUpgrade.objects.filter(id=device_upgrade_id).first()
        if not instance:
            return ErrorResponse(data=[], msg="未找到应用设备升级数据")
        if instance.status != 0:
            return ErrorResponse(data=[], msg="当前不是待完成状态，无需再取消!")
        instance.status = 3
        instance.save()
        return DetailResponse(data=[], msg="上线成功!")

    def internal_test(self, request, *args, **kwargs):
        """
        版本内测
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        device_ids = self.request.data.get('device_ids')
        version_id = self.request.data.get('version_id')
        app_version_obj = AppVersion.objects.filter(id=version_id).first()
        if not app_version_obj:
            return ErrorResponse(data=[], msg="未找到版本")
        device_ids = AppDeviceManage.objects.filter(id__in=device_ids).values_list('id', flat=True)
        device_upgrade_list = []
        DeviceUpgrade.objects.filter(app_device_manage_id__in=device_ids, status=0).update(status=2)
        for device_id in device_ids:
            device_upgrade_list.append(
                DeviceUpgrade(app_version_id=app_version_obj.id,
                              app_device_manage_id=device_id,
                              upgrade_type=2,
                              is_coerce_upgrade=app_version_obj.is_coerce_upgrade)
            )
        DeviceUpgrade.objects.bulk_create(device_upgrade_list)
        return DetailResponse(data=[], msg="添加内测成功!")
