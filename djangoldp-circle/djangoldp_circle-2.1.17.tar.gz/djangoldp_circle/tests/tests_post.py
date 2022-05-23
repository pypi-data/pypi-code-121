import uuid
import json
from datetime import datetime, timedelta
from rest_framework.test import APITestCase, APIClient
from guardian.shortcuts import assign_perm

from djangoldp_circle.models import Circle, CircleMember, manage_deleted_owner
from djangoldp_circle.tests.utils import get_random_user


class PostTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()

    def setUpLoggedInUser(self):
        self.user = get_random_user()
        self.client.force_authenticate(user=self.user)

    def test_post_circle(self):
        self.setUpLoggedInUser()

        body = {
          "status":"Public",
          "linebreak":"",
          "name":"test1",
          "subtitle":"test1",
          "description":"\n",
          "help":"",
          "@context": {
            "@vocab":"http://happy-dev.fr/owl/#",
            "rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#",
            "rdfs":"http://www.w3.org/2000/01/rdf-schema#",
            "ldp":"http://www.w3.org/ns/ldp#",
            "foaf":"http://xmlns.com/foaf/0.1/",
            "name":"rdfs:label",
            "description":"rdfs:comment",
            "acl":"http://www.w3.org/ns/auth/acl#",
            "permissions":"acl:accessControl",
            "mode":"acl:mode",
            "geo":"http://www.w3.org/2003/01/geo/wgs84_pos#",
            "lat":"geo:lat",
            "lng":"geo:long",
            "inbox":"http://happy-dev.fr/owl/#inbox",
            "object":"http://happy-dev.fr/owl/#object",
            "author":"http://happy-dev.fr/owl/#author",
            "account":"http://happy-dev.fr/owl/#account",
            "jabberID":"foaf:jabberID",
            "picture":"foaf:depiction"
          }
        }

        response = self.client.post('/circles/', data=json.dumps(body), content_type='application/ld+json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Circle.objects.count(), 1)

    def test_post_circle_missing_data(self):
        self.setUpLoggedInUser()

        body = {
            "description": "\n",
            "@context": {
                "@vocab": "http://happy-dev.fr/owl/#",
                # notice the missing context
                # "description":"rdfs:comment",
            }
        }

        response = self.client.post('/circles/', data=json.dumps(body), content_type='application/ld+json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Circle.objects.count(), 1)
