from unittest import TestCase
from c import cutil


class Test(TestCase):
    def test_echo(self):
        request: str = "weijingjing"
        result = cutil.echo(request)
        self.assertEqual(result, "v1.0 : " + request)
