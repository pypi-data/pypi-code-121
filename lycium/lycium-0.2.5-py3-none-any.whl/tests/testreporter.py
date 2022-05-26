#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import time
from lycium.exceptionreporter import ExceptionReporter

class TestExceptionReporter(unittest.TestCase):
    """
    """
    def testReport(self):
        ExceptionReporter().configure('test', {'connector': 'es', 'host': '127.0.0.1', 'port': 9200})
        ExceptionReporter().report(key='test', typ='unittest', 
            endpoint='debug+python://localhost/exceptionreporter',
            method='debug',
            inputs='{}',
            outputs='{"code":0, "message": "Debugging"}',
            content='foo',
            level='DEBUG'
        )

if __name__ == "__main__":
    unittest.main()
    time.sleep(10)

