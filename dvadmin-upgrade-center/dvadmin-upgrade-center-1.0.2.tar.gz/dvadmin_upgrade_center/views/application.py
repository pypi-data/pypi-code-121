# -*- coding: utf-8 -*-
from rest_framework.views import APIView
from user_agents import parse

from dvadmin.utils.json_response import ErrorResponse, DetailResponse
from dvadmin.utils.request_util import get_request_ip, get_ip_analysis, get_os, get_browser
from dvadmin.utils.serializers import CustomModelSerializer
from dvadmin.utils.viewset import CustomModelViewSet
from dvadmin_upgrade_center.models import Application, AppVersion, AppDeviceManage, DeviceUpgrade, UpgradeLogging


class ApplicationSerializer(CustomModelSerializer):
    """
    应用管理-序列化器
    """

    class Meta:
        model = Application
        fields = "__all__"
        read_only_fields = ["id"]


class ApplicationViewSet(CustomModelViewSet):
    """
    应用管理后台接口
    """
    extra_filter_backends = []
    queryset = Application.objects.all()
    serializer_class = ApplicationSerializer


class ApplicationUpdateViewSet(APIView):
    """
    软件更新检测接口
    """
    authentication_classes = []
    permission_classes = []

    def save_upgrade_logging(self, version_id, device_id, type, device_upgrade_id=None):
        """
        保存升级日志log
        :return:
        """
        # 3. 获取该"应用ID"及"设备号"的最近一条升级日志，如果版本和所上传版本一致，则表示前一个请求升级失败，未升级，并更新
        # 3.1 根据当前日志，查询对应的"应用设备升级"表，更新对应的升级状态
        upgrade_logging_obj = UpgradeLogging()

        app_version_obj = AppVersion.objects.filter(
            application__app_id=self.request.data.get('app_id'),
            version_number=self.request.data.get('version'),
            platform=int(self.request.data.get('platform'))).first()
        if app_version_obj:
            upgrade_logging_obj.before_app_version_id = app_version_obj.id
        upgrade_logging_obj.app_version_id = version_id
        upgrade_logging_obj.app_device_manage_id = device_id
        upgrade_logging_obj.device_upgrade_id = device_upgrade_id
        upgrade_logging_obj.logging_type = type
        ip = get_request_ip(request=self.request)
        upgrade_logging = get_ip_analysis(ip)
        upgrade_logging_obj.ip = ip
        upgrade_logging_obj.agent = str(parse(self.request.META['HTTP_USER_AGENT']))
        upgrade_logging_obj.browser = get_browser(self.request)
        upgrade_logging_obj.os = get_os(self.request)
        upgrade_logging_obj.save()
        UpgradeLogging.objects.update_or_create(id=upgrade_logging_obj.id, defaults=upgrade_logging)

        # 升级前的版本
        if type != -1:
            app_device_manage_obj = AppDeviceManage.objects.get(id=device_id)
            app_device_manage_obj.before_app_version_id = app_version_obj and app_version_obj.id
            app_device_manage_obj.app_version_id = version_id
            app_device_manage_obj.save()

        return

    def return_data(self, version_id):
        instance = AppVersion.objects.get(id=version_id)
        return {
            "app_id": instance.application_id,
            "platform": instance.platform,
            "platform_name": instance.platform,
            "version": instance.version_number,
            "download_url": instance.download_url,
            "file_md5": instance.file_md5,
            "file_size": instance.file_size,
            "title": instance.title,
            "content": instance.content,
            "is_coerce_upgrade": instance.is_coerce_upgrade,
            "upgrade_type": instance.upgrade_type,
            "status": instance.status,
            "status_name": instance.status,
        }

    def post(self, request, *args, **kwargs):

        app_id = self.request.data.get('app_id', None)
        version = self.request.data.get('version', None)
        platform = self.request.data.get('platform', None)
        device = self.request.data.get('device', None)

        if not app_id:
            return ErrorResponse(msg='应用标识不能为空!')
        application_obj = Application.objects.filter(app_id=app_id).first()
        if not application_obj:
            return ErrorResponse(msg='应用标识找不到!')
        app_id = application_obj.id
        if not platform:
            # 如果发布平台为空
            return ErrorResponse(msg='发布平台不能为空!')
        # =================================
        """
        应用id必传
        版本发布平台必传
        情况1: 设备号不传，版本号不传
        情况2: 设备号不传，只传版本号
        情况3: 设备号传，版本号传
        """

        if not device:
            # 设备号为空，判断版本号是否有，有则返回指定版本
            if version:
                app_version_obj = AppVersion.objects.filter(application_id=app_id, version_number=version,
                                                            platform=int(platform)).first()
                if not app_version_obj:
                    return ErrorResponse(msg='未找到版本号!')
                # 保存日志
                self.save_upgrade_logging(version_id=app_version_obj.id, device_id=None, type=0)
            else:
                app_version_obj = AppVersion.objects.filter(application_id=app_id, upgrade_type=1,
                                                            platform=int(platform)).first()
                if not app_version_obj:
                    return ErrorResponse(msg='未找到正式上线版本!')
                # 保存日志
                self.save_upgrade_logging(version_id=app_version_obj.id, device_id=None, type=0)
            return DetailResponse(data=self.return_data(app_version_obj.id), msg="获取成功")

        # ============== 传设备管理 ====================
        # 设备号不存在则创建
        app_device_manage_obj, _ = AppDeviceManage.objects.get_or_create(application_id=app_id, device_id=device,
                                                                         platform_type=int(platform))
        # ============== 获取版本 =====================
        # 1. 根据"应用ID"及"设备号"查询"应用设备升级"表
        # 1.1 查询此"应用ID"及"设备号"是否有手动升级的版本有则返回手动升级版本
        # 1.2 检查当前"应用ID"及"设备号"是否有版本回滚，有则返回版本回滚版本
        # 1.3 检查当前"应用ID"及"设备号"是否有内测升级，有则返回内测升级版本
        # 2. "应用设备升级"表中无记录，则检查当前版本是否为上线版本，否则返回正在上线版本
        # 3. 获取该"应用ID"及"设备号"的最近一条升级日志，如果版本和所上传版本一致，则表示前一个请求升级失败未升级，并更新
        # 3.1 根据当前日志，查询对应的"应用设备升级"表，更新对应的升级状态
        # 4. 保存当前请求日志，并更新最后一条日志进行状态更新(改为未升级)
        # 4.1 根据当前日志，查询对应的"应用设备升级"表，更新对应的升级状态
        device_upgrade_obj = DeviceUpgrade.objects.filter(app_device_manage_id=app_device_manage_obj.id,
                                                          status=0).order_by('upgrade_type').first()
        if device_upgrade_obj:
            # 1. 根据"应用ID"及"设备号"查询"应用设备升级"表
            # 1.1 查询此"应用ID"及"设备号"是否有手动升级的版本有则返回手动升级版本
            # 1.2 检查当前"应用ID"及"设备号"是否有版本回滚，有则返回版本回滚版本
            # 1.3 检查当前"应用ID"及"设备号"是否有内测升级，有则返回内测升级版本
            if device_upgrade_obj.app_version.version_number == version:
                device_upgrade_obj.status = 1
                device_upgrade_obj.save()
                # 保存日志
                self.save_upgrade_logging(version_id=device_upgrade_obj.app_version.id,
                                          device_id=app_device_manage_obj.id,
                                          type=-1)
                return ErrorResponse(code=2002, msg="已是最新版本")
            data = self.return_data(device_upgrade_obj.app_version_id)
            data['is_coerce_upgrade'] = device_upgrade_obj.is_coerce_upgrade
            data['upgrade_type'] = device_upgrade_obj.upgrade_type
            data['status'] = device_upgrade_obj.status
            data['status_name'] = device_upgrade_obj.status
            # 保存日志
            self.save_upgrade_logging(version_id=device_upgrade_obj.app_version_id,
                                      device_id=app_device_manage_obj.id,
                                      type=device_upgrade_obj.status,
                                      device_upgrade_id=device_upgrade_obj.id)
            return DetailResponse(data=data, msg="获取成功")
        # 2. "应用设备升级"表中无记录，则检查当前版本是否为上线版本，否则返回正在上线版本
        app_version_obj = AppVersion.objects.filter(application_id=app_id, status=1).first()
        if not app_version_obj:
            return ErrorResponse(msg='未找到正式上线版本!')
        if app_version_obj.version_number == version:
            # 保存日志
            self.save_upgrade_logging(version_id=app_version_obj.id,
                                      device_id=app_device_manage_obj.id,
                                      type=-1)
            return ErrorResponse(code=2002, msg="已是最新版本")
        # 保存日志
        self.save_upgrade_logging(version_id=app_version_obj.id,
                                  device_id=app_device_manage_obj.id,
                                  type=0)
        return DetailResponse(data=self.return_data(app_version_obj.id), msg="获取成功")
