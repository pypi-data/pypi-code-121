from backports.strenum import StrEnum


class _NameClasses(StrEnum):
    BASE = 'Base'


class _DDLOptions(StrEnum):
    CREATE = 'create'
    DROP_CREATE = 'drop_create'
    FULL_DROP_CREATE = 'full_drop_create'
    TEST = 'test'


class _Config(StrEnum):
    DDL_AUTO_VALUE = 'ddl_auto_value'
    NAME_SHCEMA_MODULE = 'name_shcema_module'
    PROPERTIES_BD_GROUP = 'properties_bd_group'


class _Properties(StrEnum):
    ASC = 'asc'
    DESC = 'desc'
    PATH_MODULE_SCHEMA = 'path_module_schema'
    DDL_AUTO = 'ddl_auto'
    URL_CONNECTION = 'url_connection'


class _Groups(StrEnum):
    BD_CORE = 'BD_CORE'


class _Params(StrEnum):
    PAGE = 'page'
    UUID = 'uuid'
    MODEL = 'model'
    EMAIL = 'email'
    CLASS_ = 'class_'
    AVATAR = 'avatar'
    SESSION = 'session'
    DDL_AUTO = 'ddl_auto'
    PASSWORD = 'password'
    USERNAME = 'username'
    LASTNAME = 'lastname'
    LAST_NAME = 'last_name'
    ORDER_TYPE = 'order_type'
    CLASS_NAME = 'class_name'
    QUERY_DICT = 'query_dict'
    LIST_MODEL = 'list_model'
    FIRST_NAME = 'first_name'
    ORDER_COLUM = 'order_colum'
    CREDIT_CARD = 'credit_card'
    UPDATE_DATA = 'update_data'
    PHONE_NUMBER = 'phone_number'
    ROW_FOR_PAGE = 'row_for_page'
