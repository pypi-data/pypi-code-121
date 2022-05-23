import json
import urllib
from django.conf import settings
from datetime import datetime, timedelta
from rest_framework.test import APITestCase, APIClient

from djangoldp_account.models import LDPUser


class UpdateTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()

    def setUpLoggedInUser(self):
        self.user = LDPUser(email='test@mactest.co.uk', first_name='Test', last_name='Mactest', username='test',
                            password='glass onion')
        self.user.save()
        self.client.force_authenticate(user=self.user)

    def test_put_account_picture(self):
        self.setUpLoggedInUser()

        test_picture = "https://github.com/" + urllib.parse.quote("calummackervoy/calummackervoy.github.io/blob/master/assets/img/profile.jpg")

        payload = {
            "@context": {"@vocab": "http://happy-dev.fr/owl/#", "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
                         "rdfs": "http://www.w3.org/2000/01/rdf-schema#", "ldp": "http://www.w3.org/ns/ldp#",
                         "foaf": "http://xmlns.com/foaf/0.1/", "name": "rdfs:label",
                         "acl": "http://www.w3.org/ns/auth/acl#", "permissions": "acl:accessControl",
                         "mode": "acl:mode", "geo": "http://www.w3.org/2003/01/geo/wgs84_pos#", "lat": "geo:lat",
                         "lng": "geo:long", "entrepreneurProfile": "http://happy-dev.fr/owl/#entrepreneur_profile",
                         "mentorProfile": "http://happy-dev.fr/owl/#mentor_profile", "account": "hd:account",
                         "messageSet": "http://happy-dev.fr/owl/#message_set",
                         "author": "http://happy-dev.fr/owl/#author_user", "title": "http://happy-dev.fr/owl/#title"},
            '@id': settings.SITE_URL + "/accounts/{}/".format(self.user.account.slug),
            'picture': test_picture,
            'slug': self.user.slug
        }

        response = self.client.put('/accounts/{}/'.format(self.user.account.slug), data=json.dumps(payload), content_type='application/ld+json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.get('picture'), test_picture)
