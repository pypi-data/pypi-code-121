from backports.strenum import StrEnum


class _PropertiesGroups(StrEnum):
    API_TEMPLATE = 'API_TEMPLATE'


class _Params(StrEnum):
    API = 'api'
    GROUPS = 'groups'
    APP_DEBUG = 'debug'
    APP_NAME = 'app_name'
    SECRET_API_KEY = 'secret_api_key'
    PROPAGATE_EXCEPTIONS = 'propagate_exceptions'


class _Properties(StrEnum):
    API_KEY_JSON = 'secret_api_key'
    PATH_RSC_API = 'path_resources_api'


class _ClassName(StrEnum):
    RESOURCE_CLASS_NAME = 'Resource'
