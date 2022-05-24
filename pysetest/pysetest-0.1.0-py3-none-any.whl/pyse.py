from typing import Union
from unittest import TestCase

from requests.models import Response


class PyseException(Exception):
    pass


class PyseTestCase(TestCase):
    def assert_status_code_equal(
        self, status_code: int, expected_status_code: int
    ) -> None:
        self.assertEqual(status_code, expected_status_code)

    def assert_content_equal(
        self, response: Response, expected_content: Union[bytes, str, dict, list]
    ) -> None:
        if isinstance(expected_content, bytes):
            self.assertEqual(response.content, expected_content)
        elif isinstance(expected_content, str):
            self.assertEqual(response.text, expected_content)
        elif isinstance(expected_content, dict) or isinstance(expected_content, list):
            self.assertEqual(response.json(), expected_content)
        else:
            raise PyseException(
                f"expected_content must be bytes, str or JSON (i.e. dict or list), "
                f"but was {type(expected_content)} instead"
            )

    def assert_success(self, response: Response) -> None:
        self.assertTrue(200 <= response.status_code <= 299)

    def assert_redirect(self, response: Response) -> None:
        self.assertTrue(300 <= response.status_code <= 399)

    def assert_client_error(self, response: Response) -> None:
        self.assertTrue(400 <= response.status_code <= 499)

    def assert_server_error(self, response: Response) -> None:
        self.assertTrue(500 <= response.status_code <= 599)
