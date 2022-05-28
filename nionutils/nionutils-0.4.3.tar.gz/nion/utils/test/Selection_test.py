# standard libraries
import logging
import unittest

# local libraries
from nion.utils import Selection


class TestSelection(unittest.TestCase):

    def setUp(self) -> None:
        pass

    def tearDown(self) -> None:
        pass

    def test_extending_selection_with_no_anchor_behaves_sensibly(self) -> None:
        s = Selection.IndexedSelection()
        s.extend(0)
        self.assertEqual({0}, s.indexes)
        self.assertEqual(0, s.anchor_index)

    def test_inserting_index_into_empty_selection_results_in_empty_index(self) -> None:
        s = Selection.IndexedSelection()
        s.insert_index(0)
        self.assertEqual(set(), s.indexes)

    def test_inserting_index_into_non_empty_selection_adjusts_indexes(self) -> None:
        s = Selection.IndexedSelection()
        s.set_multiple({0, 2, 4})
        s.insert_index(1)
        self.assertEqual({0, 3, 5}, s.indexes)


if __name__ == '__main__':
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
