from unittest.mock import MagicMock
from django.core.exceptions import ValidationError
from django.core.files import File
from django.test import TestCase
from custom_url.models import CustomUrl

class CustomUrlTestCase(TestCase):
    
    def setUp(self):
        # Mocking a txt file
        self.file_mock = MagicMock(spec=File, name='FileMock')
        self.file_mock.name = 'my_file.txt'

        # Mocking an HTML file
        self.html_file_mock = MagicMock(spec=File, name='FileMock')
        self.html_file_mock.name = 'index.html'

    def test_custom_url_creation(self):
        """Testing creation of a Custom URL"""
        obj = CustomUrl.objects.create(url='/hi/', file=self.file_mock, file_type='text/plain')
        obj.full_clean()
        self.assertTrue(isinstance(obj, CustomUrl))
    
    def test_custom_url_file_extension_validation_error(self):
        """Testing ValidationError raises when file extension is invalid"""
        with self.assertRaises(ValidationError):
            obj = CustomUrl.objects.create(url='/hi/', file=self.html_file_mock, file_type='text/plain')
            obj.full_clean()
    
    def test_custom_url_file_type_validation_error(self):
        """Testing ValidationError raises when file type is invalid"""
        with self.assertRaises(ValidationError):
            obj = CustomUrl.objects.create(url='/hi/', file=self.file_mock, file_type='bad/type')
            obj.full_clean()