from rest_framework.test import APIRequestFactory, APIClient, APITestCase

from djangoldp.models import LDPSource


class TestSource(APITestCase):

    def setUp(self):
        self.factory = APIRequestFactory()
        self.client = APIClient()

    def tearDown(self):
        pass

    def test_get_resource(self):
        source = LDPSource.objects.create(federation="source_name", urlid="http://bar.foo/")
        response = self.client.get('/sources/{}/'.format(source.federation), content_type='application/ld+json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['@id'], 'http://happy-dev.fr/sources/source_name/')
        self.assertEqual(len(response.data['ldp:contains']), 1)

    def test_get_empty_resource(self):
        response = self.client.get('/sources/{}/'.format('unknown'), content_type='application/ld+json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['@id'], 'http://happy-dev.fr/sources/unknown/')
        self.assertEqual(len(response.data['ldp:contains']), 0)
