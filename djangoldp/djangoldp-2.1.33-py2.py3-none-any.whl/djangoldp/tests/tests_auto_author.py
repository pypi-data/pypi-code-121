import json

from django.contrib.auth import get_user_model
from rest_framework.test import APIRequestFactory, APIClient, APITestCase
from djangoldp.tests.models import UserProfile


class TestAutoAuthor(APITestCase):

    def setUp(self):
        self.factory = APIRequestFactory()
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(username='john', email='jlennon@beatles.com', password='glass onion')
        UserProfile.objects.create(user=self.user)

    def tearDown(self):
        self.user.delete()

    def test_save_with_anonymous_user(self):
        post = {
            '@graph': [{'http://happy-dev.fr/owl/#content': "post content"}]}

        response = self.client.post('/posts/', data=json.dumps(post), content_type='application/ld+json')
        self.assertEqual(response.status_code, 201)
        self.assertEquals(response.data['content'], "post content")

    def test_auto_author_field(self):
        self.client.force_authenticate(user=self.user)
        post = {
            '@graph': [{'http://happy-dev.fr/owl/#content': "post content"}]}

        response = self.client.post('/posts/', data=json.dumps(post), content_type='application/ld+json')
        self.assertEqual(response.status_code, 201)
        self.assertEquals(response.data['content'], "post content")
        self.assertIsNotNone(response.data['author'])
