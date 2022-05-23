# -*- coding: utf-8 -*-
import datetime

from django.db import models

from dvadmin.utils.models import CoreModel

TABLE_PREFIX = 'upgrade_center_'

PLATFORM_CHOICES = (
    (0, "Windows"),
    (1, "Linux"),
    (2, "Android"),
    (3, "Apple"),
)


class Application(CoreModel):
    name = models.CharField(max_length=50, verbose_name="应用名称")
    app_id = models.CharField(max_length=100, unique=True, verbose_name="应用标识")

    # download_url = models.CharField(max_length=400, verbose_name="最新版本下载地址", null=True, blank=True)

    class Meta:
        db_table = TABLE_PREFIX + "application"
        verbose_name = "应用管理"
        verbose_name_plural = verbose_name
        ordering = ('-create_datetime',)


class AppVersion(CoreModel):
    UPGRADE_TYPE_CHOICES = (
        (0, "整包"),
        (1, "部分")
    )

    STATUS_CHOICES = (
        (0, "待上线"),
        (1, "正式发布"),
        (2, "灰度内测"),
        (3, "版本回滚"),
        (4, "下线"),
    )
    version_number = models.CharField(max_length=100, verbose_name="版本号")
    title = models.CharField(max_length=50, null=True, blank=True, verbose_name="版本标题")
    content = models.CharField(max_length=1000, null=True, blank=True, verbose_name="版本内容")
    application = models.ForeignKey(Application, db_constraint=False, on_delete=models.PROTECT, verbose_name="所属应用")
    upgrade_type = models.IntegerField(choices=UPGRADE_TYPE_CHOICES, default=0, verbose_name="升级类型")
    is_coerce_upgrade = models.BooleanField(default=False, verbose_name="是否强制升级")
    platform = models.IntegerField(choices=PLATFORM_CHOICES, default=0, verbose_name="版本发布平台")
    download_url = models.CharField(max_length=400, null=True, blank=True, verbose_name="版本文件地址")
    file_size = models.CharField(max_length=20, null=True, blank=True, verbose_name="文件大小")
    file_md5 = models.CharField(max_length=40, null=True, blank=True, verbose_name="文件md5")
    status = models.IntegerField(choices=STATUS_CHOICES, default=0, verbose_name="版本状态")
    release_time = models.DateTimeField(default=datetime.datetime.now, verbose_name="发布时间")

    class Meta:
        db_table = TABLE_PREFIX + "app_version"
        verbose_name = "应用版本"
        verbose_name_plural = verbose_name
        ordering = ['-release_time']
        unique_together = (("application", "version_number"),)  # 应用和版本联合唯一


class AppDeviceManage(CoreModel):
    application = models.ForeignKey(Application, db_constraint=False, on_delete=models.CASCADE, verbose_name="所属应用")
    device_id = models.CharField(max_length=255, verbose_name="设备标识号")
    online_ip = models.CharField(max_length=100, null=True, blank=True, verbose_name="常在设备ip")
    platform_type = models.IntegerField(choices=PLATFORM_CHOICES, default=0, verbose_name="版本发布平台类型")
    app_version = models.ForeignKey(AppVersion, db_constraint=False, on_delete=models.CASCADE, null=True, blank=True,
                                    verbose_name="当前版本号")
    before_app_version = models.ForeignKey(AppVersion, db_constraint=False, null=True, blank=True,
                                           related_name='before_app_version_device',
                                           on_delete=models.CASCADE, verbose_name="升级前版本")

    class Meta:
        db_table = TABLE_PREFIX + "app_device_manage"
        verbose_name = "应用设备管理"
        verbose_name_plural = verbose_name
        ordering = ('-create_datetime',)
        unique_together = (("application", "device_id", "platform_type"),)  # 应用和版本联合唯一


