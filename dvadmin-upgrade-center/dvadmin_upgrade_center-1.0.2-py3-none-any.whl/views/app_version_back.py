# -*- coding: utf-8 -*-
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import serializers
from rest_framework.decorators import action

from dvadmin.utils.json_response import ErrorResponse, DetailResponse
from dvadmin.utils.serializers import CustomModelSerializer
from dvadmin.utils.validator import CustomValidationError
from dvadmin.utils.viewset import CustomModelViewSet
from dvadmin_upgrade_center.models import AppVersion
from dvadmin_upgrade_center.views.version_request import VersionRequestSerializer


class AppVersionSerializer(CustomModelSerializer):
    """
    app版本管理-序列化器
    """

    class Meta:
        model = AppVersion
        fields = "__all__"
        read_only_fields = ["id"]


class AppVersionCreateSerializer(CustomModelSerializer):
    """
    app版本管理-新增序列化器
    """

    def validate_status(self, value):
        application = self.initial_data.get('application')
        if value:
            AppVersion.objects.filter(application_id=application).update(status=False)
        return value

    def validate_version(self, value):
        """验证平台和版本号"""
        platform = self.initial_data.get('platform')
        application = self.initial_data.get('application')
        version = ''.join(value.split("."))
        queryset = AppVersion.objects.filter(application_id=application).values('version', 'platform')
        list = iter(queryset)
        for item in list:
            q_version = item.get('version')
            q_version = ''.join(q_version.split("."))
            q_platform = item.get('platform')
            if int(version) <= int(q_version) and platform == q_platform:
                raise CustomValidationError("同平台的应用版本号必须大于已存在的版本号")
        return value

    class Meta:
        model = AppVersion
        fields = "__all__"
        read_only_fields = ["id"]


class AppVersionUpdateSerializer(CustomModelSerializer):
    """
    app版本管理-修改序列化器
    """

    def validate_status(self, value):
        platform = self.initial_data.get('platform')
        application = self.initial_data.get('application')
        if value:
            AppVersion.objects.filter(platform=platform, application_id=application).update(status=False)
        return value

    class Meta:
        model = AppVersion
        fields = "__all__"
        read_only_fields = ["id"]


class AppVersionResponseSerializer(CustomModelSerializer):
    """
    app版本管理-序列化器
    """
    file_md5 = serializers.CharField(source='file_url.md5sum', default='')
    download_url = serializers.SerializerMethodField()

    def get_download_url(self, obj):
        return obj.file_url and f"/media/{obj.file_url.url}"

    file_size = serializers.SerializerMethodField()

    def get_file_size(self, obj):
        return obj.file_url and obj.file_url.url and obj.file_url.url.size

    class Meta:
        model = AppVersion
        fields = ['app_id', 'platform', 'version', 'title', 'content', 'download_url', 'upgrade_type', 'coerce_upgrade',
                  'file_md5', 'file_size']
        read_only_fields = ["id"]


class AppVersionViewSet(CustomModelViewSet):
    """
    APP版本管理接口
    list:查询
    create:新增
    update:修改
    retrieve:单例
    destroy:删除
    """
    queryset = AppVersion.objects.all()
    serializer_class = AppVersionSerializer
    create_serializer_class = AppVersionCreateSerializer
    update_serializer_class = AppVersionUpdateSerializer


class UpdateRecordViewSet(CustomModelViewSet):
    """
    APP版本管理接口
    list:查询
    create:新增
    update:修改
    retrieve:单例
    destroy:删除
    """
    queryset = AppVersion.objects.all()
    serializer_class = AppVersionSerializer
    create_serializer_class = AppVersionCreateSerializer
    update_serializer_class = AppVersionUpdateSerializer
    permission_classes = []
    authentication_classes = []

    app_id = openapi.Schema(description='设备标识', type=openapi.TYPE_STRING)
    device = openapi.Schema(description='设备号', type=openapi.TYPE_STRING)
    version = openapi.Schema(description='版本号', type=openapi.TYPE_STRING)
    platform = openapi.Schema(description='平台', type=openapi.TYPE_STRING)

    @action(methods=['post'], detail=False, permission_classes=[])
    @swagger_auto_schema(request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['app_id', 'version', 'platform'],
        properties={'app_id': app_id, 'device': device, 'version': version, 'platform': platform}
    ), operation_summary='应用版本访问更新')
    def update_record(self, request, *args, **kwargs):
        """更新访问记录"""
        body = request.data
        app_id = body.get('app_id')
        device = body.get('device')
        version = body.get('version')
        platform = body.get('platform')
        s = VersionRequestSerializer(data=body)
        if s.is_valid(raise_exception=True):
            queryset = AppVersion.objects.filter(app_id=app_id, platform=platform, status=True).first()
            if not queryset:
                return ErrorResponse(code=2103, msg="未获取到版本，请检查传入版本是否正确!")
            q_version = queryset.version
            if q_version != version:
                serializers = AppVersionResponseSerializer(queryset)
                s.save()
                data = serializers.data
                return DetailResponse(data=data, msg="获取成功!")
            else:
                return ErrorResponse(code=2002, msg="已是最新版本")
        else:
            return ErrorResponse(msg=s.error_messages)
