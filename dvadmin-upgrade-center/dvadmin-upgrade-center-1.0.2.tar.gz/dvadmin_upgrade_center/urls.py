# -*- coding: utf-8 -*-
from django.urls import path
from rest_framework import routers

from dvadmin_upgrade_center.views.app_device_manage import AppDeviceManageViewSet
from dvadmin_upgrade_center.views.app_version import AppVersionViewSet
from dvadmin_upgrade_center.views.application import ApplicationViewSet, ApplicationUpdateViewSet
from dvadmin_upgrade_center.views.device_upgrade import DeviceUpgradeViewSet
from dvadmin_upgrade_center.views.upgrade_logging import UpgradeLoggingViewSet

router_url = routers.SimpleRouter()
router_url.register(r'application', ApplicationViewSet)
router_url.register(r'app_version', AppVersionViewSet)
router_url.register(r'app_device_manage', AppDeviceManageViewSet)
router_url.register(r'upgrade_logging', UpgradeLoggingViewSet)
router_url.register(r'device_upgrade', DeviceUpgradeViewSet)

urlpatterns = [
    # 发布上线
    path('release_online/', AppVersionViewSet.as_view({'post': 'release_online'}), ),
    # 版本回滚
    path('version_rollback/', AppVersionViewSet.as_view({'post': 'version_rollback'}), ),
    # 取消更新
    path('cancel_update/', AppVersionViewSet.as_view({'post': 'cancel_update'}), ),
    # 版本内测
    path('internal_test/', AppVersionViewSet.as_view({'post': 'internal_test'}), ),
    # 软件版本更新-对外提供接口
    path('update/', ApplicationUpdateViewSet.as_view(), )
]
urlpatterns += router_url.urls
