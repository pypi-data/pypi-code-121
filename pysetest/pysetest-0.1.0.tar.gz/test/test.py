import os
import pathlib
import subprocess
import sys
import time

import requests

from pyse import PyseTestCase, PyseException


class PyseTest(PyseTestCase):
    @classmethod
    def setUpClass(cls) -> None:
        test_dir = pathlib.Path(__file__).parent.resolve()
        subprocess.Popen([sys.executable, os.path.join(test_dir, "server.py")])
        time.sleep(5)  # wait for server to start

    @classmethod
    def tearDownClass(cls) -> None:
        requests.post("http://127.0.0.1:5000/shutdown")

    def test_status_code_equal(self) -> None:
        self.assert_status_code_equal(200, 200)

    def test_content_equal_exception(self) -> None:
        response = requests.get("http://127.0.0.1:5000/text")
        self.assertRaises(PyseException, self.assert_content_equal, response, {"Text"})

    def test_bytes(self) -> None:
        response = requests.get("http://127.0.0.1:5000/text")
        self.assert_success(response)
        self.assert_content_equal(response, b"Text")

    def test_text(self) -> None:
        response = requests.get("http://127.0.0.1:5000/text")
        self.assert_success(response)
        self.assert_content_equal(response, "Text")

    def test_json_list_empty(self) -> None:
        response = requests.get("http://127.0.0.1:5000/json/list/empty")
        self.assert_success(response)
        self.assert_content_equal(response, b"[]\n")
        self.assert_content_equal(response, "[]\n")
        self.assert_content_equal(response, [])

    def test_json_list_filled(self) -> None:
        response = requests.get("http://127.0.0.1:5000/json/list/filled")
        self.assert_success(response)
        self.assert_content_equal(response, b'["elem1","elem2","elem3"]\n')
        self.assert_content_equal(response, '["elem1","elem2","elem3"]\n')
        self.assert_content_equal(response, ["elem1", "elem2", "elem3"])

    def test_json_list_nested(self) -> None:
        response = requests.get("http://127.0.0.1:5000/json/list/nested")
        self.assert_success(response)
        self.assert_content_equal(response, b'[["elem1","elem2"],["elem3","elem4"]]\n')
        self.assert_content_equal(response, '[["elem1","elem2"],["elem3","elem4"]]\n')
        self.assert_content_equal(response, [["elem1", "elem2"], ["elem3", "elem4"]])

    def test_json_dict_empty(self) -> None:
        response = requests.get("http://127.0.0.1:5000/json/dict/empty")
        self.assert_success(response)
        self.assert_content_equal(response, b"{}\n")
        self.assert_content_equal(response, "{}\n")
        self.assert_content_equal(response, {})

    def test_json_dict_filled(self) -> None:
        response = requests.get("http://127.0.0.1:5000/json/dict/filled")
        self.assert_success(response)
        self.assert_content_equal(
            response, b'{"key1":"value1","key2":"value2","key3":"value3"}\n'
        )
        self.assert_content_equal(
            response, '{"key1":"value1","key2":"value2","key3":"value3"}\n'
        )

        # should still work with permuted key-value pairs
        self.assert_content_equal(
            response, {"key2": "value2", "key3": "value3", "key1": "value1"}
        )

    def test_json_dict_nested(self) -> None:
        response = requests.get("http://127.0.0.1:5000/json/dict/nested")
        self.assert_success(response)
        self.assert_content_equal(
            response, b'{"key1":{"k1":"v1","k2":"v2"},"key2":{"k3":"v3","k4":"v4"}}\n'
        )
        self.assert_content_equal(
            response, '{"key1":{"k1":"v1","k2":"v2"},"key2":{"k3":"v3","k4":"v4"}}\n'
        )

        # should still work with permuted key-value pairs
        self.assert_content_equal(
            response,
            {"key2": {"k3": "v3", "k4": "v4"}, "key1": {"k2": "v2", "k1": "v1"}},
        )

    def test_redirect(self) -> None:
        response = requests.get("http://127.0.0.1:5000/redirect", allow_redirects=False)
        self.assert_redirect(response)

    def test_client_error(self) -> None:
        response = requests.get("http://127.0.0.1:5000/nopath")
        self.assert_client_error(response)

    def test_server_error(self) -> None:
        response = requests.get("http://127.0.0.1:5000/server-error")
        self.assert_server_error(response)
