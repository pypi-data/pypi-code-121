class CONFIGURATION:
    # loggers

    MAIN_LOGGER_NAME = "main"
    ALPHA_LOGGER_NAME = "alpha"
    ERRORS_LOGGER_NAME = "errors"
    MONITORING_LOGGER_NAME = "monitoring"
    
    API_LOGGER_NAME = "api"
    HTTP_LOGGER_NAME = "http"

    DEFAULT_LOGGERS_FILEPATH = "src/configs/loggers"
    DEFAULT_CONFIG_FILEPATH = "src/configs/config"
    DEFAULT_LOGGERS_COLORS_FILEPATH = "src/configs/loggers_colors"

    # Databases

    MAIN_DATABASE_NAME = "main"
    USERS_DATABASE_NAME = "users"

    # configuration

    MAIN_CONFIGURATION_NAME = "config"
    API_CONFIGURATION_NAME = "api"
    CONFIGURATION_ENV_NAME = "ALPHA_CONF"

    # Debug
    DEBUG_SCHEMA = False