from tecton._internals.sdk_decorators import sdk_public_method
from tecton_spark import conf
from tecton_spark import logger as logger_lib
from tecton_spark.snowflake.snowflake_utils import supress_snowflake_logs

logger = logger_lib.get_logger("SnowflakeContext")


class SnowflakeContext:
    """
    Get access to Snowflake session.
    """

    _current_context_instance = None
    _session = None

    def __init__(self):
        from snowflake.snowpark import Session

        supress_snowflake_logs()

        connection_parameters = {
            "user": conf.get_or_raise("SNOWFLAKE_USER"),
            "password": conf.get_or_raise("SNOWFLAKE_PASSWORD"),
            "account": conf.get_or_raise("SNOWFLAKE_ACCOUNT_IDENTIFIER"),
            "warehouse": conf.get_or_raise("SNOWFLAKE_WAREHOUSE"),
            # Database and schema are required for Snowpark to create various temporary objects under the covers
            "database": conf.get_or_raise("SNOWFLAKE_DATABASE"),
            "schema": "PUBLIC",
        }
        self._session = Session.builder.configs(connection_parameters).create()

    def get_session(self):
        return self._session

    @classmethod
    @sdk_public_method
    def get_instance(cls) -> "SnowflakeContext":
        """
        Get the singleton instance of SnowflakeContext.
        """
        # If the instance doesn't exist, creates a new SnowflakeContext from
        # an existing Spark context. Alternatively, creates a new Spark context on the fly.
        if cls._current_context_instance is not None:
            return cls._current_context_instance
        else:
            return cls._generate_and_set_new_instance()

    @classmethod
    def _generate_and_set_new_instance(cls) -> "SnowflakeContext":
        logger.debug(f"Generating new Snowflake session")
        cls._current_context_instance = cls()
        return cls._current_context_instance
