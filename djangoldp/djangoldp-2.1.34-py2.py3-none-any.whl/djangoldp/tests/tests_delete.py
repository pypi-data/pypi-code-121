from django.test import TestCase
from rest_framework.test import APIRequestFactory, APIClient

from djangoldp.tests.models import Post


class TestDelete(TestCase):

    def setUp(self):
        self.factory = APIRequestFactory()
        self.client = APIClient()

    def tearDown(self):
        pass

    def test_delete(self):
        post = Post.objects.create(content="content")
        response = self.client.delete('/posts/{}/'.format(post.pk), content_type='application/ld+json')
        self.assertEqual(response.status_code, 204)

        self.assertEqual(Post.objects.filter(pk=post.pk).count(), 0)
