from twisted.trial import unittest

from peek_plugin_eventdb._private.PluginNames import eventdbTuplePrefix


class MyTestCase(unittest.TestCase):
    def testPluginName(self):
        self.assertEqual(eventdbTuplePrefix, "peek_plugin_eventdb.")
