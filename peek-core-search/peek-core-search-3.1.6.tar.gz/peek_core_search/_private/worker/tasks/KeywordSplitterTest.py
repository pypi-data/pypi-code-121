from twisted.trial import unittest

from peek_core_search._private.worker.tasks.KeywordSplitter import (
    splitPartialKeywords,
    splitFullKeywords,
    _splitFullTokens,
    twoCharTokens,
)


class KeywordSplitterTest(unittest.TestCase):
    def testDuplicates(self):
        self.assertEqual({"smith"}, _splitFullTokens("smith smith"))

    def test_twoCharTokens(self):
        self.assertEqual(set(), twoCharTokens("smith smith"))

        self.assertEqual({"^to$"}, twoCharTokens(splitFullKeywords("two to")))

        self.assertEqual({"^to"}, twoCharTokens(splitPartialKeywords("two to")))

    def testFullKeywordSplit(self):
        self.assertEqual({"^smith$"}, splitFullKeywords("smith"))
        self.assertEqual({"^zorroreyner$"}, splitFullKeywords("ZORRO-REYNER"))
        self.assertEqual({"^34534535$"}, splitFullKeywords("34534535"))

        self.assertEqual({"^and$"}, splitFullKeywords("and"))
        self.assertEqual({"^to$"}, splitFullKeywords("to"))
        self.assertEqual({"^to$"}, splitFullKeywords("to"))

        self.assertEqual(
            {"^milton$", "^unit$", "^22$"}, splitFullKeywords("Milton Unit 22")
        )

        self.assertEqual({"^unit$"}, splitFullKeywords("Unit A"))

        self.assertEqual({"^unit$"}, splitFullKeywords("Unit 1"))

        self.assertEqual(
            {"^trans$", "^66kv$", "^b3$", "^cb$", "^ats$"},
            splitFullKeywords("ATS B3 TRANS 66KV CB"),
        )

    def testPartialKeywordSplit(self):
        self.assertEqual({"^smi", "mit", "ith"}, splitPartialKeywords("smith"))

        self.assertEqual(
            {"^zor", "orr", "rro", "ror", "ore", "rey", "eyn", "yne", "ner"},
            splitPartialKeywords("ZORRO-REYNER"),
        )
        self.assertEqual(
            {"^345", "535", "453", "534", "345"}, splitPartialKeywords("34534535")
        )

        self.assertEqual({"^and"}, splitPartialKeywords("and"))

        self.assertEqual({"^to"}, splitPartialKeywords("to"))

        self.assertEqual({"a55", "^ha5"}, splitPartialKeywords("ha55"))

        self.assertEqual(
            {"^mil", "ilt", "lto", "ton", "^uni", "nit", "^22"},
            splitPartialKeywords("Milton Unit 22"),
        )

        self.assertEqual(
            {"^mil", "ill", "lls", "^un", "^no"}, splitPartialKeywords("mills un no")
        )

        self.assertEqual({"^uni", "nit", "^22"}, splitPartialKeywords("Unit 22"))

        self.assertEqual({"^uni", "nit"}, splitPartialKeywords("Unit 1"))

        self.assertEqual({"^uni", "nit"}, splitPartialKeywords("A Unit"))

        self.assertEqual({"^uni", "nit"}, splitPartialKeywords("2 Unit"))

        self.assertEqual(
            {"^ats", "^cb", "^b3", "^66k", "6kv", "^tra", "ran", "ans"},
            splitPartialKeywords("ATS B3 TRANS 66KV CB"),
        )

        self.assertEqual({"^col", "^lin", "ins"}, splitPartialKeywords("COL LINS"))

        self.assertNotEqual(
            splitPartialKeywords("COLLINS"), splitPartialKeywords("COL LINS")
        )
