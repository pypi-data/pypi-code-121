

import unittest
import datetime
import time
from .. import FileOperations


class TestFileOperations(unittest.TestCase):

    # @classmethod
    # def setUpClass(cls):
    #     cls.shared_resource = random.randint(1, 100)

    # @classmethod
    # def tearDownClass(cls):
    #     cls.shared_resource = None

    def setUp(self):
        self.file_ops = FileOperations(start_at_file_location=True)

    def tearDown(self):
        self.file_ops.delete_file('test.json')

    def test_update_json_if_time_elapsed(self):
        initial_write = self.file_ops.update_json_if_time_elapsed('test.json', 'GOOG', update_data={'price': 200, '200 Day SMA': 176})
        self.assertIn('last_updated', initial_write)

        data = self.file_ops.read_json('test.json')
        del data['GOOG']['last_updated']
        self.assertEqual(data, {
            'GOOG': {
                'price': 200,
                '200 Day SMA': 176
            }
        })

        time.sleep(1)
        # test that it wont update if sufficient time hasnt passed
        write_again = self.file_ops.update_json_if_time_elapsed('test.json', 'GOOG', update_data={'price': 200, '200 Day SMA': 176})
        self.assertFalse(write_again)

        # test that write happens when time_since_last_update param is less than the time passed
        third_write = self.file_ops.update_json_if_time_elapsed('test.json', 'GOOG', update_data={'price': 180, '200 Day SMA': 150}, time_since_last_update=datetime.timedelta(seconds=1))
        self.assertIn('last_updated', third_write)
        data = self.file_ops.read_json('test.json')
        del data['GOOG']['last_updated']
        self.assertEqual(data, {
            'GOOG': {
                'price': 180,
                '200 Day SMA': 150
            }
        })
