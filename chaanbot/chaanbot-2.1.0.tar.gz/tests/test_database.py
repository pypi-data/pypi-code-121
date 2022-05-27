from unittest import TestCase

from chaanbot.database import Database


class TestDatabase(TestCase):
    def test_initialization(self):
        path = "/path/"
        database = Database(path)
        self.assertEqual(path, database.sqlite_database_path)

    def test_connect_to_database(self):
        # TODO: Implement
        pass
