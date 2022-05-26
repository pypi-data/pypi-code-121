# -*- coding: utf-8 -*-

__author__ = r'wsb310@gmail.com'

from aliyun.log import QueuedLogHandler
from aliyun.log.logclient import LogClient as _LogClient
from aliyun.log.version import LOGGING_HANDLER_USER_AGENT
from aliyun.log.gethistogramsrequest import GetHistogramsRequest

from ...extend.error import catch_error
from ...extend.asyncio.future import ThreadWorker


_thread_worker = ThreadWorker(32)


class LogClient(_LogClient):

    def __init__(self, endpoint, access_key_id, access_key, project, log_store, **kwargs):

        super().__init__(endpoint, access_key_id, access_key, **kwargs)

        self._project = project
        self._log_store = log_store

    @_thread_worker
    def async_get_histograms(self, from_time, to_time, *, topic=None, query=None):

        result = None

        with catch_error():

            request = GetHistogramsRequest(self._project, self._log_store, from_time, to_time, topic, query)

            respose = self.get_histograms(request)

            if respose.progress == r'Complete':
                result = respose.body

        return result

    @_thread_worker
    def async_get_log(self, from_time, to_time, offset, size, *, topic=None, query=None, reverse=False):

        result = None

        with catch_error():

            respose = self.get_log(
                self._project, self._log_store,
                from_time, to_time, topic, query, reverse, offset, size
            )

            if respose.progress == r'Complete':
                result = respose.body

        return result


class LogHandler(QueuedLogHandler):

    def __init__(self, end_point, access_key_id, access_key, project, log_store, topic=None, source=None, **kwargs):

        super().__init__(end_point, access_key_id, access_key, project, log_store, topic, **kwargs)

        self._source = source

    def create_client(self):

        self.client = LogClient(
            self.end_point, self.access_key_id, self.access_key,
            self.project, self.log_store, source=self._source
        )

        self.client.set_user_agent(LOGGING_HANDLER_USER_AGENT)
