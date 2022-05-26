import tracemalloc
import logging

from falcon import Request, Response

logger = logging.getLogger(__name__)


class MemoryMiddleware:

    def _get_url_fingerprint(self, req: Request):
        if hasattr(req.context, "url_fingerprint"):
            fingerprint = req.context.url_fingerprint
        else:
            fingerprint = req.path
            for key, value in req.params.items():
                fingerprint = fingerprint.replace(value, f'{{{key}}}') if value else fingerprint

        return fingerprint

    def process_request(self, req: Request, resp: Response):
        """
        :param req: falcon.Request
        :param resp: falcon.Response
        :return:
        """
        tracemalloc.start()

    def process_response(self, req: Request, resp: Response, resource, req_succeeded: bool):
        """
        :param req: falcon.Request
        :param resp: falcon.Response
        :param resource: Resource object
        :param req_succeeded: bool
        :return:
        """
        url_fingerprint = self._get_url_fingerprint(req)
        current, peak = tracemalloc.get_traced_memory()
        current = current / 10 ** 6
        peak = peak / 10 ** 6
        logger.info(f'Current memory usage is {current}MB; Peak was {peak}MB', extra={
            'current_memory': current,
            'peak_memory': peak,
            'url_fingerprint': url_fingerprint,
        })
        tracemalloc.stop()
