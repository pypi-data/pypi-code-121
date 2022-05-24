import unittest
from pypers.utils.archive_dates import ArchiveDateManagement
import logging
import os


class Test(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_frtm(self):
        archive_name = '2020-23'
        collection = 'frtm'
        a = ArchiveDateManagement(collection, archive_name)
        self.assertEqual(a.archive_date, '2020-06-05')

    def test_empty(self):
        archive_name = 'FR_FRST66_2020-23.zip'
        collection = 'toto'
        a = ArchiveDateManagement(collection, archive_name)
        self.assertEqual(a.archive_date, 'FR_FRST66_2020-23.zip')


if __name__ == "__main__":
    unittest.main()
