import unittest
from sdap.data_access.index.temporal import Daily


class DailyTestCase(unittest.TestCase):
    def test_get_codes(self):

        daily_index = Daily(format='%Y%j')
        time_range = ['2017-05-19T00:00:00.000000+00:00', '2017-05-21T00:00:00.000000+00:00']
        codes = daily_index.get_codes(time_range)

        assert codes == ['2017139', '2017140']




if __name__ == '__main__':
    unittest.main()
