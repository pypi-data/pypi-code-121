import unittest
import mwx.framework as mwx


class TestTokenizerMethods(unittest.TestCase):

    def test_split_words1(self):
        values = (
            ("(1 * 2), (1 / 2)", ['(1 * 2)', ',', ' ', '(1 / 2)']),
        )
        for text, result in values:
            self.assertEqual(mwx.split_words(text), result)


if __name__ == "__main__":
    unittest.main()
