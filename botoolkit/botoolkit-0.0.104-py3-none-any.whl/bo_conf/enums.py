class WebBBConfigSectionEnum:
    """
    Перечисление секций конфигурационного файла проекта web_bb
    """
    ASYNC_DATABASE = 'async_database'
    SUFD = 'SUFD'
    ACCOUNTING_DB = 'accounting_db'
    ACCOUNTING_OPITONS = 'accounting_opitons'
    ACCOUNTING_OPTIONS = 'accounting_options'
    ACTIVE_USERS = 'active_users'
    ADMIN_PANEL = 'admin_panel'
    BARSAM = 'barsam'
    CATEGORY_DB_MAP = 'category_db_map'
    CONTENT = 'content'
    DATABASE = 'database'
    DATALOGGER = 'datalogger'
    DEMO = 'demo'
    DEVTOOLS = 'devtools'
    DICT_LOGIC = 'dict_logic'
    DISCARD_OS_TRANSFER = 'discard_os_transfer'
    DOWNLOADS = 'downloads'
    FIAS = 'fias'
    FORMAT = 'format'
    GAR = 'gar'
    IMPORT_BUAU = 'import_buau'
    LICENSE = 'license'
    LOGGING = 'logging'
    MEDIA = 'media'
    MIS = 'mis'
    NFS_WAIT = 'nfs_wait'
    NOTIFICATIONS = 'notifications'
    OSS = 'oss'
    PLUGINS = 'plugins'
    PRODUCTION_REQUEST = 'production_request'
    READONLY_DB = 'readonly_db'
    REDIS = 'redis'
    REPLISYNC = 'replisync'
    REPORT_MATERIAL_OBOROTKA = 'report_material_oborotka'
    RIS = 'ris'
    RUNTIME = 'runtime'
    SALARY = 'salary'
    SQL_LOG = 'sql_log'
    SSMP_INTEGRATION = 'ssmp_integration'
    STATIC = 'static'
    STYLE = 'style'
    SVODY = 'svody'
    TAXNET_INTEGRATION = 'taxnet_integration'
    TEMPORARY = 'temporary'
    URLS = 'urls'
    USERS = 'users'
    VEHICLE = 'vehicle'
    WATERFALL = 'waterfall'
    WEBSOCKET = 'websocket'

    values = {
        ASYNC_DATABASE: 'Настройка базы данных для подключения asyncpg',
        SUFD: '',
        ACCOUNTING_DB: '',
        ACCOUNTING_OPITONS: '',
        ACCOUNTING_OPTIONS: '',
        ACTIVE_USERS: '',
        ADMIN_PANEL: '',
        BARSAM: '',
        CATEGORY_DB_MAP: '',
        CONTENT: '',
        DATABASE: '',
        DATALOGGER: '',
        DEMO: '',
        DEVTOOLS: (
            'Дополнительные настройки приложения, расширяющие ту или иную функциональность для более удобной разработки'
        ),
        DICT_LOGIC: '',
        DISCARD_OS_TRANSFER: '',
        DOWNLOADS: '',
        FIAS: '',
        FORMAT: '',
        GAR: 'Настройки подключения к сервису ГАР',
        IMPORT_BUAU: '',
        LICENSE: '',
        LOGGING: '',
        MEDIA: '',
        MIS: '',
        NFS_WAIT: '',
        NOTIFICATIONS: '',
        OSS: '',
        PLUGINS: '',
        PRODUCTION_REQUEST: '',
        READONLY_DB: '',
        REDIS: '',
        REPLISYNC: '',
        REPORT_MATERIAL_OBOROTKA: '',
        RIS: '',
        RUNTIME: '',
        SALARY: '',
        SQL_LOG: 'Настройки для включения логирования, позволяющие увидеть исполняемые в БД запросы',
        SSMP_INTEGRATION: '',
        STATIC: '',
        STYLE: '',
        SVODY: '',
        TAXNET_INTEGRATION: '',
        TEMPORARY: '',
        URLS: '',
        USERS: '',
        VEHICLE: '',
        WATERFALL: '',
        WEBSOCKET: '',
    }


