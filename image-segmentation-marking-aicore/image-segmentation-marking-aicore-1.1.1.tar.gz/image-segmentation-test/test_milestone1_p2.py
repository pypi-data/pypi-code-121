import unittest
import os

# print(process)

class ImageSegmentationTestCase(unittest.TestCase):
    def setUp(self) -> None:
        api_script = 'api.py'
        with open(api_script, 'r') as f:
            self.api_code = f.read()
        self.user_id = os.environ['USER_ID']


    def test_netcat(self):
        number_calls = int(os.environ['NETCAT_CALLS'])
        self.assertGreater(number_calls, 0, 'You should have called netcat server to listen port 8080 at least once')
    
    def test_print_image_name(self):
        self.assertIn('print(image_name)', self.api_code, 'You should print the image name in the api.py file. If you have, make sure it has the right syntax')

    def test_decoding_image(self):
        self.assertIn('decode_image(image)', self.api_code, 'You should call the decode_image on the image in the api.py file. If you have, make sure it has the right syntax')
        self.assertIn('decoded_image', self.api_code, 'You haven\'t assigned the decoded image to any variable. If you have, make sure the variable is called "decoded_image"')
        self.assertIn('decoded_image.size', self.api_code, 'You are not printing the size of the decoded image. If you are, remember that the variable should be named "decoded_image"')
    
    def test_save_to_s3(self):
        number_occurrences = self.api_code.count('save_image_to_s3')
        self.assertGreater(number_occurrences, 1, 'You should have called the "save_image_to_s3" function in the api.py file. If you have, make sure it has the right syntax')
        bucket_name = self.user_id + '-data'
        self.assertIn(bucket_name, self.api_code, 'You are not using the right name for your bucket. The name of the bucket should look like an id followed by -data. Something like xxxx-xxxxx-xxxx-xxxx-data')

    def test_check_images_in_s3(self):
        number_input_images = int(os.environ['NUMBER_INPUT_IMAGES'])
        self.assertGreater(number_input_images, 0, 'You should have uploaded at least one image to S3. If you have, make sure you have the right number of images in your bucket')

if __name__ == '__main__':

    unittest.main(verbosity=2)
    