class DeviceUpgrade(CoreModel):
    UPGRADE_TYPE_CHOICES = (
        (1, "手动升级"),
        (2, "灰度内测"),
        (3, "版本回滚"),
    )
    STATUS_CHOICES = (
        (0, "待完成"),
        (1, "已完成"),
        (2, "已失效"),
        (3, "手动取消"),
    )
    app_version = models.ForeignKey(AppVersion, db_constraint=False, on_delete=models.CASCADE, verbose_name="升级版本")
    app_device_manage = models.ForeignKey(AppDeviceManage, db_constraint=False, on_delete=models.CASCADE,
                                          verbose_name="所属设备")
    upgrade_type = models.IntegerField(choices=UPGRADE_TYPE_CHOICES, default=1, verbose_name="升级类型")
    status = models.IntegerField(choices=STATUS_CHOICES, default=0, verbose_name="升级状态")
    is_coerce_upgrade = models.BooleanField(default=False, verbose_name="是否强制")

    class Meta:
        db_table = TABLE_PREFIX + "device_upgrade"
        verbose_name = "应用设备升级"
        verbose_name_plural = verbose_name
        ordering = ('status', '-create_datetime')


class UpgradeLogging(CoreModel):
    LOGGING_TYPE_CHOICES = (
        (-1, "无变化"),
        (0, "正常升级"),
        (1, "手动升级"),
        (2, "灰度内测"),
        (3, "版本回滚"),
        (4, "错误日志"),
    )
    app_version = models.ForeignKey(AppVersion, db_constraint=False, on_delete=models.CASCADE, verbose_name="升级版本")
    before_app_version = models.ForeignKey(AppVersion, db_constraint=False, null=True, blank=True,
                                           related_name='before_app_version_logging',
                                           on_delete=models.CASCADE, verbose_name="升级前版本")
    app_device_manage = models.ForeignKey(AppDeviceManage, db_constraint=False, on_delete=models.CASCADE,
                                          null=True, blank=True, verbose_name="所属设备")
    device_upgrade = models.ForeignKey(DeviceUpgrade, db_constraint=False, on_delete=models.CASCADE,
                                       null=True, blank=True, verbose_name="关联设备升级")
    error_content = models.TextField(verbose_name="错误日志内容", null=True, blank=True, help_text="错误日志内容")
    logging_type = models.IntegerField(choices=LOGGING_TYPE_CHOICES, default=1, verbose_name="日志类型")
    ip = models.CharField(max_length=32, verbose_name="日志ip", null=True, blank=True, help_text="登录ip")
    # 日志信息
    agent = models.TextField(verbose_name="agent信息", null=True, blank=True, help_text="agent信息")
    browser = models.CharField(max_length=200, verbose_name="浏览器名", null=True, blank=True, help_text="浏览器名")
    os = models.CharField(max_length=200, verbose_name="操作系统", null=True, blank=True, help_text="操作系统")

    continent = models.CharField(max_length=50, verbose_name="州", null=True, blank=True, help_text="州")
    country = models.CharField(max_length=50, verbose_name="国家", null=True, blank=True, help_text="国家")
    province = models.CharField(max_length=50, verbose_name="省份", null=True, blank=True, help_text="省份")
    city = models.CharField(max_length=50, verbose_name="城市", null=True, blank=True, help_text="城市")
    district = models.CharField(max_length=50, verbose_name="县区", null=True, blank=True, help_text="县区")
    isp = models.CharField(max_length=50, verbose_name="运营商", null=True, blank=True, help_text="运营商")
    area_code = models.CharField(max_length=50, verbose_name="区域代码", null=True, blank=True, help_text="区域代码")
    country_english = models.CharField(max_length=50, verbose_name="英文全称", null=True, blank=True, help_text="英文全称")
    country_code = models.CharField(max_length=50, verbose_name="简称", null=True, blank=True, help_text="简称")
    longitude = models.CharField(max_length=50, verbose_name="经度", null=True, blank=True, help_text="经度")
    latitude = models.CharField(max_length=50, verbose_name="纬度", null=True, blank=True, help_text="纬度")

    class Meta:
        db_table = TABLE_PREFIX + "logging"
        verbose_name = "应用升级日志"
        verbose_name_plural = verbose_name
        ordering = ('-create_datetime',)
