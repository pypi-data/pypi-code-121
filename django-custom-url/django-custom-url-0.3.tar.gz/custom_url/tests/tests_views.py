from unittest.mock import MagicMock
from django.core.files import File
from django.test import TestCase
from custom_url.models import CustomUrl

class CustomUrlViewTestCase(TestCase):

    def setUp(self):
        # Mocking a txt file
        self.file_mock = MagicMock(spec=File, name='FileMock')
        self.file_mock.name = 'my_file.txt'
        CustomUrl.objects.create(url='/hi/', file=self.file_mock, file_type='text/plain')
    
    def test_view_url_exists_at_desired_location(self):
        """Testing view catches a Custom URL"""
        response = self.client.get('/hi/')
        self.assertEqual(response.status_code, 200)
    
    def test_view_url_return_desired_content_type(self):
        """Testing response's content type matches the content type of a Custom URL object"""
        response = self.client.get('/hi/')
        obj = CustomUrl.objects.get()
        self.assertEqual(response.headers['Content-Type'], obj.file_type)
    
    def test_view_url_return_404(self):
        """Testing response return error 404 if Custom URL doesn't exists"""
        response = self.client.get('/not-found/')
        self.assertEqual(response.status_code, 404)