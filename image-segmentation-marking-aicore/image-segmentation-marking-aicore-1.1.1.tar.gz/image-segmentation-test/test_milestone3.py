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

    def test_save_to_s3_again(self):
        number_occurrences = self.api_code.count('save_image_to_s3')
        self.assertGreater(number_occurrences, 2, 'You should have called the "save_image_to_s3" function in the api.py file at least twice, one for the input and another one for the output. If you have, make sure it has the right syntax')
        bucket_name = self.user_id + '-data'
        number_occurrences_bucket = self.api_code.count(bucket_name)
        self.assertGreater(number_occurrences_bucket, 1, 'Looks like the second time you are uploading the image, you are using the wrong bucket')

    def test_output_in_s3(self):
        with open('output_files.txt', 'r') as f:
            output_file = f.read()
        with open('input_files.txt', 'r') as f:
            input_file = f.read()
        number_outputs = len(output_file.split('\n')) - 1
        self.assertGreater(number_outputs, 0, 'You haven\'t uploaded any image with the name "output.png". Make sure you are giving the right name to it')
        input_numbers = get_numbers(input_file)
        output_numbers = get_numbers(output_file)
        number_common = len(set(input_numbers).intersection(output_numbers))
        self.assertGreater(number_common, 0, 'You don\'t have any image with input and output in the same folder. Remember that, for each image, you have to store both input.png and output.png')

if __name__ == '__main__':

    unittest.main(verbosity=2)
    