import unittest
from pypers.utils import download
import logging
import os


class Test(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_retry(self):

        self.nb_calls = 0
        logger = logging.getLogger()

        def _worker(obj):
            obj.nb_calls += 1
            if obj.nb_calls < 2:
                raise Exception("Keep the retying context")
            if obj.nb_calls < 3:
                ex = Exception("Keep the retying context")
                ex.code = 404
                raise ex

        @download.retry(Exception, tries=3, delay=0, backoff=1)
        def my_test_function(obj):
            _worker(obj)

        @download.retry(Exception, tries=3, delay=0, backoff=1, logger=logger)
        def my_test_function2(obj):
            _worker(obj)

        my_test_function(self)
        self.assertEqual(self.nb_calls, 3)
        self.nb_calls = 0
        my_test_function2(self)
        self.assertEqual(self.nb_calls, 3)

    def test_download(self):
        if os.environ.get('SHORT_TEST', None):
            return
        res = download.download('http://wipo.int/').read()
        self.assertTrue(len(res) > 0)
        try:
            # No local proxy is installed.
            download.download('http://wipo.int/',
                              http_proxy='localhost').read()
            self.fail("No local proxy is installed")
        except Exception as e:
            try:
                # No local proxy is installed.
                download.download('https://wipo.int/',
                                  https_proxy='localhost').read()
                self.fail("No local proxy is installed")
            except Exception as e:
                pass


if __name__ == "__main__":
    unittest.main()
