from unittest import mock, TestCase

from citibox.profiling.contrib.falcon import MemoryMiddleware


class EmptyResource:
    pass


@mock.patch('citibox.profiling.contrib.falcon.memory_middleware.Response')
@mock.patch('citibox.profiling.contrib.falcon.memory_middleware.Request')
class TestMemoryMiddleware(TestCase):

    def test_process_request_get_http(self, request_mock, response_mock):
        falcon_middleware = MemoryMiddleware()
        request_mock.method = "GET"
        request_mock.host = "PYTEST"
        request_mock.path = "/test_path"
        request_mock.headers = {"header-a": "A"}
        request_mock.params = {"parameter_1": "1"}

        response_mock.body = {"status": "ok"}
        response_mock.status = "200 Ok"

        with self.assertLogs() as log:
            falcon_middleware.process_response(request_mock, response_mock, EmptyResource(), True)
            self.assertEqual(1, len(log.output))
            self.assertEqual(log.output[0],
                             'INFO:citibox.profiling.contrib.falcon.memory_middleware:Current memory usage is 0.0MB; Peak was 0.0MB')







