from application import settings

# ================================================= #
# ***************** 插件配置区开始 *******************
# ================================================= #
# 路由配置
plugins_url_patterns = [
    {"re_path": r'api/upgrade_center_backend/', "include": "dvadmin_upgrade_center.urls"},
    {"re_path": r'api/dvadmin_upgrade_center/', "include": "dvadmin_upgrade_center.urls"}
]
# app 配置
apps = ['dvadmin_upgrade_center']
# 共享app配置(用于租户管理)
tenant_shared_apps = ['dvadmin_upgrade_center']
# ================================================= #
# ******************* 插件配置区结束 *****************
# ================================================= #


# ********** 赋值到 settings 中 **********
settings.INSTALLED_APPS += [app for app in apps if app not in settings.INSTALLED_APPS]
settings.TENANT_SHARED_APPS += tenant_shared_apps

# ********** 注册路由 **********
settings.PLUGINS_URL_PATTERNS += plugins_url_patterns
