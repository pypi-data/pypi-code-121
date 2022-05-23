import uuid
import json
from datetime import datetime, timedelta

from djangoldp.permissions import LDPPermissions

from rest_framework.test import APITestCase, APIClient
from guardian.shortcuts import assign_perm

from djangoldp_circle.models import Circle, CircleMember, CircleAccessRequest
from djangoldp_circle.tests.utils import get_random_user


class PermissionsTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()

    def setUpLoggedInUser(self):
        self.user = get_random_user()
        self.client.force_authenticate(user=self.user)

    def _get_random_circle(self, status_choice='Public', owner=None):
        if owner is None:
            owner = self.user

        return Circle.objects.create(name='Test', status=status_choice, owner=owner)

    def setUpCircle(self, status_choice='Public', owner=None):
        self.circle = self._get_random_circle(status_choice, owner)

    def _get_circle_member_request_json(self, user, circle=None):
        res = self._get_request_json(user=user.urlid)

        if circle is not None:
            res.update({'circle': {'@id': circle.urlid}})

        return res

    def _get_request_json(self, **kwargs):
        res = {
            '@context': {
                '@vocab': "http://happy-dev.fr/owl/#",
                'rdf': "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
                'rdfs': "http://www.w3.org/2000/01/rdf-schema#",
                'ldp': "http://www.w3.org/ns/ldp#",
                'foaf': "http://xmlns.com/foaf/0.1/",
                'name': "rdfs:label",
                'acl': "http://www.w3.org/ns/auth/acl#",
                'permissions': "acl:accessControl",
                'mode': "acl:mode",
                'inbox': "http://happy-dev.fr/owl/#inbox",
                'object': "http://happy-dev.fr/owl/#object",
                'author': "http://happy-dev.fr/owl/#author",
                'account': "http://happy-dev.fr/owl/#account",
                'jabberID': "foaf:jabberID",
                'picture': "foaf:depiction",
                'firstName': "http://happy-dev.fr/owl/#first_name",
                'lastName': "http://happy-dev.fr/owl/#last_name",
                'isAdmin': "http://happy-dev.fr/owl/#is_admin"
            }
        }

        for kwarg in kwargs:
            if isinstance(kwargs[kwarg], str):
                res.update({kwarg: {'@id': kwargs[kwarg]}})
            else:
                res.update({kwarg: kwargs[kwarg]})

        return res

    # list circles - not logged in
    def test_list_circles_anonymous_user(self):
        another_user = get_random_user()
        self.setUpCircle('Public', another_user)
        response = self.client.get('/circles/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['ldp:contains']), 1)

    # GET circle - not logged in
    def test_get_circle_public_anonymous_user(self):
        another_user = get_random_user()
        self.setUpCircle('Public', another_user)

        response = self.client.get('/circles/1/')
        self.assertEqual(response.status_code, 200)

    # list circles - not include private circles
    def test_list_circles(self):
        self.setUpLoggedInUser()
        # a public circle, a private circle I own and a private circle I'm not in
        another_user = get_random_user()
        public_circle = self._get_random_circle('Public', another_user)
        my_circle = self._get_random_circle('Private', self.user)
        private_circle = self._get_random_circle('Private', another_user)
        restricted_circle = self._get_random_circle('Restricted', another_user)

        response = self.client.get('/circles/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['ldp:contains']), 3)

    # GET circle public
    def test_get_public_circle(self):
        self.setUpLoggedInUser()
        another_user = get_random_user()
        self.setUpCircle('Public', another_user)

        response = self.client.get('/circles/1/')
        self.assertEqual(response.status_code, 200)

    # GET circle private - I am a member
    def test_get_circle_private_member(self):
        self.setUpLoggedInUser()
        self.setUpCircle('Private')

        response = self.client.get('/circles/1/')
        self.assertEqual(response.status_code, 200)

    # GET circle private - I am not a member
    def test_get_circle_private_not_member(self):
        self.setUpLoggedInUser()
        another_user = get_random_user()

        self.setUpCircle('Private', another_user)

        response = self.client.get('/circles/1/')
        self.assertEqual(response.status_code, 404)

    # POST a new circle - anyone authenticated can do this
    def test_post_circle(self):
        self.setUpLoggedInUser()

        response = self.client.post('/circles/', json.dumps({}), content_type='application/ld+json')
        self.assertEqual(response.status_code, 201)

    # POST a new circle - anonymous user
    def test_post_circle_anonymous_user(self):
        response = self.client.post('/circles/')
        self.assertEqual(response.status_code, 403)

    # PATCH circle public - denied
    def test_patch_public_circle(self):
        self.setUpLoggedInUser()
        another_user = get_random_user()

        self.setUpCircle('Public', another_user)

        response = self.client.patch('/circles/1/', json.dumps({}), content_type='application/ld+json')
        self.assertEqual(response.status_code, 403)

    # PATCH circle - I am a member but not an admin - denied
    def test_patch_circle_not_admin(self):
        self.setUpLoggedInUser()
        another_user = get_random_user()

        self.setUpCircle('Public', another_user)
        CircleMember.objects.create(circle=self.circle, user=self.user, is_admin=False)

        response = self.client.patch('/circles/1/', json.dumps({}), content_type='application/ld+json')
        self.assertEqual(response.status_code, 403)

    # PATCH circle - I am an admin
    def test_patch_circle_admin(self):
        self.setUpLoggedInUser()
        another_user = get_random_user()

        self.setUpCircle('Private', another_user)
        CircleMember.objects.create(circle=self.circle, user=self.user, is_admin=True)

        response = self.client.patch('/circles/1/')
        self.assertEqual(response.status_code, 200)

    # adding a CircleMember - I am not a member myself
    def test_post_circle_member_not_member(self):
        self.setUpLoggedInUser()
        another_user = get_random_user()

        self.setUpCircle('Private', another_user)

        payload = self._get_request_json(circle=self.circle.urlid, user=another_user.urlid)

        response = self.client.post('/circle-members/', json.dumps(payload), content_type='application/ld+json')
        self.assertEqual(response.status_code, 403)

    def test_post_circle_member_nested_not_member(self):
        self.setUpLoggedInUser()
        another_user = get_random_user()

        self.setUpCircle('Private', another_user)

        payload = self._get_circle_member_request_json(self.user, self.circle)

        response = self.client.post('/circles/1/members/', json.dumps(payload), content_type='application/ld+json')
        self.assertEqual(response.status_code, 403)

        # TODO
        '''payload.pop('user')
        response = self.client.post('/users/{}/circles/'.format(self.user.pk), data=json.dumps(payload),
                                    content_type='application/ld+json')
        self.assertEqual(response.status_code, 403)'''

    # adding a CircleMember - I am a member but not an admin
    def test_post_circle_member(self):
        self.setUpLoggedInUser()
        another_user = get_random_user()

        self.setUpCircle('Private', another_user)
        CircleMember.objects.create(circle=self.circle, user=self.user, is_admin=False)

        payload = self._get_circle_member_request_json(self.user)

        response = self.client.post('/circles/1/members/', json.dumps(payload), content_type='application/ld+json')
        self.assertEqual(response.status_code, 201)

    # removing a CircleMember - I am not an admin
    def test_delete_circle_member(self):
        self.setUpLoggedInUser()
        another_user = get_random_user()

        self.setUpCircle('Private', another_user)
        CircleMember.objects.create(circle=self.circle, user=self.user, is_admin=False)

        response = self.client.delete('/circle-members/1/')
        self.assertEqual(response.status_code, 403)

    # removing a circle member - I am not logged in
    def test_delete_circle_member_anonymous_user(self):
        another_user = get_random_user()
        self.setUpCircle('Private', another_user)

        response = self.client.delete('/circle-members/1/')
        self.assertEqual(response.status_code, 403)

    # removing myself from CircleMember - I am not an admin
    def test_delete_myself_circle_member(self):
        self.setUpLoggedInUser()
        another_user = get_random_user()

        self.setUpCircle('Private', another_user)
        CircleMember.objects.create(circle=self.circle, user=self.user, is_admin=False)

        response = self.client.delete('/circle-members/2/')
        self.assertEqual(response.status_code, 204)

    # adding a CircleMember - I am an admin
    def test_post_circle_member_admin(self):
        self.setUpLoggedInUser()
        self.setUpCircle('Private', self.user)

        another_user = get_random_user()

        body = self._get_circle_member_request_json(another_user, self.circle)

        response = self.client.post('/circle-members/', data=json.dumps(body),
                                    content_type='application/ld+json')
        self.assertEqual(response.status_code, 201)
        circle = Circle.objects.get(pk=self.circle.pk)
        self.assertEqual(len(circle.members.all()), 2)

    # adding a CircleMember - nested field
    def test_post_circle_member_nested_admin(self):
        self.setUpLoggedInUser()
        self.setUpCircle('Private', self.user)

        another_user = get_random_user()
        body = self._get_circle_member_request_json(another_user)

        response = self.client.post('/circles/1/members/', data=json.dumps(body),
                                    content_type='application/ld+json')
        self.assertEqual(response.status_code, 201)
        circle = Circle.objects.get(pk=self.circle.pk)
        self.assertEqual(len(circle.members.all()), 2)

        another_user = get_random_user()
        body = self._get_circle_member_request_json(another_user, self.circle)

        response = self.client.post('/users/{}/circles/'.format(another_user.username), data=json.dumps(body),
                                    content_type='application/ld+json')
        self.assertEqual(response.status_code, 201)
        circle = Circle.objects.get(pk=self.circle.pk)
        self.assertEqual(len(circle.members.all()), 3)

    def test_post_circle_member_no_circle_passed(self):
        self.setUpLoggedInUser()
        self.setUpCircle('Private', self.user)

        another_user = get_random_user()
        body = self._get_circle_member_request_json(another_user)
        response = self.client.post('/users/{}/members/'.format(another_user.pk), data=json.dumps(body),
                                    content_type='application/ld+json')
        self.assertEqual(response.status_code, 404)

    # removing a CircleMember - I am an admin
    def test_delete_circle_member_admin(self):
        self.setUpLoggedInUser()
        self.setUpCircle('Private', self.user)

        another_user = get_random_user()
        CircleMember.objects.create(circle=self.circle, user=another_user, is_admin=False)

        response = self.client.delete('/circle-members/2/')
        self.assertEqual(response.status_code, 204)

    # removing another admin from the Circle
    def test_delete_circle_admin(self):
        self.setUpLoggedInUser()
        self.setUpCircle('Private')

        another_user = get_random_user()
        CircleMember.objects.create(circle=self.circle, user=another_user, is_admin=True)

        response = self.client.delete('/circle-members/2/')
        self.assertEqual(response.status_code, 403)

    # removing myself from Circle - I am an admin, but I'm the last admin
    def test_delete_circle_member_admin_last_admin(self):
        self.setUpLoggedInUser()
        self.setUpCircle('Private')

        another_user = get_random_user()
        CircleMember.objects.create(circle=self.circle, user=another_user, is_admin=False)

        response = self.client.delete('/circle-members/1/')
        self.assertEqual(response.status_code, 403)

    # removing myself from Circle - I am an admin, and I'm not the last admin
    def test_delete_circle_member_admin_not_last_admin(self):
        self.setUpLoggedInUser()
        self.setUpCircle('Private')

        another_user = get_random_user()
        CircleMember.objects.create(circle=self.circle, user=another_user, is_admin=True)

        self.assertEqual(self.circle.members.count(), 2)
        self.assertEqual(self.circle.members.all()[0].user, self.user)
        self.assertEqual(self.circle.members.all()[0].is_admin, True)

        response = self.client.delete('/circle-members/1/')
        self.assertEqual(response.status_code, 204)

    # PATCH circle-member - I am not an admin
    def test_patch_circle_member_not_admin(self):
        self.setUpLoggedInUser()
        another_user = get_random_user()

        self.setUpCircle('Private', another_user)
        CircleMember.objects.create(circle=self.circle, user=self.user, is_admin=False)

        response = self.client.patch('/circle-members/1/')
        self.assertEqual(response.status_code, 403)

    # make another admin - I am a circle member
    def test_make_circle_member_admin(self):
        self.setUpLoggedInUser()
        self.setUpCircle('Private', self.user)

        another_user = get_random_user()
        CircleMember.objects.create(circle=self.circle, user=another_user, is_admin=False)

        body = self._get_request_json(is_admin=True)

        response = self.client.patch('/circle-members/2/', json.dumps(body), content_type='application/ld+json')

        self.assertEqual(response.status_code, 200)

        cm = CircleMember.objects.get(pk=2)
        self.assertEqual(cm.is_admin, True)

    # test that django guardian object-level permission is applied
    def test_guardian_view_applied(self):
        self.setUpLoggedInUser()
        another_user = get_random_user()
        self.setUpCircle('Private', another_user)

        assign_perm('view_circle', self.user, self.circle)

        response = self.client.get('/circles/1/')

        self.assertEqual(response.status_code, 200)

    # even with object-permission, I can't remove an admin
    def test_delete_circle_admin_guardian(self):
        self.setUpLoggedInUser()
        another_user = get_random_user()
        self.setUpCircle('Private', another_user)

        assign_perm('delete_circle', self.user, self.circle)
        assign_perm('view_circle', self.user, self.circle)

        response = self.client.delete('/circle-members/2/')

        self.assertEqual(response.status_code, 404)

    # security test - admin changing which circle they are an admin of
    def test_hack_myself_admin_of_another_circle(self):
        self.setUpLoggedInUser()
        self.setUpCircle('Private', self.user)

        another_user = get_random_user()
        circle = Circle.objects.create(name='Test 2', status='Private', owner=another_user)

        payload = self._get_request_json(circle=circle.urlid)

        response = self.client.patch('/circle-members/1/', json.dumps(payload), content_type='application/ld+json')
        self.assertEqual(response.status_code, 403)

        cm = CircleMember.objects.get(pk=1)
        self.assertEqual(cm.circle.pk, self.circle.pk)

    def test_hack_otheruser_member_of_another_circle(self):
        self.setUpLoggedInUser()
        self.setUpCircle('Private', self.user)

        my_accomplice = get_random_user()
        CircleMember.objects.create(circle=self.circle, user=my_accomplice, is_admin=False)

        another_user = get_random_user()
        circle = Circle.objects.create(name='Test 2', status='Private', owner=another_user)

        payload = self._get_request_json(circle=circle.urlid, is_admin=True)

        response = self.client.patch('/circle-members/1/', data=json.dumps(payload),
                                     content_type='application/ld+json')
        self.assertEqual(response.status_code, 403)

        cm = CircleMember.objects.get(pk=1)
        self.assertEqual(cm.circle.pk, self.circle.pk)

    def test_hack_post_circle_member_to_admin(self):
        self.setUpLoggedInUser()
        another_user = get_random_user()
        self.setUpCircle('Private', another_user)

        payload = self._get_request_json(circle=self.circle.urlid, user=self.user.urlid, is_admin=True)

        response = self.client.post('/circles/1/members/', data=json.dumps(payload), content_type='application/ld+json')
        self.assertEqual(response.status_code, 403)

    def test_hack_post_circle_member_again_to_admin(self):
        self.setUpLoggedInUser()
        another_user = get_random_user()
        self.setUpCircle('Private', another_user)

        CircleMember.objects.create(user=self.user, circle=self.circle, is_admin=False)

        payload = self._get_request_json(circle=self.circle.urlid, user=self.user.urlid, is_admin=True)

        self.client.post('/circles/1/members/', data=json.dumps(payload), content_type='application/ld+json')
        self.assertFalse(CircleMember.objects.filter(user=self.user, circle=self.circle, is_admin=True).exists())

    def test_update_circle_owner_distant(self):
        self.setUpLoggedInUser()
        self.setUpCircle('Public', self.user)

        owner_id = "https://distant.com/users/1/"

        payload = self._get_request_json(owner=owner_id)
        payload.update({'@id': self.circle.urlid})

        response = self.client.patch('/circles/{}/'.format(self.circle.pk),
                                     data=json.dumps(payload), content_type='application/ld+json')
        self.assertEqual(response.status_code, 200)

        circle = Circle.objects.get(pk=self.circle.pk)
        self.assertEqual(circle.owner.urlid, owner_id)
    
    def test_make_access_request(self):
        self.setUpLoggedInUser()
        self.setUpCircle('Restrict', get_random_user())
        
        payload = self._get_request_json(circle=self.circle.urlid)

        response = self.client.post('/circles/{}/access_requests/'.format(self.circle.pk),
                                    data=json.dumps(payload), content_type='application/ld+json')
        self.assertEqual(response.status_code, 201)
        ar = CircleAccessRequest.objects.filter(user=self.user)[0]
        self.assertEqual(ar.circle, self.circle)

    def test_accept_access_request(self):
        self.setUpLoggedInUser()
        self.setUpCircle('Restrict', get_random_user())

        CircleMember.objects.create(circle=self.circle, user=self.user, is_admin=True)
        other_user = get_random_user()
        ar = CircleAccessRequest.objects.create(circle=self.circle, user=other_user, status='Pending')
        self.assertFalse(CircleMember.objects.filter(user=other_user, circle=self.circle).exists())

        payload = self._get_request_json()
        payload.update({
            'status': 'Accepted'
        })

        response = self.client.patch('/circleaccessrequests/{}/'.format(ar.pk),
                                     data=json.dumps(payload), content_type='application/ld+json')
        self.assertEqual(response.status_code, 200)
        ar = self.circle.access_requests.all()[0]
        self.assertEqual(ar.status, payload['status'])
        self.assertTrue(CircleMember.objects.filter(user=other_user, circle=self.circle).exists())
    
    def test_respond_access_request_not_admin(self):
        self.setUpLoggedInUser()
        self.setUpCircle('Restrict', get_random_user())

        CircleMember.objects.create(circle=self.circle, user=self.user, is_admin=False)
        ar = CircleAccessRequest.objects.create(circle=self.circle, user=get_random_user(), status='Pending')

        payload = self._get_request_json()
        payload.update({
            'status': 'Accepted'
        })

        response = self.client.patch('/circleaccessrequests/{}/'.format(ar.pk),
                                     data=json.dumps(payload), content_type='application/ld+json')
        self.assertEqual(response.status_code, 404)
