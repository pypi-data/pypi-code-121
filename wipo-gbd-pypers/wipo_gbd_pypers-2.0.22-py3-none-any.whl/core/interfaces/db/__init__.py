from .dynamodb import DynamoDBInterface, DynamoDbLogger, DynamoDbConfig, \
    DynamoErrorDB, DynamoSeenSteps, DynamoDoneFile, DynamoPreProd, DynamoTrigger, \
    DynamoIndexingConfig, DynamoPreProdHistory, DynamoEntity, DynamoDailyOperations

_db = None

_db_logger = None

_db_config = None

_db_error = None

_db_steps = None

_db_done_file = None

_db_pre_prod = None

_db_pre_prod_history = None

_db_cron = None

_db_entity = None

_indexer_config = None

_db_op = None


def get_operation_db():
    global _db_op
    if _db_op is None:
        _db_op = DynamoDailyOperations()
    return _db_op


def get_cron_db():
    global _db_cron
    if _db_cron is None:
        _db_cron = DynamoTrigger()
    return _db_cron


def get_pre_prod_db():
    global _db_pre_prod
    if _db_pre_prod is None:
        _db_pre_prod = DynamoPreProd()
    return _db_pre_prod


def get_pre_prod_db_history():
    global _db_pre_prod_history
    if _db_pre_prod_history is None:
        _db_pre_prod_history = DynamoPreProdHistory()
    return _db_pre_prod_history


def get_done_file_manager():
    global _db_done_file
    if _db_done_file is None:
        _db_done_file = DynamoDoneFile()
    return _db_done_file


def get_db():
    global _db
    if _db is None:
        _db = DynamoDBInterface()
    return _db


def get_db_logger():
    global _db_logger
    if _db_logger is None:
        _db_logger = DynamoDbLogger()
    return _db_logger


def get_db_config():
    global _db_config
    if _db_config is None:
        _db_config = DynamoDbConfig()
    return _db_config

def get_indexer_config():
    global _indexer_config
    if _indexer_config is None:
        _indexer_config = DynamoIndexingConfig()
    return _indexer_config


def get_db_error():
    global _db_error
    if _db_error is None:
        _db_error = DynamoErrorDB()
    return _db_error


def get_seen_steps():
    global _db_steps
    if _db_steps is None:
        _db_steps = DynamoSeenSteps()
    return _db_steps


def get_db_entity():
    global _db_entity
    if _db_entity is None:
        _db_entity = DynamoEntity()
    return _db_entity