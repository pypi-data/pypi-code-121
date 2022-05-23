import unittest
import os

class ImageSegmentationTestCase(unittest.TestCase):
    def test_presence_api(self):
        api_script = 'api.py'
        self.assertIn(api_script, os.listdir('.'), 'There is no api.py file in your project folder. If it is there, make sure it is named correctly, and that it is in the main folder. If you accidentally deleted it, you can type "reset_script"')

if __name__ == '__main__':

    unittest.main(verbosity=2)
    