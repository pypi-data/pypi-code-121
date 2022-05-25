from rest_framework.test import APIRequestFactory, APIClient, APITestCase

from djangoldp.tests.models import Post


class TestPagination(APITestCase):

    def setUp(self):
        self.factory = APIRequestFactory()
        self.client = APIClient()
        for i in range(0, 10):
            Post.objects.create(content="content {}".format(i))

    def tearDown(self):
        pass

    def test_next(self):
        response = self.client.get('/posts/', content_type='application/ld+json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('link', response._headers)
        self.assertEquals(response._headers['link'][1], '<http://testserver/posts/?limit=5&offset=5>; rel="next"')

    def test_previous(self):
        response = self.client.get('/posts/?offset=2&limit=2', content_type='application/ld+json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('link', response._headers)
        self.assertEquals(response._headers['link'][1],
                          '<http://testserver/posts/?limit=2>; rel="prev", <http://testserver/posts/?limit=2&offset=4>; rel="next"')
