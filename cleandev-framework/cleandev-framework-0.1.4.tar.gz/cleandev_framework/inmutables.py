from backports.strenum import StrEnum

class _PropertiesGroups(StrEnum):
    BD_CORE = 'BD_CORE'
    CLEANDEV_FRAMEWORK = 'CLEANDEV_FRAMEWORK'


class _PropertiesParams(StrEnum):
    PATH_MODULE_SCHEMA = 'path_module_schema'
    CAMEL_CASE_ENABLED = 'camel_case_enabled'

DATA_CLASS_NAME: str = 'DataClass'
MODEL_BASE_CLASS_NAME: str = 'Base'