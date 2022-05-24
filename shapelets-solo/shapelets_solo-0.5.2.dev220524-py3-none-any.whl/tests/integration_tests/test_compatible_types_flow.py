# Copyright (c) 2021 Grumpy Cat Software S.L.
#
# This Source Code is licensed under the MIT 2.0 license.
# the terms can be found in LICENSE.md at the root of
# this project, or at http://mozilla.org/MPL/2.0/.

import unittest

from shapelets import init_session
from shapelets.dsl import dsl_op, InputParameter
from shapelets.model import View, Match

from tests.util.test_util import load_medium_sequence


def my_flow(view):
    seq_id, begin, end = dsl_op.decompose_view(view)
    index, w_size, corr = dsl_op.patternSelfMatch(seq_id, begin, end)  # requires CPP worker
    return dsl_op.to_match(seq_id, index, w_size, corr)


class CompatibleTypeFlowTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls._client = init_session("admin", "admin", "https://127.0.0.1")
        cls._seq1 = load_medium_sequence(cls._client)

    @unittest.skip("Re-enable when you have a CPP worker available")
    def test_seq_and_seq_id_compatible(self):
        CompatibleTypeFlowTest._client.register_flow(
            "compatible_flow",
            my_flow(InputParameter(0, "view")))
        view = View(CompatibleTypeFlowTest._seq1.sequence_id, 5, 12)
        res = CompatibleTypeFlowTest._client.run(dsl_op.compatible_flow(view))
        self.assertTrue(isinstance(res, Match))
        self.assertAlmostEqual(res.correlation, 0.50152640147)
        self.assertEqual(res.view.sequence_id, view.sequence_id)
        self.assertEqual(res.view.begin, 1)
        self.assertEqual(res.view.end, 8)
