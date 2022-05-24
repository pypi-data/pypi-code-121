# Copyright (c) 2021 Grumpy Cat Software S.L.
#
# This Source Code is licensed under the MIT 2.0 license.
# the terms can be found in LICENSE.md at the root of
# this project, or at http://mozilla.org/MPL/2.0/.

import unittest

from shapelets import init_session
from shapelets.dsl import dsl_op, MalformedGraph
from shapelets.model import InvalidArgumentValue

from tests.util.test_util import (
    load_small_sequence1,
    load_small_sequence2
)


class GraphExceptions(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls._client = init_session("admin", "admin", "https://127.0.0.1")
        cls._sequence1 = load_small_sequence1(cls._client)
        cls._sequence2 = load_small_sequence2(cls._client)

    def test_bad_input_argument(self):
        seq1 = GraphExceptions._sequence1
        seq2 = GraphExceptions._sequence2
        with self.assertRaises(InvalidArgumentValue):
            GraphExceptions._client.run(dsl_op.times_ts(seq1, seq2))

    def test_bad_connection(self):
        seq1 = GraphExceptions._sequence1
        seq2 = GraphExceptions._sequence2
        with self.assertRaises(MalformedGraph):
            aux = dsl_op.times_ts_ts(seq1, seq2)
            res = dsl_op.times_ts(seq1, aux)
            GraphExceptions._client.run(res)
