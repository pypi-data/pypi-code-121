# Copyright (C) 2020-Present the hyssop authors and contributors.
#
# This module is part of hyssop and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

'''
File created: August 21st 2020

Modified By: hsky77
Last Updated: September 4th 2020 14:12:34 pm
'''

import asyncio
from enum import Enum

from ..util import Callbacks
from .base import UnitTestCase


class TestCallbackType(Enum):
    Event_A = 'a'
    Event_A_Async = 'a_async'


class UtilTestCase(UnitTestCase):
    def test(self):
        self.test_callback()

    def test_callback(self, callbacks: Callbacks = None):
        cb = callbacks or Callbacks(TestCallbackType)
        cb.add_callback(TestCallbackType.Event_A, UtilTestCase.test_func)
        cb.add_callback(TestCallbackType.Event_A_Async,
                        UtilTestCase.test_func_async)

        cb.execute_callback(TestCallbackType.Event_A, self, 1, kwindex=2)

        loop = asyncio.get_event_loop()
        loop.run_until_complete(cb.execute_callback_async(
            TestCallbackType.Event_A_Async, self, 1, kwindex=2))

    def test_func(self, i, kwindex):
        self.assertEqual(i, 1)
        self.assertEqual(kwindex, 2)

    async def test_func_async(self, i, kwindex):
        self.assertEqual(i, 1)
        self.assertEqual(kwindex, 2)