class WebBBConfigOptionEnum:
    """
    Перечисление параметров конфигурационного файла проекта web_bb
    """

    ASYNC_DATABASE___DATABASE_ENGINE = (
        WebBBConfigSectionEnum.ASYNC_DATABASE,
        'database_engine',
    )
    ASYNC_DATABASE___DATABASE_NAME = (
        WebBBConfigSectionEnum.ASYNC_DATABASE,
        'database_name',
    )
    ASYNC_DATABASE___DATABASE_USER = (
        WebBBConfigSectionEnum.ASYNC_DATABASE,
        'database_user',
    )
    ASYNC_DATABASE___DATABASE_PASSWORD = (
        WebBBConfigSectionEnum.ASYNC_DATABASE,
        'database_password',
    )
    ASYNC_DATABASE___DATABASE_HOST = (
        WebBBConfigSectionEnum.ASYNC_DATABASE,
        'database_host',
    )
    ASYNC_DATABASE___DATABASE_PORT = (
        WebBBConfigSectionEnum.ASYNC_DATABASE,
        'database_port',
    )
    ASYNC_DATABASE___DATABASE_DISABLE_SERVER_SIDE_CURSORS = (
        WebBBConfigSectionEnum.ASYNC_DATABASE,
        'database_disable_server_side_cursors',
    )
    SUFD___SERVER_URL = (
        WebBBConfigSectionEnum.SUFD,
        'server_url',
    )
    ACCOUNTING_DB___URL = (
        WebBBConfigSectionEnum.ACCOUNTING_DB,
        'url',
    )
    ACCOUNTING_OPITONS___HIDE_NUMBERS_OPERATIONS_JOURNAL = (
        WebBBConfigSectionEnum.ACCOUNTING_OPITONS,
        'hide_numbers_operations_journal',
    )
    ACCOUNTING_OPITONS___WITH_JOURNAL = (
        WebBBConfigSectionEnum.ACCOUNTING_OPITONS,
        'with_journal',
    )
    ACCOUNTING_OPTIONS___BATCH_PROCESSING_CONTRACT = (
        WebBBConfigSectionEnum.ACCOUNTING_OPTIONS,
        'batch_processing_contract',
    )
    ACCOUNTING_OPTIONS___BATCH_PROCESSING_CONTRACT_YEAR = (
        WebBBConfigSectionEnum.ACCOUNTING_OPTIONS,
        'batch_processing_contract_year',
    )
    ACCOUNTING_OPTIONS___HIDE_NUMBERS_OPERATIONS_JOURNAL = (
        WebBBConfigSectionEnum.ACCOUNTING_OPTIONS,
        'hide_numbers_operations_journal',
    )
    ACCOUNTING_OPTIONS___HIDE_NUMBERS_OPERATIONS_JOURNAL_CHECKBOX = (
        WebBBConfigSectionEnum.ACCOUNTING_OPTIONS,
        'hide_numbers_operations_journal_checkbox',
    )
    ACCOUNTING_OPTIONS___STRICT_REPORT_REG = (
        WebBBConfigSectionEnum.ACCOUNTING_OPTIONS,
        'strict_report_reg',
    )
    ACCOUNTING_OPTIONS___WITH_JOURNAL = (
        WebBBConfigSectionEnum.ACCOUNTING_OPTIONS,
        'with_journal',
    )
    ACTIVE_USERS___USE = (
        WebBBConfigSectionEnum.ACTIVE_USERS,
        'use',
    )
    ADMIN_PANEL___ALLOW_COMMANDS = (
        WebBBConfigSectionEnum.ADMIN_PANEL,
        'allow_commands',
    )
    ADMIN_PANEL___FORCE_USE = (
        WebBBConfigSectionEnum.ADMIN_PANEL,
        'force_use',
    )
    ADMIN_PANEL___USERNAME = (
        WebBBConfigSectionEnum.ADMIN_PANEL,
        'username',
    )
    BARSAM___PATH = (
        WebBBConfigSectionEnum.BARSAM,
        'path',
    )
    BARSAM___USE = (
        WebBBConfigSectionEnum.BARSAM,
        'use',
    )
    CATEGORY_DB_MAP___ACCOUNTING_READONLY = (
        WebBBConfigSectionEnum.CATEGORY_DB_MAP,
        'accounting_readonly',
    )
    CATEGORY_DB_MAP___ACCOUNTING_READONLY_WRITE = (
        WebBBConfigSectionEnum.CATEGORY_DB_MAP,
        'accounting_readonly_write',
    )
    CATEGORY_DB_MAP___CORE_READONLY = (
        WebBBConfigSectionEnum.CATEGORY_DB_MAP,
        'core_readonly',
    )
    CATEGORY_DB_MAP___CORE_READONLY_WRITE = (
        WebBBConfigSectionEnum.CATEGORY_DB_MAP,
        'core_readonly_write',
    )
    CATEGORY_DB_MAP___READONLY = (
        WebBBConfigSectionEnum.CATEGORY_DB_MAP,
        'readonly',
    )
    CATEGORY_DB_MAP___READONLY_WRITE = (
        WebBBConfigSectionEnum.CATEGORY_DB_MAP,
        'readonly_write',
    )
    CATEGORY_DB_MAP___SALARY_READONLY = (
        WebBBConfigSectionEnum.CATEGORY_DB_MAP,
        'salary_readonly',
    )
    CATEGORY_DB_MAP___SALARY_READONLY_WRITE = (
        WebBBConfigSectionEnum.CATEGORY_DB_MAP,
        'salary_readonly_write',
    )
    CONTENT___DATA_MAX_NUMBER_FIELDS = (
        WebBBConfigSectionEnum.CONTENT,
        'data_max_number_fields',
    )
    DATABASE___DATABASE_ENGINE = (
        WebBBConfigSectionEnum.DATABASE,
        'database_engine',
    )
    DATABASE___DATABASE_HOST = (
        WebBBConfigSectionEnum.DATABASE,
        'database_host',
    )
    DATABASE___DATABASE_NAME = (
        WebBBConfigSectionEnum.DATABASE,
        'database_name',
    )
    DATABASE___DATABASE_PASSWORD = (
        WebBBConfigSectionEnum.DATABASE,
        'database_password',
    )
    DATABASE___DATABASE_PORT = (
        WebBBConfigSectionEnum.DATABASE,
        'database_port',
    )
    DATABASE___DATABASE_USER = (
        WebBBConfigSectionEnum.DATABASE,
        'database_user',
    )
    DATABASE___EXTERNAL = (
        WebBBConfigSectionEnum.DATABASE,
        'external',
    )
    DATALOGGER___DATABASE_ENGINE = (
        WebBBConfigSectionEnum.DATALOGGER,
        'database_engine',
    )
    DATALOGGER___DATABASE_HOST = (
        WebBBConfigSectionEnum.DATALOGGER,
        'database_host',
    )
    DATALOGGER___DATABASE_NAME = (
        WebBBConfigSectionEnum.DATALOGGER,
        'database_name',
    )
    DATALOGGER___DATABASE_PASSWORD = (
        WebBBConfigSectionEnum.DATALOGGER,
        'database_password',
    )
    DATALOGGER___DATABASE_PORT = (
        WebBBConfigSectionEnum.DATALOGGER,
        'database_port',
    )
    DATALOGGER___DATABASE_USER = (
        WebBBConfigSectionEnum.DATALOGGER,
        'database_user',
    )
    DATALOGGER___SHUTUP = (
        WebBBConfigSectionEnum.DATALOGGER,
        'shutup',
    )
    DEMO___PASSWORD = (
        WebBBConfigSectionEnum.DEMO,
        'password',
    )
    DEMO___USER = (
        WebBBConfigSectionEnum.DEMO,
        'user',
    )
    DEVTOOLS___PROFILING = (
        WebBBConfigSectionEnum.DEVTOOLS,
        'profiling',
    )
    DEVTOOLS___TRACE_ACTION = (
        WebBBConfigSectionEnum.DEVTOOLS,
        'trace_action'
    )
    DEVTOOLS___USE_SOURCE_URL_JS = (
        WebBBConfigSectionEnum.DEVTOOLS,
        'use_source_url_js',
    )
    DICT_LOGIC___ALLOW_SUPPLIER_ZERO_INN = (
        WebBBConfigSectionEnum.DICT_LOGIC,
        'allow_supplier_zero_inn',
    )
    DICT_LOGIC___ALLOW_SUPPLIER_ZERO_INN_KPP = (
        WebBBConfigSectionEnum.DICT_LOGIC,
        'allow_supplier_zero_inn_kpp',
    )
    DICT_LOGIC___SKIP_KBK_VALIDATION = (
        WebBBConfigSectionEnum.DICT_LOGIC,
        'skip_kbk_validation',
    )
    DISCARD_OS_TRANSFER___USERNAME = (
        WebBBConfigSectionEnum.DISCARD_OS_TRANSFER,
        'username',
    )
    DOWNLOADS___ROOT = (
        WebBBConfigSectionEnum.DOWNLOADS,
        'root',
    )
    DOWNLOADS___URL = (
        WebBBConfigSectionEnum.DOWNLOADS,
        'url',
    )
    FIAS___API_URL = (
        WebBBConfigSectionEnum.FIAS,
        'api_url',
    )
    FIAS___CACHE_PREFIX = (
        WebBBConfigSectionEnum.FIAS,
        'cache_prefix',
    )
    FIAS___CACHE_TIMEOUT = (
        WebBBConfigSectionEnum.FIAS,
        'cache_timeout',
    )
    FIAS___DATABASE_ENGINE = (
        WebBBConfigSectionEnum.FIAS,
        'database_engine',
    )
    FIAS___DATABASE_HOST = (
        WebBBConfigSectionEnum.FIAS,
        'database_host',
    )
    FIAS___DATABASE_NAME = (
        WebBBConfigSectionEnum.FIAS,
        'database_name',
    )
    FIAS___DATABASE_PASSWORD = (
        WebBBConfigSectionEnum.FIAS,
        'database_password',
    )
    FIAS___DATABASE_PORT = (
        WebBBConfigSectionEnum.FIAS,
        'database_port',
    )
    FIAS___DATABASE_USER = (
        WebBBConfigSectionEnum.FIAS,
        'database_user',
    )
    FIAS___DEDICATED_DB = (
        WebBBConfigSectionEnum.FIAS,
        'dedicated_db',
    )
    FIAS___SHOW_KLADR_FIELD = (
        WebBBConfigSectionEnum.FIAS,
        'show_kladr_field',
    )
    FORMAT___DATE_FORMAT = (
        WebBBConfigSectionEnum.FORMAT,
        'date_format',
    )
    GAR___API_URL = (
        WebBBConfigSectionEnum.GAR,
        'api_url',
    )
    GAR___USE_CACHE = (
        WebBBConfigSectionEnum.GAR,
        'use_cache',
    )
    GAR___TIMEOUT = (
        WebBBConfigSectionEnum.GAR,
        'timeout',
    )
    GAR___PAGE_LIMIT = (
        WebBBConfigSectionEnum.GAR,
        'page_limit',
    )
    GAR___TOKEN_URL = (
        WebBBConfigSectionEnum.GAR,
        'token_url',
    )
    GAR___CLIENT_ID = (
        WebBBConfigSectionEnum.GAR,
        'client_id',
    )
    GAR___CLIENT_SECRET = (
        WebBBConfigSectionEnum.GAR,
        'client_secret',
    )
    GAR___USERNAME = (
        WebBBConfigSectionEnum.GAR,
        'username',
    )
    GAR___PASSWORD = (
        WebBBConfigSectionEnum.GAR,
        'password',
    )
    GAR___BACKEND = (
        WebBBConfigSectionEnum.GAR,
        'backend',
    )
    GAR___USE_SIMPLE_SERVER = (
        WebBBConfigSectionEnum.GAR,
        'use_simple_server',
    )
    IMPORT_BUAU___ALLOW_CONTRACTS = (
        WebBBConfigSectionEnum.IMPORT_BUAU,
        'allow_contracts',
    )
    LICENSE___KEY_FILE = (
        WebBBConfigSectionEnum.LICENSE,
        'key_file',
    )
    LOGGING___LOG_ACC_ENTRY_DELETION = (
        WebBBConfigSectionEnum.LOGGING,
        'log_acc_entry_deletion',
    )
    LOGGING___LOG_PATH = (
        WebBBConfigSectionEnum.LOGGING,
        'log_path',
    )
    LOGGING___MONITORING = (
        WebBBConfigSectionEnum.LOGGING,
        'monitoring',
    )
    LOGGING___PRODUCTION_REQUEST = (
        WebBBConfigSectionEnum.LOGGING,
        'production_request',
    )
    LOGGING___PRODUCTION_REQUEST_CLIENT_INTERVAL = (
        WebBBConfigSectionEnum.LOGGING,
        'production_request_client_interval',
    )
    LOGGING___SENTRY_ORG = (
        WebBBConfigSectionEnum.LOGGING,
        'sentry_org',
    )
    LOGGING___SENTRY_SERVER = (
        WebBBConfigSectionEnum.LOGGING,
        'sentry_server',
    )
    MEDIA___ROOT = (
        WebBBConfigSectionEnum.MEDIA,
        'root',
    )
    MEDIA___URL = (
        WebBBConfigSectionEnum.MEDIA,
        'url',
    )
    MIS___HARDCODE_ENT = (
        WebBBConfigSectionEnum.MIS,
        'hardcode_ent',
    )
    MIS___MIS_PAID_SERVICES_AUTH = (
        WebBBConfigSectionEnum.MIS,
        'mis_paid_services_auth',
    )
    MIS___MIS_PAID_SERVICES_LOGIN = (
        WebBBConfigSectionEnum.MIS,
        'mis_paid_services_login',
    )
    MIS___MIS_PAID_SERVICES_PASSWORD = (
        WebBBConfigSectionEnum.MIS,
        'mis_paid_services_password',
    )
    MIS___MIS_PAID_SERVICES_SERVER = (
        WebBBConfigSectionEnum.MIS,
        'mis_paid_services_server',
    )
    MIS___MIS_SERVER = (
        WebBBConfigSectionEnum.MIS,
        'mis_server',
    )
    MIS___MIS_SYNC_CONTRACT_AUTH = (
        WebBBConfigSectionEnum.MIS,
        'mis_sync_contract_auth',
    )
    MIS___MIS_SYNC_CONTRACT_SEND = (
        WebBBConfigSectionEnum.MIS,
        'mis_sync_contract_send',
    )
    NFS_WAIT___NFS_MAX_COUNT = (
        WebBBConfigSectionEnum.NFS_WAIT,
        'nfs_max_count',
    )
    NFS_WAIT___NFS_PAUSE = (
        WebBBConfigSectionEnum.NFS_WAIT,
        'nfs_pause',
    )
    NOTIFICATIONS___EMAIL_BACKEND = (
        WebBBConfigSectionEnum.NOTIFICATIONS,
        'email_backend',
    )
    NOTIFICATIONS___EMAIL_FILE_PATH = (
        WebBBConfigSectionEnum.NOTIFICATIONS,
        'email_file_path',
    )
    NOTIFICATIONS___EMAIL_FROM = (
        WebBBConfigSectionEnum.NOTIFICATIONS,
        'email_from',
    )
    NOTIFICATIONS___EMAIL_HOST = (
        WebBBConfigSectionEnum.NOTIFICATIONS,
        'email_host',
    )
    NOTIFICATIONS___EMAIL_HOST_PASSWORD = (
        WebBBConfigSectionEnum.NOTIFICATIONS,
        'email_host_password',
    )
    NOTIFICATIONS___EMAIL_HOST_USER = (
        WebBBConfigSectionEnum.NOTIFICATIONS,
        'email_host_user',
    )
    NOTIFICATIONS___EMAIL_PORT = (
        WebBBConfigSectionEnum.NOTIFICATIONS,
        'email_port',
    )
    NOTIFICATIONS___EMAIL_USE_SSL = (
        WebBBConfigSectionEnum.NOTIFICATIONS,
        'email_use_ssl',
    )
    NOTIFICATIONS___EMAIL_USE_TLS = (
        WebBBConfigSectionEnum.NOTIFICATIONS,
        'email_use_tls',
    )
    NOTIFICATIONS___USE_EMAIL_NOTIFICATION = (
        WebBBConfigSectionEnum.NOTIFICATIONS,
        'use_email_notification',
    )
    OSS___URL = (
        WebBBConfigSectionEnum.OSS,
        'url',
    )
    PLUGINS___ACTIVATED_PLUGINS = (
        WebBBConfigSectionEnum.PLUGINS,
        'activated_plugins',
    )
    PLUGINS___RMR_URL = (
        WebBBConfigSectionEnum.PLUGINS,
        'rmr_url',
    )
    PLUGINS___USE_PLUGIN_DISPATCHER = (
        WebBBConfigSectionEnum.PLUGINS,
        'use_plugin_dispatcher',
    )
    PRODUCTION_REQUEST___CLIENT_INTERVAL = (
        WebBBConfigSectionEnum.PRODUCTION_REQUEST,
        'client_interval',
    )
    PRODUCTION_REQUEST___LOG_CLIENT = (
        WebBBConfigSectionEnum.PRODUCTION_REQUEST,
        'log_client',
    )
    PRODUCTION_REQUEST___LOG_SERVER = (
        WebBBConfigSectionEnum.PRODUCTION_REQUEST,
        'log_server',
    )
    PRODUCTION_REQUEST___PRODUCTION_REQUEST_CLIENT_INTERVAL = (
        WebBBConfigSectionEnum.PRODUCTION_REQUEST,
        'production_request_client_interval',
    )
    PRODUCTION_REQUEST___PRODUCTION_REQUEST_LOG_MEMORY = (
        WebBBConfigSectionEnum.PRODUCTION_REQUEST,
        'production_request_log_memory',
    )
    READONLY_DB___ALIAS = (
        WebBBConfigSectionEnum.READONLY_DB,
        'alias',
    )
    READONLY_DB___DATABASE_ENGINE = (
        WebBBConfigSectionEnum.READONLY_DB,
        'database_engine',
    )
    READONLY_DB___DATABASE_HOST = (
        WebBBConfigSectionEnum.READONLY_DB,
        'database_host',
    )
    READONLY_DB___DATABASE_NAME = (
        WebBBConfigSectionEnum.READONLY_DB,
        'database_name',
    )
    READONLY_DB___DATABASE_PASSWORD = (
        WebBBConfigSectionEnum.READONLY_DB,
        'database_password',
    )
    READONLY_DB___DATABASE_PORT = (
        WebBBConfigSectionEnum.READONLY_DB,
        'database_port',
    )
    READONLY_DB___DATABASE_USER = (
        WebBBConfigSectionEnum.READONLY_DB,
        'database_user',
    )
    READONLY_DB___URL = (
        WebBBConfigSectionEnum.READONLY_DB,
        'url',
    )
    REDIS___REDIS_HOST = (
        WebBBConfigSectionEnum.REDIS,
        'redis_host',
    )
    REPLISYNC___SYNC_TABLES_FILE_PATH = (
        WebBBConfigSectionEnum.REPLISYNC,
        'sync_tables_file_path',
    )
    REPORT_MATERIAL_OBOROTKA___PRODUCT_SUM_ACCOUNTING_USAGE = (
        WebBBConfigSectionEnum.REPORT_MATERIAL_OBOROTKA,
        'product_sum_accounting_usage',
    )
    RIS___AUTH_SERVICE = (
        WebBBConfigSectionEnum.RIS,
        'auth_service',
    )
    RIS___GET_BILLS_SERVICE = (
        WebBBConfigSectionEnum.RIS,
        'get_bills_service',
    )
    RIS___LOGIN = (
        WebBBConfigSectionEnum.RIS,
        'login',
    )
    RIS___PASSWORD = (
        WebBBConfigSectionEnum.RIS,
        'password',
    )
    RIS___URL = (
        WebBBConfigSectionEnum.RIS,
        'url',
    )
    RUNTIME___APP_CONFIG_UUID = (
        WebBBConfigSectionEnum.RUNTIME,
        'app_config_uuid',
    )
    RUNTIME___APP_REGION_ABBREVIATION = (
        WebBBConfigSectionEnum.RUNTIME,
        'app_region_abbreviation',
    )
    RUNTIME___DEBUG = (
        WebBBConfigSectionEnum.RUNTIME,
        'debug',
    )
    RUNTIME___MONITORING = (
        WebBBConfigSectionEnum.RUNTIME,
        'monitoring',
    )
    RUNTIME___SESSION_COOKIE_NAME = (
        WebBBConfigSectionEnum.RUNTIME,
        'session_cookie_name',
    )
    RUNTIME___TEST_APPLICATION = (
        WebBBConfigSectionEnum.RUNTIME,
        'test_application',
    )
    RUNTIME___TEST_MODE = (
        WebBBConfigSectionEnum.RUNTIME,
        'test_mode',
    )
    RUNTIME___TIME_ZONE = (
        WebBBConfigSectionEnum.RUNTIME,
        'time_zone',
    )
    RUNTIME___USE_MEMCACHE = (
        WebBBConfigSectionEnum.RUNTIME,
        'use_memcache',
    )
    RUNTIME___WITH_ACCOUNT_ANALYSIS = (
        WebBBConfigSectionEnum.RUNTIME,
        'with_account_analysis',
    )
    SALARY___DESKTOP_HTML_NAME = (
        WebBBConfigSectionEnum.SALARY,
        'desktop_html_name',
    )
    SALARY___DICT_IMPORT_SERVICE = (
        WebBBConfigSectionEnum.SALARY,
        'dict_import_service',
    )
    SALARY___ENABLE_RMR_INTEGRATION = (
        WebBBConfigSectionEnum.SALARY,
        'enable_rmr_integration',
    )
    SALARY___IGNORE_MIGRATION = (
        WebBBConfigSectionEnum.SALARY,
        'ignore_migration',
    )
    SALARY___LOGIN_HTML_NAME = (
        WebBBConfigSectionEnum.SALARY,
        'login_html_name',
    )
    SALARY___LOGO_STYLE = (
        WebBBConfigSectionEnum.SALARY,
        'logo_style',
    )
    SALARY___MAX_ELEMENT_IN_QUEUE = (
        WebBBConfigSectionEnum.SALARY,
        'max_element_in_queue',
    )
    SALARY___PAYROLL_CALC_IDLE_LOOPS = (
        WebBBConfigSectionEnum.SALARY,
        'payroll_calc_idle_loops',
    )
    SALARY___RMR_URL = (
        WebBBConfigSectionEnum.SALARY,
        'rmr_url',
    )
    SALARY___SVODY_REPORT_URL = (
        WebBBConfigSectionEnum.SALARY,
        'svody_report_url',
    )
    SQL_LOG___ENABLE = (
        WebBBConfigSectionEnum.SQL_LOG,
        'enable',
    )
    SQL_LOG___TRACEBACK = (
        WebBBConfigSectionEnum.SQL_LOG,
        'traceback',
    )
    SQL_LOG___MAX_SIZE = (
        WebBBConfigSectionEnum.SQL_LOG,
        'max_size',
    )
    SSMP_INTEGRATION___ACTIVE = (
        WebBBConfigSectionEnum.SSMP_INTEGRATION,
        'active',
    )
    SSMP_INTEGRATION___CONSOLE_LOG = (
        WebBBConfigSectionEnum.SSMP_INTEGRATION,
        'console_log',
    )
    STATIC___ROOT = (
        WebBBConfigSectionEnum.STATIC,
        'root',
    )
    STATIC___URL = (
        WebBBConfigSectionEnum.STATIC,
        'url',
    )
    STYLE___DESKTOP_HTML_NAME = (
        WebBBConfigSectionEnum.STYLE,
        'desktop_html_name',
    )
    STYLE___HIDE_BUH_DESKTOP = (
        WebBBConfigSectionEnum.STYLE,
        'hide_buh_desktop',
    )
    STYLE___HIDE_VERSION_CHANGES = (
        WebBBConfigSectionEnum.STYLE,
        'hide_version_changes',
    )
    STYLE___LOGIN_BACKGROUND_STYLE = (
        WebBBConfigSectionEnum.STYLE,
        'login_background_style',
    )
    STYLE___LOGIN_CLOUD_STYLE = (
        WebBBConfigSectionEnum.STYLE,
        'login_cloud_style',
    )
    STYLE___LOGIN_HTML_FOOD_NAME = (
        WebBBConfigSectionEnum.STYLE,
        'login_html_food_name',
    )
    STYLE___LOGIN_HTML_NAME = (
        WebBBConfigSectionEnum.STYLE,
        'login_html_name',
    )
    STYLE___LOGIN_HTML_VEHICLE_NAME = (
        WebBBConfigSectionEnum.STYLE,
        'login_html_vehicle_name',
    )
    STYLE___LOGO_BARS_STYLE = (
        WebBBConfigSectionEnum.STYLE,
        'logo_bars_style',
    )
    STYLE___LOGO_STYLE = (
        WebBBConfigSectionEnum.STYLE,
        'logo_style',
    )
    STYLE___SNOW_MODE_COUNT = (
        WebBBConfigSectionEnum.STYLE,
        'snow_mode_count',
    )
    STYLE___SNOW_MODE_ON = (
        WebBBConfigSectionEnum.STYLE,
        'snow_mode_on',
    )
    STYLE___TEST_APPLICATION_TEXT = (
        WebBBConfigSectionEnum.STYLE,
        'test_application_text',
    )
    SVODY___CREATE_USER = (
        WebBBConfigSectionEnum.SVODY,
        'create_user',
    )
    SVODY___ROLES = (
        WebBBConfigSectionEnum.SVODY,
        'roles',
    )
    SVODY___URL = (
        WebBBConfigSectionEnum.SVODY,
        'url',
    )
    SVODY___USE_EMPTY_ENTERPRISE = (
        WebBBConfigSectionEnum.SVODY,
        'use_empty_enterprise',
    )
    TAXNET_INTEGRATION___DOCS_ALLOWED_REQUESTS_TIME_RANGE = (
        WebBBConfigSectionEnum.TAXNET_INTEGRATION,
        'docs_allowed_requests_time_range',
    )
    TAXNET_INTEGRATION___DOCS_BEAT_INTERVAL = (
        WebBBConfigSectionEnum.TAXNET_INTEGRATION,
        'docs_beat_interval',
    )
    TAXNET_INTEGRATION___DOCS_CHECK_HANG_INTERVAL = (
        WebBBConfigSectionEnum.TAXNET_INTEGRATION,
        'docs_check_hang_interval',
    )
    TAXNET_INTEGRATION___DOCS_FIRST_RETRY_AFTER = (
        WebBBConfigSectionEnum.TAXNET_INTEGRATION,
        'docs_first_retry_after',
    )
    TAXNET_INTEGRATION___DOCS_LOGIN = (
        WebBBConfigSectionEnum.TAXNET_INTEGRATION,
        'docs_login',
    )
    TAXNET_INTEGRATION___DOCS_MAX_RETRIES = (
        WebBBConfigSectionEnum.TAXNET_INTEGRATION,
        'docs_max_retries',
    )
    TAXNET_INTEGRATION___DOCS_PASSWORD = (
        WebBBConfigSectionEnum.TAXNET_INTEGRATION,
        'docs_password',
    )
    TAXNET_INTEGRATION___DOCS_REQUEST_TIMEOUT = (
        WebBBConfigSectionEnum.TAXNET_INTEGRATION,
        'docs_request_timeout',
    )
    TAXNET_INTEGRATION___DOCS_RESYNC_TIME = (
        WebBBConfigSectionEnum.TAXNET_INTEGRATION,
        'docs_resync_time',
    )
    TAXNET_INTEGRATION___DOCS_RETRY_MULTIPLIER = (
        WebBBConfigSectionEnum.TAXNET_INTEGRATION,
        'docs_retry_multiplier',
    )
    TAXNET_INTEGRATION___DOCS_URL = (
        WebBBConfigSectionEnum.TAXNET_INTEGRATION,
        'docs_url',
    )
    TEMPORARY___ROOT = (
        WebBBConfigSectionEnum.TEMPORARY,
        'root',
    )
    URLS___DOWNLOADS = (
        WebBBConfigSectionEnum.URLS,
        'downloads',
    )
    URLS___HELP = (
        WebBBConfigSectionEnum.URLS,
        'help',
    )
    URLS___HELP_SALARY = (
        WebBBConfigSectionEnum.URLS,
        'help_salary',
    )
    URLS___M3STATIC = (
        WebBBConfigSectionEnum.URLS,
        'm3static',
    )
    URLS___ROOT = (
        WebBBConfigSectionEnum.URLS,
        'root',
    )
    URLS___STATIC = (
        WebBBConfigSectionEnum.URLS,
        'static',
    )
    USERS___INACTIVE_SESSION_LIFETIME = (
        WebBBConfigSectionEnum.USERS,
        'inactive_session_lifetime',
    )
    USERS___LOG_OS = (
        WebBBConfigSectionEnum.USERS,
        'log_os',
    )
    VEHICLE___USE_WAYBILL_COPY = (
        WebBBConfigSectionEnum.VEHICLE,
        'use_waybill_copy',
    )
    WATERFALL___BACKGROUND_PROCESS_PANEL_UPDATING_INTERVAL = (
        WebBBConfigSectionEnum.WATERFALL,
        'background_process_panel_updating_interval',
    )
    WATERFALL___CELERY_BROKER_URL = (
        WebBBConfigSectionEnum.WATERFALL,
        'celery_broker_url',
    )
    WATERFALL___CELERY_ALWAYS_EAGER = (
        WebBBConfigSectionEnum.WATERFALL,
        'celery_always_eager',
    )
    WATERFALL___CELERYD_TASK_SOFT_TIME_LIMIT = (
        WebBBConfigSectionEnum.WATERFALL,
        'celeryd_task_soft_time_limit',
    )
    WATERFALL___DISTRIBUTED_CELERY_DAEMONS = (
        WebBBConfigSectionEnum.WATERFALL,
        'distributed_celery_daemons',
    )
    WATERFALL___ENABLE_BACKGROUND_PROCESS_PANEL = (
        WebBBConfigSectionEnum.WATERFALL,
        'enable_background_process_panel',
    )
    WATERFALL___TASK_TIME_LIMIT = (
        WebBBConfigSectionEnum.WATERFALL,
        'task_time_limit',
    )
    WATERFALL___USE_WEBSOCKET = (
        WebBBConfigSectionEnum.WATERFALL,
        'use_websocket',
    )
    WATERFALL___WORKER_DEADLINE = (
        WebBBConfigSectionEnum.WATERFALL,
        'worker_deadline',
    )
    WATERFALL___WTF_ASYNC = (
        WebBBConfigSectionEnum.WATERFALL,
        'wtf_async',
    )
    WATERFALL___WTF_REPORT_LIFETIME = (
        WebBBConfigSectionEnum.WATERFALL,
        'wtf_report_lifetime',
    )
    WATERFALL___WTF_SSE_STREAM = (
        WebBBConfigSectionEnum.WATERFALL,
        'wtf_sse_stream',
    )
    WEBSOCKET___3SERVER = (
        WebBBConfigSectionEnum.WEBSOCKET,
        '3server',
    )
    WEBSOCKET___WEBSOCKET_BACKEND = (
        WebBBConfigSectionEnum.WEBSOCKET,
        'websocket_backend',
    )
    WEBSOCKET___WEBSOCKET_PORT = (
        WebBBConfigSectionEnum.WEBSOCKET,
        'websocket_port',
    )
    WEBSOCKET___WEBSOCKET_QUEUE_HOST = (
        WebBBConfigSectionEnum.WEBSOCKET,
        'websocket_queue_host',
    )
    WEBSOCKET___WEBSOCKET_QUEUE_PORT = (
        WebBBConfigSectionEnum.WEBSOCKET,
        'websocket_queue_port',
    )
    WEBSOCKET___WEBSOCKET_URL = (
        WebBBConfigSectionEnum.WEBSOCKET,
        'websocket_url',
    )

    BARSDOCK_OPTIONS = [
        ASYNC_DATABASE___DATABASE_ENGINE,
        ASYNC_DATABASE___DATABASE_NAME,
        ASYNC_DATABASE___DATABASE_USER,
        ASYNC_DATABASE___DATABASE_PASSWORD,
        ASYNC_DATABASE___DATABASE_HOST,
        ASYNC_DATABASE___DATABASE_PORT,
        ASYNC_DATABASE___DATABASE_DISABLE_SERVER_SIDE_CURSORS,
        DATABASE___DATABASE_ENGINE,
        DATABASE___DATABASE_HOST,
        DATABASE___DATABASE_NAME,
        DATABASE___DATABASE_PASSWORD,
        DATABASE___DATABASE_PORT,
        DATABASE___DATABASE_USER,
        DEVTOOLS___TRACE_ACTION,
        DEVTOOLS___PROFILING,
        DEVTOOLS___USE_SOURCE_URL_JS,
        GAR___API_URL,
        GAR___USE_CACHE,
        GAR___TIMEOUT,
        GAR___PAGE_LIMIT,
        GAR___TOKEN_URL,
        GAR___CLIENT_ID,
        GAR___CLIENT_SECRET,
        GAR___USERNAME,
        GAR___PASSWORD,
        GAR___BACKEND,
        GAR___USE_SIMPLE_SERVER,
        PLUGINS___ACTIVATED_PLUGINS,
        RUNTIME___DEBUG,
        RUNTIME___TEST_APPLICATION,
        RUNTIME___TIME_ZONE,
        SQL_LOG___ENABLE,
        SQL_LOG___MAX_SIZE,
        SQL_LOG___TRACEBACK,
        WATERFALL___BACKGROUND_PROCESS_PANEL_UPDATING_INTERVAL,
        WATERFALL___CELERY_ALWAYS_EAGER,
        WATERFALL___ENABLE_BACKGROUND_PROCESS_PANEL,
        WATERFALL___TASK_TIME_LIMIT,
        WATERFALL___USE_WEBSOCKET,
    ]

    values = {
        ASYNC_DATABASE___DATABASE_ENGINE: (
            'СУБД, которая используется в системе. По умолчанию: web_bb.db_wrapper.postgresql_psycopg2_with_hooks.'
        ),
        ASYNC_DATABASE___DATABASE_NAME: (
            'Наименование базы данных. Укажите имя базы данных, которую Вы создали для хранения данных проекта. По '
            'вумолчанию: bars_web_bb.'
        ),
        ASYNC_DATABASE___DATABASE_USER: (
            'Пользователь СУБД, от имени которого происходит подключение к базе данных. По умолчанию: bars_web_bb.'
        ),
        ASYNC_DATABASE___DATABASE_PASSWORD: (
            'Пароль пользователя СУБД, который используется при подключении к СУБД. По умолчанию: bars_web_bb.'
        ),
        ASYNC_DATABASE___DATABASE_HOST: (
            'Имя контейнера или IP адрес сервера, на котором располагается СУБД. По умолчанию: database, если '
            'используется barsdock или 127.0.0.1.'
        ),
        ASYNC_DATABASE___DATABASE_PORT: (
            'Порт, используемый для подключения к серверу базы данных. По умолчанию: 5432.'
        ),
        ASYNC_DATABASE___DATABASE_DISABLE_SERVER_SIDE_CURSORS: 'Выключить ли server side курсоры. По умолчанию: False.',
        SUFD___SERVER_URL: '',
        ACCOUNTING_DB___URL: '',
        ACCOUNTING_OPITONS___HIDE_NUMBERS_OPERATIONS_JOURNAL: '',
        ACCOUNTING_OPITONS___WITH_JOURNAL: '',
        ACCOUNTING_OPTIONS___BATCH_PROCESSING_CONTRACT: '',
        ACCOUNTING_OPTIONS___BATCH_PROCESSING_CONTRACT_YEAR: '',
        ACCOUNTING_OPTIONS___HIDE_NUMBERS_OPERATIONS_JOURNAL: '',
        ACCOUNTING_OPTIONS___HIDE_NUMBERS_OPERATIONS_JOURNAL_CHECKBOX: '',
        ACCOUNTING_OPTIONS___STRICT_REPORT_REG: '',
        ACCOUNTING_OPTIONS___WITH_JOURNAL: '',
        ACTIVE_USERS___USE: '',
        ADMIN_PANEL___ALLOW_COMMANDS: '',
        ADMIN_PANEL___FORCE_USE: '',
        ADMIN_PANEL___USERNAME: '',
        BARSAM___PATH: '',
        BARSAM___USE: '',
        CATEGORY_DB_MAP___ACCOUNTING_READONLY: '',
        CATEGORY_DB_MAP___ACCOUNTING_READONLY_WRITE: '',
        CATEGORY_DB_MAP___CORE_READONLY: '',
        CATEGORY_DB_MAP___CORE_READONLY_WRITE: '',
        CATEGORY_DB_MAP___READONLY: '',
        CATEGORY_DB_MAP___READONLY_WRITE: '',
        CATEGORY_DB_MAP___SALARY_READONLY: '',
        CATEGORY_DB_MAP___SALARY_READONLY_WRITE: '',
        CONTENT___DATA_MAX_NUMBER_FIELDS: '',
        DATABASE___DATABASE_ENGINE: 'Движок для работы с базой данных',
        DATABASE___DATABASE_HOST: 'Порт для подключения к базе данных',
        DATABASE___DATABASE_NAME: 'Имя базы данных',
        DATABASE___DATABASE_PASSWORD: 'Пароль пользователя для подключения к базе данных',
        DATABASE___DATABASE_PORT: 'Порт подключения к базе данных',
        DATABASE___DATABASE_USER: 'Пользователь подключения к базе данных',
        DATABASE___EXTERNAL: '',
        DATALOGGER___DATABASE_ENGINE: '',
        DATALOGGER___DATABASE_HOST: '',
        DATALOGGER___DATABASE_NAME: '',
        DATALOGGER___DATABASE_PASSWORD: '',
        DATALOGGER___DATABASE_PORT: '',
        DATALOGGER___DATABASE_USER: '',
        DATALOGGER___SHUTUP: '',
        DEMO___PASSWORD: '',
        DEMO___USER: '',
        DEVTOOLS___PROFILING: 'Включает режим профилирования. По умолчанию: False',
        DEVTOOLS___TRACE_ACTION: (
            'Включает вывод в консоль информации о месте нахождения запрошенного действия (пак, действие, метод). По '
            'умолчанию: False'
        ),
        DEVTOOLS___USE_SOURCE_URL_JS: (
            'Указание sourceURL в генерируемых js-файлах. Облегчает отладку кода фронта, т.к. в трейсе явно '
            'указывается файл с упавшим кодом. Механизм иногда вызывает ошибку парсинга кода. В этом случае его '
            'не получится использовать. По умолчанию: False'
        ),
        DICT_LOGIC___ALLOW_SUPPLIER_ZERO_INN: '',
        DICT_LOGIC___ALLOW_SUPPLIER_ZERO_INN_KPP: '',
        DICT_LOGIC___SKIP_KBK_VALIDATION: '',
        DISCARD_OS_TRANSFER___USERNAME: '',
        DOWNLOADS___ROOT: '',
        DOWNLOADS___URL: '',
        FIAS___API_URL: '',
        FIAS___CACHE_PREFIX: '',
        FIAS___CACHE_TIMEOUT: '',
        FIAS___DATABASE_ENGINE: '',
        FIAS___DATABASE_HOST: '',
        FIAS___DATABASE_NAME: '',
        FIAS___DATABASE_PASSWORD: '',
        FIAS___DATABASE_PORT: '',
        FIAS___DATABASE_USER: '',
        FIAS___DEDICATED_DB: '',
        FIAS___SHOW_KLADR_FIELD: '',
        FORMAT___DATE_FORMAT: '',
        GAR___API_URL: 'Адрес для доступа к сервису ГАР. По умолчанию: None.',
        GAR___USE_CACHE: 'Необходимо ли кэшировать запросы к сервису. По умолчанию: True.',
        GAR___TIMEOUT: 'Таймаут запросов. По умолчанию: 10000.',
        GAR___PAGE_LIMIT: 'Количество выбираемых страниц. По умолчанию: 20',
        GAR___TOKEN_URL: 'URL для доступа по OAuth2. По умолчанию: None.',
        GAR___CLIENT_ID: 'CLIENT_ID для доступа по OAuth2. По умолчанию: None.',
        GAR___CLIENT_SECRET: 'CLIENT_SECRET для доступа по OAuth2. По умолчанию: None.',
        GAR___USERNAME: 'Имя пользователя. По умолчанию: None.',
        GAR___PASSWORD: 'Пароль пользователя. По умолчанию: None.',
        GAR___BACKEND: 'Backend. По умолчанию: web_bb.core.wb_gar.backends.wb_gar_backend.',
        GAR___USE_SIMPLE_SERVER: 'Флаг для использования простого клиента для авторизации',
        IMPORT_BUAU___ALLOW_CONTRACTS: '',
        LICENSE___KEY_FILE: '',
        LOGGING___LOG_ACC_ENTRY_DELETION: '',
        LOGGING___LOG_PATH: '',
        LOGGING___MONITORING: '',
        LOGGING___PRODUCTION_REQUEST: '',
        LOGGING___PRODUCTION_REQUEST_CLIENT_INTERVAL: '',
        LOGGING___SENTRY_ORG: '',
        LOGGING___SENTRY_SERVER: '',
        MEDIA___ROOT: '',
        MEDIA___URL: '',
        MIS___HARDCODE_ENT: '',
        MIS___MIS_PAID_SERVICES_AUTH: '',
        MIS___MIS_PAID_SERVICES_LOGIN: '',
        MIS___MIS_PAID_SERVICES_PASSWORD: '',
        MIS___MIS_PAID_SERVICES_SERVER: '',
        MIS___MIS_SERVER: '',
        MIS___MIS_SYNC_CONTRACT_AUTH: '',
        MIS___MIS_SYNC_CONTRACT_SEND: '',
        NFS_WAIT___NFS_MAX_COUNT: '',
        NFS_WAIT___NFS_PAUSE: '',
        NOTIFICATIONS___EMAIL_BACKEND: '',
        NOTIFICATIONS___EMAIL_FILE_PATH: '',
        NOTIFICATIONS___EMAIL_FROM: '',
        NOTIFICATIONS___EMAIL_HOST: '',
        NOTIFICATIONS___EMAIL_HOST_PASSWORD: '',
        NOTIFICATIONS___EMAIL_HOST_USER: '',
        NOTIFICATIONS___EMAIL_PORT: '',
        NOTIFICATIONS___EMAIL_USE_SSL: '',
        NOTIFICATIONS___EMAIL_USE_TLS: '',
        NOTIFICATIONS___USE_EMAIL_NOTIFICATION: '',
        OSS___URL: '',
        PLUGINS___ACTIVATED_PLUGINS: 'Подключенные к системе плагины',
        PLUGINS___RMR_URL: '',
        PLUGINS___USE_PLUGIN_DISPATCHER: '',
        PRODUCTION_REQUEST___CLIENT_INTERVAL: '',
        PRODUCTION_REQUEST___LOG_CLIENT: '',
        PRODUCTION_REQUEST___LOG_SERVER: '',
        PRODUCTION_REQUEST___PRODUCTION_REQUEST_CLIENT_INTERVAL: '',
        PRODUCTION_REQUEST___PRODUCTION_REQUEST_LOG_MEMORY: '',
        READONLY_DB___ALIAS: '',
        READONLY_DB___DATABASE_ENGINE: '',
        READONLY_DB___DATABASE_HOST: '',
        READONLY_DB___DATABASE_NAME: '',
        READONLY_DB___DATABASE_PASSWORD: '',
        READONLY_DB___DATABASE_PORT: '',
        READONLY_DB___DATABASE_USER: '',
        READONLY_DB___URL: '',
        REDIS___REDIS_HOST: '',
        REPLISYNC___SYNC_TABLES_FILE_PATH: '',
        REPORT_MATERIAL_OBOROTKA___PRODUCT_SUM_ACCOUNTING_USAGE: '',
        RIS___AUTH_SERVICE: '',
        RIS___GET_BILLS_SERVICE: '',
        RIS___LOGIN: '',
        RIS___PASSWORD: '',
        RIS___URL: '',
        RUNTIME___APP_CONFIG_UUID: 'Уникальный идентификатор конфигурационного файла',
        RUNTIME___APP_REGION_ABBREVIATION: 'Аббревиатура региона, на котором запущено приложение',
        RUNTIME___DEBUG: 'Активация отладочного режима',
        RUNTIME___MONITORING: '',
        RUNTIME___SESSION_COOKIE_NAME: (
            'Если на одном сервере несколько проектов, то необходимо указывать различные имена'
        ),
        RUNTIME___TEST_APPLICATION: 'Указывает на то, является ли приложение тестовым или нет. По умолчанию: False',
        RUNTIME___TEST_MODE: '',
        RUNTIME___TIME_ZONE: 'Временная зона, в которой работает сервер. По умолчанию: False',
        RUNTIME___USE_MEMCACHE: '',
        RUNTIME___WITH_ACCOUNT_ANALYSIS: '',
        SALARY___DESKTOP_HTML_NAME: '',
        SALARY___DICT_IMPORT_SERVICE: '',
        SALARY___ENABLE_RMR_INTEGRATION: '',
        SALARY___IGNORE_MIGRATION: '',
        SALARY___LOGIN_HTML_NAME: '',
        SALARY___LOGO_STYLE: '',
        SALARY___MAX_ELEMENT_IN_QUEUE: '',
        SALARY___PAYROLL_CALC_IDLE_LOOPS: '',
        SALARY___RMR_URL: '',
        SALARY___SVODY_REPORT_URL: '',
        SQL_LOG___ENABLE: (
            'Включение отображения запросов к БД. Работает только при включенном режиме дебага. По умолчанию: False'
        ),
        SQL_LOG___TRACEBACK: 'Включение трейсбэка до места, откуда был отправлен запрос в БД. По умолчанию: False',
        SQL_LOG___MAX_SIZE: (
            'Максимальная длина SQL-запроса, подлежащего выводу в лог с форматированием. По умолчанию: 25000'
        ),
        SSMP_INTEGRATION___ACTIVE: '',
        SSMP_INTEGRATION___CONSOLE_LOG: '',
        STATIC___ROOT: '',
        STATIC___URL: '',
        STYLE___DESKTOP_HTML_NAME: '',
        STYLE___HIDE_BUH_DESKTOP: '',
        STYLE___HIDE_VERSION_CHANGES: '',
        STYLE___LOGIN_BACKGROUND_STYLE: '',
        STYLE___LOGIN_CLOUD_STYLE: '',
        STYLE___LOGIN_HTML_FOOD_NAME: '',
        STYLE___LOGIN_HTML_NAME: '',
        STYLE___LOGIN_HTML_VEHICLE_NAME: '',
        STYLE___LOGO_BARS_STYLE: '',
        STYLE___LOGO_STYLE: '',
        STYLE___SNOW_MODE_COUNT: '',
        STYLE___SNOW_MODE_ON: '',
        STYLE___TEST_APPLICATION_TEXT: '',
        SVODY___CREATE_USER: '',
        SVODY___ROLES: '',
        SVODY___URL: '',
        SVODY___USE_EMPTY_ENTERPRISE: '',
        TAXNET_INTEGRATION___DOCS_ALLOWED_REQUESTS_TIME_RANGE: '',
        TAXNET_INTEGRATION___DOCS_BEAT_INTERVAL: '',
        TAXNET_INTEGRATION___DOCS_CHECK_HANG_INTERVAL: '',
        TAXNET_INTEGRATION___DOCS_FIRST_RETRY_AFTER: '',
        TAXNET_INTEGRATION___DOCS_LOGIN: '',
        TAXNET_INTEGRATION___DOCS_MAX_RETRIES: '',
        TAXNET_INTEGRATION___DOCS_PASSWORD: '',
        TAXNET_INTEGRATION___DOCS_REQUEST_TIMEOUT: '',
        TAXNET_INTEGRATION___DOCS_RESYNC_TIME: '',
        TAXNET_INTEGRATION___DOCS_RETRY_MULTIPLIER: '',
        TAXNET_INTEGRATION___DOCS_URL: '',
        TEMPORARY___ROOT: '',
        URLS___DOWNLOADS: '',
        URLS___HELP: '',
        URLS___HELP_SALARY: '',
        URLS___M3STATIC: '',
        URLS___ROOT: '',
        URLS___STATIC: '',
        USERS___INACTIVE_SESSION_LIFETIME: '',
        USERS___LOG_OS: '',
        VEHICLE___USE_WAYBILL_COPY: '',
        WATERFALL___BACKGROUND_PROCESS_PANEL_UPDATING_INTERVAL: (
            'Интервал обновления состояния фоновых задач в миллисекундах. По умолчанию: 10000'
        ),
        WATERFALL___CELERY_BROKER_URL: '',
        WATERFALL___CELERY_ALWAYS_EAGER: (
            'Параметр, при включении которого выключается многопроцессность в celery. По умолчанию: False'
        ),
        WATERFALL___CELERYD_TASK_SOFT_TIME_LIMIT: '',
        WATERFALL___DISTRIBUTED_CELERY_DAEMONS: '',
        WATERFALL___ENABLE_BACKGROUND_PROCESS_PANEL: (
            'Признак активности панели фоновых задач на рабочем столе пользователя. По умолчанию: True'
        ),
        WATERFALL___TASK_TIME_LIMIT: 'Ограничение жизни воркера по времени в секундах. По умолчанию: 3600',
        WATERFALL___USE_WEBSOCKET: (
            'Признак использования вебсокетов для оповещения о задачах. В barsdock используется pushme, поэтому '
            'установка этого параметра сейчас приводит к отправке сообщений по обновлению через сокет, они в свою '
            'очередь не достигают цели и не дергают сервер. По умолчанию: False'
        ),
        WATERFALL___WORKER_DEADLINE: '',
        WATERFALL___WTF_ASYNC: '',
        WATERFALL___WTF_REPORT_LIFETIME: '',
        WATERFALL___WTF_SSE_STREAM: '',
        WEBSOCKET___3SERVER: '',
        WEBSOCKET___WEBSOCKET_BACKEND: '',
        WEBSOCKET___WEBSOCKET_PORT: '',
        WEBSOCKET___WEBSOCKET_QUEUE_HOST: '',
        WEBSOCKET___WEBSOCKET_QUEUE_PORT: '',
        WEBSOCKET___WEBSOCKET_URL: '',
    }
