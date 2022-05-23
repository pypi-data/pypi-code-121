from security.backends.reader import BaseBackendReader
from security.utils import get_object_triple

from .writer import capture_security_logs


class TestingBackendReader(BaseBackendReader):

    def get_count_input_requests(self, from_time, ip=None, path=None, view_slug=None, slug=None, method=None,
                                 exclude_log_id=None):
        if not capture_security_logs.logged_data:
            return 0

        count_requests = 0
        for logger in capture_security_logs.logged_data.input_request:
            if ((exclude_log_id is None or logger.id != exclude_log_id)
                    and (method is None or logger.method == method)
                    and (ip is None or logger.ip == ip)
                    and (path is None or logger.path == path)
                    and (view_slug is None or logger.view_slug == view_slug)
                    and (slug is None or logger.slug == slug)
                    and (logger.start >= from_time)):
                count_requests += 1
        return count_requests

    def get_logs_related_with_object(self, logger_name, related_object):
        if not capture_security_logs.logged_data:
            return []

        return [
            logger for logger in capture_security_logs.logged_data.get(logger_name.replace('-', '_'))
            if get_object_triple(related_object) in logger.related_objects
        ]
