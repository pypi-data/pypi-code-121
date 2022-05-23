from django.contrib.auth import get_user_model
from rest_framework.test import APIClient, APITestCase
from djangoldp.tests.models import User, Project
import cProfile, pstats, io


class TestPerformance(APITestCase):
    fixtures = ['test.json',]

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(username='john', email='jlennon@beatles.com',
                                                         password='glass onion')
        self.client.force_authenticate(user=self.user)
        print('there are ' + str(Project.objects.count()) + ' projects in the database')
        print('there are ' + str(User.objects.count()) + ' users in the database')

    def _print_stats(self, pr):
        s = io.StringIO()
        ps = pstats.Stats(pr, stream=s)
        ps.print_stats()
        print(s.getvalue())

    def _enable_new_profiler(self):
        pr = cProfile.Profile()
        pr.enable()
        return pr

    def test_get_container(self):
        pr = self._enable_new_profiler()
        response = self.client.get('/projects/', content_type='application/ld+json')
        self.assertEqual(response.status_code, 200)
        print('counted ' + str(len(response.data['ldp:contains'])) + ' projects')
        pr.disable()
        self._print_stats(pr)

        pr = self._enable_new_profiler()
        response = self.client.get('/users/', content_type='application/ld+json')
        self.assertEqual(response.status_code, 200)
        print('counted ' + str(len(response.data['ldp:contains'])) + ' users')
        pr.disable()
        self._print_stats(pr)
