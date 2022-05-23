from twisted.internet.defer import inlineCallbacks
from twisted.trial import unittest

from peek_core_search._private.client.controller.FastKeywordController import (
    FastKeywordController,
)
from peek_core_search._private.tuples.search_object.SearchResultObjectTuple import (
    SearchResultObjectTuple,
)
from peek_core_search._private.worker.tasks.KeywordSplitter import splitPartialKeywords


class FastKeywordControllerTest(unittest.TestCase):
    def test_mergePartialAndFullMatches_1(self):
        fullByKw = {"^to$": [5, 6]}
        partialByKw = {"^to": [7], "^aa": [8]}

        inst = FastKeywordController(None, None)

        resultByKw = inst._mergePartialAndFullMatches("to", fullByKw, partialByKw)

        self.assertEqual(set(resultByKw), {"to"})
        self.assertEqual(len(resultByKw), 1)
        self.assertEqual(set(resultByKw["to"]), {5, 6, 7})

    def test_mergePartialAndFullMatches_2(self):
        fullByKw = {"^five$": [5, 6]}
        partialByKw = {"^fiv": [7, 6], "ive": [7, 6]}

        inst = FastKeywordController(None, None)

        resultByKw = inst._mergePartialAndFullMatches(
            "five seven", fullByKw, partialByKw
        )

        self.assertEqual(set(resultByKw), {"five"})
        self.assertEqual(len(resultByKw), 1)
        self.assertEqual(set(resultByKw["five"]), {5, 6, 7})

    def test_mergePartialAndFullMatches_3(self):
        searchString = "tatu west fus"
        fullByKw = {}
        partialByKw = {t: [7, 6] for t in splitPartialKeywords(searchString)}

        inst = FastKeywordController(None, None)

        resultByKw = inst._mergePartialAndFullMatches(
            searchString, fullByKw, partialByKw
        )

        self.assertEqual(set(resultByKw), {"west", "fus", "tatu"})
        self.assertEqual(set(resultByKw["west"]), {6, 7})
        self.assertEqual(set(resultByKw["fus"]), {6, 7})
        self.assertEqual(set(resultByKw["tatu"]), {6, 7})

    def test_setIntersectFilterIndexResults(self):
        data = {"0": [6778979, 7042955]}

        inst = FastKeywordController(None, None)

        result = inst._setIntersectFilterIndexResults(data)

        self.assertEqual(result, {6778979, 7042955})
        self.assertEqual(len(result), len(data["0"]))

    @inlineCallbacks
    def test_filterObjectsForSearchString(self):
        from twisted.python import threadable

        threadable.isInIOThread = lambda: True

        data = [
            SearchResultObjectTuple(properties={"any": "TRANS HV FUSE TATURA WEST 28"})
        ]

        inst = FastKeywordController(None, None)

        # No property name
        result = yield inst._filterObjectsForSearchString(
            data, "TRANS HV FUSE TATURA WEST 28", None
        )

        self.assertEqual(len(result), 1)

        # Now try it with the property name
        result = yield inst._filterObjectsForSearchString(
            data, "TRANS HV FUSE TATURA WEST 28", "any"
        )

        self.assertEqual(len(result), 1)

        # Now try it with a WRONG the property name
        result = yield inst._filterObjectsForSearchString(
            data, "TRANS HV FUSE TATURA WEST 28", "dfgdfg"
        )

        self.assertEqual(len(result), 0)

        # partial keywords search string
        result = yield inst._filterObjectsForSearchString(data, "tatu west fus", None)

        self.assertEqual(len(result), 1)
