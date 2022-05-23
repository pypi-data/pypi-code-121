import unittest
import os

def get_numbers(files):
    numbers = []
    for image in files.split('"Key": "')[1:]:
        numbers.append(image.split('/')[0])
    return numbers

class ImageSegmentationTestCase(unittest.TestCase):
    def setUp(self) -> None:
        api_script = 'api.py'
        with open(api_script, 'r') as f:
            self.api_code = f.read()
        self.user_id = os.environ['USER_ID']

    def test_nohup(self):
        number_occurrences = int(os.environ['NOHUP_CALLS'])
        self.assertGreater(number_occurrences, 0, 'You should use the nohup command to run Python on the background')
        python_background = int(os.environ['PYTHON_BACKGROUND'])
        self.assertGreater(python_background, 0, 'Looks like Python is not running on the background. You can use the nohup command to run it on the background')

    def test_ip_dig(self):
        ip_dig_calls = int(os.environ['IP_DIG'])
        self.assertGreater(ip_dig_calls, 0, 'Looks like you haven\'t call the "dig +short myip.opendns.com @resolver1.opendns.com" command to check your public IPv4 address. You will need it to check your Prometheus dashboard')
if __name__ == '__main__':

    unittest.main(verbosity=2)
    