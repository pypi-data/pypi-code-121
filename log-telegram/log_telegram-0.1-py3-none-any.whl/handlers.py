import logging.handlers
import time
from queue import Queue

import telegram

logger = logging.getLogger()


class Handler(logging.handlers.QueueHandler):
    def __init__(self, token: str, chat_ids: list[int], fmt=None):
        """
        :param token: telegram bot API token
        :param chat_ids: list of intergers with chat ids
        :param fmt: formatter output style
        """
        queue = Queue()
        super().__init__(queue)

        self.handler = LogMessageDispatcher(token, chat_ids)
        self.handler.setFormatter(logging.Formatter(fmt))
        listener = logging.handlers.QueueListener(queue, self.handler)
        listener.start()

    def prepare(self, record):
        return record


class LogMessageDispatcher(logging.Handler):
    """
    Separate thread for a message dispatching
    """

    MAX_MSG_LEN = 4096
    API_CALL_INTERVAL = 60 / 20  # One message every 3 seconds

    def __init__(self, token: str, chat_ids: list):
        self.token = token
        self.chat_ids = chat_ids
        self.client = telegram.Bot(token)
        super().__init__()

    def handle(self, record):
        record = self.format(record)
        if len(record) > self.MAX_MSG_LEN:
            while record:
                chunked_message = record[: self.MAX_MSG_LEN]
                self.emit(chunked_message)
                record = record[self.MAX_MSG_LEN :]
        else:
            self.emit(record)

    def emit(self, record):
        for chat_id in self.chat_ids:
            try:
                self.client.send_message(chat_id, record)
            except telegram.error.TimedOut:
                time.sleep(5)
            except telegram.error.Unauthorized:
                logger.debug("Invalid bot token")
                time.sleep(5)
            except telegram.error.RetryAfter as e:
                logger.debug(f"Retry after {e.retry_after} seconds")
                time.sleep(e.retry_after)

            time.sleep(self.API_CALL_INTERVAL)
