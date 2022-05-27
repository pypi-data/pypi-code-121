"""Module for handling logging messages out of a Jupyter Notebook."""
import inspect
import logging
from logging import Logger, LogRecord
from multiprocessing.managers import BaseManager
from queue import Empty, Queue
import secrets
from threading import Event, Thread
from typing import Final, Generator, List

from pytest import fixture

logger = logging.getLogger(__name__)

_LOG_QUEUE_PORT: Final[int] = 50000
_LOG_QUEUE_AUTH_KEY: Final[bytes] = secrets.token_hex(10).encode()
_RECORD_GET_TIMEOUT: Final[int] = 1

# Shared queue for logging messages to and from
_LOG_QUEUE: Final[Queue] = Queue()


def _get_log_queue() -> Queue:
    """Return the shared queue for logging messages."""
    return _LOG_QUEUE


class LogQueueManager(BaseManager):
    """Custom multiprocessing Manager for handling log messages."""

    pass


LogQueueManager.register("get_log_queue", callable=_get_log_queue)


def _log_retriever(log_queue: Queue, stopper: Event) -> None:
    """Listen to queue, log received records until stop is set."""
    logger.info("Log retriever started")
    while not stopper.is_set():
        try:
            record: LogRecord = log_queue.get(timeout=_RECORD_GET_TIMEOUT)
            # Update log info with annotations
            notebook_name: str = record.notebook  # type: ignore[attr-defined] # Reason: we ensure this is added using LogQueueFilter below # noqa: B950
            record.processName = f"[{notebook_name}_notebook]"
            record.msg = f"[FROM {notebook_name.upper()} NOTEBOOK] {record.msg}"
            # Send to handler
            logger.handle(record)
        except Empty:
            pass
    logger.info("Log retriever stopped")


@fixture(scope="module")
def log_queue_manager() -> Generator[LogQueueManager, None, None]:
    """Hosts and starts a LogQueueManager instance for logging messages."""
    with LogQueueManager(
        address=("", _LOG_QUEUE_PORT), authkey=_LOG_QUEUE_AUTH_KEY
    ) as manager:
        logger.info("LogQueueManager started")
        yield manager


@fixture
def clear_log_queue() -> None:
    """Clears the log queue, ready for the next test."""
    # Clear queue, using direct reference as otherwise will hit Manager's proxy
    logger.info("Clearing log queue")
    with _LOG_QUEUE.mutex:
        _LOG_QUEUE.queue.clear()
    logger.info("Log queue cleared")


@fixture(scope="module", autouse=True)
def log_queue_listener(
    log_queue_manager: LogQueueManager,
) -> Generator[None, None, None]:
    """Function-scoped listener to retrieve and log from the LogQueueManager."""
    # Get shared proxy of queue and create thread to listen to it
    log_queue: Queue = log_queue_manager.get_log_queue()  # type: ignore[attr-defined] # Reason: registered on Manager above # noqa: B950
    stop_event: Event = Event()
    log_retrieval_thread = Thread(
        target=_log_retriever,
        name="log retriever",
        args=(log_queue, stop_event),
        daemon=True,
    )
    logger.info("Starting log retrieval thread")
    log_retrieval_thread.start()

    yield

    logger.info("Stopping log retrieval thread")
    stop_event.set()
    log_retrieval_thread.join(_RECORD_GET_TIMEOUT + 1)


# Just a placeholder to mimic it being in scope in the notebook
loggers: Final[List[Logger]] = []
_NOTEBOOK_PLACEHOLDER: Final[str] = "_NOTEBOOK_PLACEHOLDER"


def _add_notebook_queue_logging() -> None:
    """Code to be injected into notebooks to setup queue logging."""
    import logging
    from logging import Filter, LogRecord
    from logging.handlers import QueueHandler
    from multiprocessing.managers import BaseManager

    # Create copy of LogQueueManager class to have one in scope of injected code
    class LogQueueManager(BaseManager):
        pass

    LogQueueManager.register("get_log_queue")

    # Connect to Manager and get shared log queue
    manager = LogQueueManager(
        address=("", _LOG_QUEUE_PORT), authkey=_LOG_QUEUE_AUTH_KEY
    )  # needs to be inlined because of how it's injected
    manager.connect()
    log_queue = manager.get_log_queue()  # type: ignore[attr-defined] # Reason: registered on Manager above # noqa: B950

    # Create queue handler for loggers
    queue_handler = QueueHandler(log_queue)
    queue_handler.setLevel("INFO")

    # Create custom filter to append additional LogRecord field
    class LogQueueFilter(Filter):
        def filter(self, record: LogRecord) -> bool:
            record.notebook = _NOTEBOOK_PLACEHOLDER  # type: ignore[attr-defined] # Reason: explicitly setting this for later use # noqa: B950
            return True

    queue_handler.addFilter(LogQueueFilter())

    # Attach to root logger and set others to propagate
    logging.info("Attaching queue handler to root logger")
    logging.root.addHandler(queue_handler)
    for i_logger in loggers:
        logging.info(f"Setting {i_logger.name} to propagate")
        i_logger.propagate = True


def notebook_queue_logging_code(notebook_name: str) -> str:
    """Generates code to inject into a notebook to allow queue-logging.

    Args:
        notebook_name: The name to use to annotate log messages from the notebook.

    Returns:
        The generated code to inject.
    """
    source = inspect.getsource(_add_notebook_queue_logging)

    # Replace constants that aren't in scope
    source = source.replace("_LOG_QUEUE_PORT", str(_LOG_QUEUE_PORT))
    source = source.replace(
        "_LOG_QUEUE_AUTH_KEY", str(_LOG_QUEUE_AUTH_KEY)
    )  # will include quote marks
    source = source.replace("_NOTEBOOK_PLACEHOLDER", f'"{notebook_name}"')

    return source + f"{_add_notebook_queue_logging.__name__}()"
