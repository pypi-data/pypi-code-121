from enum import Enum


class DropStyle(Enum):
    """
    Represents the three approaches to handling the dropping of objects
    """
    # No objects will be dropped, User sql scripts will take care of the dropping of objects
    NONE = 1

    # The schema will be dropped and recreated before models are generated. This method prevents any objects from
    # accumulating in the schema
    SCHEMA = 2

    # The table will be dropped before the model is generated
    TABLE = 3



class ConfigFormats(Enum):
    """
    Enumeration of the configuration formats supported by DataBeaver
    """
    # cfg/ini format
    INI = 'ini'

    # JSON format
    JSON = 'json'

    # TOML format
    TOML = 'toml'

    # YAML format
    YAML = 'yaml'


class ModelStatus(Enum):
    """
    Enumeration of the status of a given model (table)
    """
    # The model was successfully realized
    NOT_BUILT = "not built"

    # We could not successfully realize the model
    FAILED = "failed"

    # The model was successfully realized
    BUILT = "built"

    # We could not build the model due to dependent models that failed to be built
    SKIPPED = "skipped"


class ExecutionStatus(Enum):
    """
    Enumeration for the sql file execution statuses
    """

    # The file has not yet been executed
    NOT_EXECUTED = "not executed"

    # The file is now being executed
    RUNNING = "running"

    # Execution failed
    FAILED = "failed"

    # File was skipped due to upstream files failing
    SKIPPED = "skipped"

    # File was executed successfully
    SUCCEEDED = "succeeded"


class Systems(Enum):
    MYSQL = "MySQL"

    POSTGRESQL = "PostgreSQL"
