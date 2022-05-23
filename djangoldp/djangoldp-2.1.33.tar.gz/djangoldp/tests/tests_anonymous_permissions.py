import json

from django.test import TestCase
from rest_framework.test import APIClient

from djangoldp.tests.models import JobOffer


class TestAnonymousUserPermissions(TestCase):
    def setUp(self):
        self.client = APIClient(enforce_csrf_checks=True)
        self.job = JobOffer.objects.create(title="job", slug=1)

    def test_get_request_for_anonymousUser(self):
        response = self.client.get('/job-offers/')
        self.assertEqual(response.status_code, 200)

    def test_get_1_request_for_anonymousUser(self):
        response = self.client.get('/job-offers/1/')
        self.assertEqual(response.status_code, 200)

    def test_post_request_for_anonymousUser(self):
        post = {'title': "job_created"}
        response = self.client.post('/job-offers/', data=json.dumps(post), content_type='application/ld+json')
        self.assertEqual(response.status_code, 403)

    # TODO: test POST request for anonymous user where it's allowed

    def test_put_request_for_anonymousUser(self):
        body = {'title':"job_updated"}
        response = self.client.put('/job-offers/{}/'.format(self.job.pk), data=json.dumps(body),
                                   content_type='application/ld+json')
        self.assertEqual(response.status_code, 403)
    
    def test_patch_request_for_anonymousUser(self):
        response = self.client.patch('/job-offers/' + str(self.job.pk) + "/",
                                   content_type='application/ld+json')
        self.assertEqual(response.status_code, 403)
