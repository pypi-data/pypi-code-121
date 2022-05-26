#!/usr/bin/env python3
#   encoding: UTF-8

# This file is part of turberfield.
#
# Turberfield is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Turberfield is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with turberfield.  If not, see <http://www.gnu.org/licenses/>.

import asyncio
import os
import unittest

from turberfield.utils.pipes import PipeQueue


@unittest.skipUnless(hasattr(os, "mkfifo"), "Named pipes unavailable here.")
class PipeQueueTest(unittest.TestCase):

    def setUp(self):
        self.path = "test.fifo"
        try:
            os.remove(self.path)
        except FileNotFoundError:
            pass

    def tearDown(self):
        self.setUp()

    def test_no_history(self):
        os.mkfifo(self.path)
        self.assertRaises(
            FileExistsError,
            PipeQueue(self.path, history=False).__enter__)

    def test_attributes(self):
        with PipeQueue(self.path) as pq:
            self.assertIsNotNone(pq._in)
            self.assertIsNotNone(pq._out)
            self.assertTrue(hasattr(pq, "get"))
            self.assertTrue(hasattr(pq, "put"))

    def test_simple_read_write(self):
        loop = asyncio.get_event_loop()
        with PipeQueue(self.path) as pq:
            loop.run_until_complete(
                asyncio.wait_for(pq.put("S"), 2))
            rv = loop.run_until_complete(
                asyncio.wait_for(pq.get(), 2))
            self.assertEqual("S", rv)

    def test_tuple_read_write(self):
        loop = asyncio.get_event_loop()
        payload = (12, "string")
        with PipeQueue(self.path) as pq:
            loop.run_until_complete(
                asyncio.wait_for(pq.put(payload), 2))
            rv = loop.run_until_complete(
                asyncio.wait_for(pq.get(), 2))
            self.assertEqual(payload, rv)

    def test_multiple_read_write(self):
        loop = asyncio.get_event_loop()
        payloads = ((i, "string") for i in range(6))
        with PipeQueue(self.path) as pq:
            for n, payload in enumerate(payloads):
                loop.run_until_complete(
                    asyncio.wait_for(pq.put(payload), 2))

            for i in range(n):
                rv = loop.run_until_complete(
                    asyncio.wait_for(pq.get(), 2))
                self.assertIsInstance(rv, tuple)
                self.assertEqual(i, rv[0])
                self.assertEqual("string", rv[1])

    def test_queue_returned_by_factory(self):

        def factory():
            return PipeQueue.pipequeue(self.path)

        loop = asyncio.get_event_loop()
        pq = factory()
        loop.run_until_complete(
            asyncio.wait_for(pq.put("S"), 2))
        rv = loop.run_until_complete(
            asyncio.wait_for(pq.get(), 2))
        self.assertEqual("S", rv)
        pq.close()
