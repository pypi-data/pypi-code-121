import unittest
from slpkg.utils import Utils


class TestUtils(unittest.TestCase):

    def setUp(self):
        self.utils = Utils()

    def test_dimensional_list(self):
        """Testing dimesional list util
        """
        lists = [[1, 2, 3, 4, 5]]
        self.assertListEqual([1, 2, 3, 4, 5],
                             self.utils.dimensional_list(lists))

    def test_remove_dbs(self):
        """Testing removing doubles item from list
        """
        lists = [1, 2, 3, 3, 4, 5, 2, 1]
        self.assertListEqual([1, 2, 3, 4, 5], self.utils.remove_dbs(lists))

    def test_case_sensitive(self):
        """Testing case sensitive
        """
        lists = ['Vlc', 'OpenOffice', 'APScheduler']
        dictionary = {'vlc': 'Vlc',
                      'openoffice': 'OpenOffice',
                      'apscheduler': 'APScheduler'}
        self.assertDictEqual(dictionary, self.utils.case_sensitive(lists))


if __name__ == "__main__":
    unittest.main()
