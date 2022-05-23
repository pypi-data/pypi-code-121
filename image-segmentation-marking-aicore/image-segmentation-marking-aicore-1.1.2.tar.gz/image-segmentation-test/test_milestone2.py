import unittest
import os


class ImageSegmentationTestCase(unittest.TestCase):
    def setUp(self) -> None:
        api_script = 'api.py'
        with open(api_script, 'r') as f:
            self.api_code = f.read()
        self.user_id = os.environ['USER_ID']

    def test_perform(self):
        number_perform = self.api_code.count('perform_segmentation(')
        self.assertGreater(number_perform, 0, 'You should have called perform_segmentation model. If you have, make sure you used the right syntax')
        self.assertIn('segmented_image', self.api_code, 'You should assign the output of the perform_segmentation function to the "segmented_image" variable. If you have, make sure the name of the variable is correct')

    def test_print_segmented(self):
        self.assertIn('segmented_image.size', self.api_code, 'You should print the size of the segmented image. If you have, make sure it has the right syntax')

if __name__ == '__main__':

    unittest.main(verbosity=2)
    