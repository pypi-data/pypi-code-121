import os
import unittest

from test.setup_test import SetupTest
from worker_bunch.database.database_utils import DatabaseUtils


class TestStep(unittest.TestCase):

    def setUp(self):
        test_dir = SetupTest.ensure_test_dir()
        self.script_file = os.path.join(test_dir, "test_script_file.sql")

        if os.path.exists(self.script_file):
            os.remove(self.script_file)

        self.assertFalse(os.path.exists(self.script_file))

    @classmethod
    def write_script_file(cls, file: str, content: str):
        if os.path.exists(file):
            os.remove(file)

        with open(file, 'w') as f:
            f.write(content)

    # noinspection SpellCheckingInspection
    def test_load_script_file(self):
        text_in = "\nabc \n gäüßhh\n\n"
        self.write_script_file(self.script_file, text_in)

        text_out = DatabaseUtils.load_script_file(self.script_file)
        self.assertEqual(text_out, text_in)

    def test_file_not_exists(self):
        with self.assertRaises(FileNotFoundError) as context:
            DatabaseUtils.load_script_file(self.script_file)

        self.assertIn(self.script_file, str(context.exception))
