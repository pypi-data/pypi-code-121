from tecton._internals.sdk_decorators import sdk_public_method
from tecton_spark import conf
from tecton_spark import errors
from tecton_spark import logger as logger_lib

logger = logger_lib.get_logger("SnowflakeContext")


@sdk_public_method
def set_connection(connection) -> "SnowflakeContext":
    """
    Connect tecton to Snowflake.

    :param connection: The SnowflakeConnection object.
    :return: A SnowflakeContext object.
    """
    from snowflake.connector import SnowflakeConnection

    if not isinstance(connection, SnowflakeConnection):
        raise errors.TectonValidationError("connection must be a SnowflakeConnection object")

    return SnowflakeContext.set_connection(connection)


class SnowflakeContext:
    """
    Get access to Snowflake connection and session.
    """

    _current_context_instance = None
    _session = None
    _connection = None

    def __init__(self, connection):
        self._connection = connection
        if conf.get_bool("ALPHA_SNOWFLAKE_SNOWPARK_ENABLED"):
            from snowflake.snowpark import Session

            connection_parameters = {
                "connection": connection,
            }
            self._session = Session.builder.configs(connection_parameters).create()

    def get_session(self):
        if conf.get_bool("ALPHA_SNOWFLAKE_SNOWPARK_ENABLED"):
            return self._session
        else:
            raise errors.TectonValidationError(
                "Snowflake session is only available with Snowpark enabled, use get_connection() instead"
            )

    def get_connection(self):
        return self._connection

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
            raise errors.TectonValidationError(
                "Please set Snowflake connection using tecton.snowflake_context.set_connection(connection)"
            )

    @classmethod
    def set_connection(cls, connection) -> "SnowflakeContext":
        logger.debug(f"Generating new Snowflake session")
        cls._current_context_instance = cls(connection)
        return cls._current_context_instance
