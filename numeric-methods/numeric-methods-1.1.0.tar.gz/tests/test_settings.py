import unittest

from numeric_methods.language import TRANSLATE
from numeric_methods.settings import get_language, set_language


class TestLanguage(unittest.TestCase):
    def tearDown(self):
        set_language("en")

    def test_default(self):
        self.assertEqual(get_language(), "ENGLISH")

    def test_getting(self):
        set_language("ru")
        self.assertEqual(get_language(), "RUSSIAN")

    def test_raising(self):
        self.assertFalse(set_language("fr"))


class TestTranslate(unittest.TestCase):
    def setUp(self):
        def function():
            pass

        self.documentations = {
            "ENGLISH": "TEST",
            "RUSSIAN": "ТЕСТ"
        }

        self.proto_function = function
        self.function = TRANSLATE.documentation(self.documentations)(function)

    def tearDown(self):
        TRANSLATE.documentation_subscribers = []
        set_language("en")

    def test_field__all_docs__(self):
        self.assertTrue(hasattr(self.function, "__all_docs__"))
        self.assertEqual(self.function.__all_docs__, self.documentations)

    def test_memory_equality(self):
        self.assertIs(self.proto_function, self.function)

    def test_setting(self):
        self.assertEqual(self.function.__doc__, self.documentations[get_language()])
        set_language("ru")
        self.assertEqual(self.function.__doc__, self.documentations[get_language()])


if __name__ == '__main__':
    unittest.main()
