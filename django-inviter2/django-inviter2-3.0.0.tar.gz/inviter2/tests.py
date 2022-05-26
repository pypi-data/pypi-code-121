"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
from __future__ import unicode_literals

from shortuuid import uuid

from urllib.parse import urlparse

from django.contrib.auth import get_user_model
from django.core import mail
from django.urls import reverse as _reverse
from django.http import Http404
from django.test import TestCase
from django.utils.http import int_to_base36

from . import settings
from .models import OptOut
from .utils import invite, token_generator
from .views import UserMixin


User = get_user_model()

def reverse(view, *args, **kwargs):
    view = '{}:{}'.format(settings.NAMESPACE, view)
    return _reverse(view, *args, **kwargs)


class InviteTest(TestCase):
    def setUp(self):
        self.required_fields = getattr(User, 'REQUIRED_FIELDS', [])
        self.required_fields.append(
            getattr(User, 'USERNAME_FIELD', 'username'))
        if 'username' in self.required_fields:
            self.inviter = User.objects.create(username=uuid())
            self.existing = User.objects.create(
                email='existing@example.com', username=uuid())
        else:
            self.inviter = User.objects.create()
            self.existing = User.objects.create(email='existing@example.com')

    def test_inviting(self):
        user, sent = invite("foo@example.com", self.inviter)
        self.assertTrue(sent)
        self.assertFalse(user.is_active)
        self.assertEqual(1, len(mail.outbox))
        self.assertEqual(3, User.objects.count())

        # Resend the mail
        user, sent = invite("foo@example.com", self.inviter)
        self.assertTrue(sent)
        self.assertFalse(user.is_active)
        self.assertEqual(2, len(mail.outbox))
        self.assertEqual(3, User.objects.count())

        # Don't resend the mail
        user, sent = invite("foo@example.com", self.inviter, resend=False)
        self.assertFalse(sent)
        self.assertFalse(user.is_active)
        self.assertEqual(2, len(mail.outbox))
        self.assertEqual(3, User.objects.count())

        # Don't send the email to active users
        user, sent = invite("existing@example.com", self.inviter)
        self.assertFalse(sent)
        self.assertTrue(user.is_active)
        self.assertEqual(2, len(mail.outbox))
        self.assertEqual(3, User.objects.count())

    def test_reinvite_user(self):
        self.existing.is_active = False
        self.existing.save()

        user, sent = invite("existing@example.com", self.inviter,
                            user=self.existing)
        self.assertTrue(sent)
        self.assertFalse(user.is_active)
        self.assertEqual(1, len(mail.outbox))
        self.assertEqual(2, User.objects.count())

    def test_views(self):
        user, sent = invite("foo@example.com", self.inviter)
        self.assertTrue(sent)
        url_parts = int_to_base36(user.id), token_generator.make_token(user)

        url = reverse('register', args=url_parts)

        resp = self.client.get(url)

        self.assertEqual(200, resp.status_code, resp.status_code)
        
        fields = {
            'email': 'foo@example.com',
            'password1': 'test-1234',
            'password2': 'test-1234'
        }
        if 'username' in self.required_fields:
            fields.update(username='testuser')
        
        resp = self.client.post(url, fields)

        self.assertEqual(302, resp.status_code, resp.content)

        # self.client.login(username='testuser', password='test-1234')

        resp = self.client.get(reverse('done'))

        self.assertEqual(200, resp.status_code, resp.status_code)

    def test_error_views(self):
        # invalid base36 encoded user id
        user, sent = invite("foo@example.com", self.inviter)
        self.assertTrue(sent)
        url_parts = 'z' * 13, token_generator.make_token(user)
        url = reverse('register', args=url_parts)
        resp = self.client.get(url)
        self.assertEqual(404, resp.status_code, resp.status_code)

        # attempt to use some other user's id
        user, sent = invite("foo@example.com", self.inviter)
        self.assertTrue(sent)
        uid = int_to_base36(self.existing.id)
        token = token_generator.make_token(user)
        url = reverse('register', args=(uid, token))
        resp = self.client.get(url)
        self.assertEqual(403, resp.status_code, resp.status_code)

        # submit an invalid form
        user, sent = invite("foo@example.com", self.inviter)
        self.assertTrue(sent)
        url_parts = int_to_base36(user.id), token_generator.make_token(user)
        url = reverse('register', args=url_parts)
        resp = self.client.get(url)
        self.assertEqual(200, resp.status_code, resp.status_code)
        
        fields = {
            'email': 'foo@example.com',
            'password1': 'test-1234',
            'password2': 'test-4321'
        }
        if 'username' in self.required_fields:
            fields.update(username='testuser')
        
        resp = self.client.post(url, fields)
        self.assertEqual(200, resp.status_code, resp.content)
        self.assertIn(
            'The two password fields didn’t match.',
            resp.content.decode('utf-8'),
        )

    def test_get_user(self):
        mixin = UserMixin()
        with self.assertRaises(Http404) as e:
            mixin.get_user('z' * 14)
        self.assertEqual(str(e.exception), 'No such invited user.')

    def test_opt_out(self):
        self.assertEqual(2, User.objects.count())

        user, sent = invite("foo@example.com", self.inviter)
        self.assertTrue(sent)
        self.assertEqual(1, len(mail.outbox))
        self.assertEqual(3, User.objects.count())

        url_parts = int_to_base36(user.id), token_generator.make_token(user)
        url = reverse('opt-out', args=url_parts)

        resp = self.client.get(url)
        self.assertEqual(200, resp.status_code, resp.status_code)

        resp = self.client.post(url, {})
        self.assertEqual(302, resp.status_code, resp.status_code)
        self.assertEqual(reverse('opt-out-done'),
                         urlparse(resp['Location']).path)
        self.assertEqual(2, User.objects.count())

        user, sent = invite("foo@example.com", self.inviter)
        self.assertFalse(sent)
        self.assertEqual(1, len(mail.outbox))
        self.assertEqual(1, OptOut.objects.count())
        self.assertTrue(OptOut.objects.is_blocked("foo@example.com"))
        self.assertIsNone(user)

        opt_out = OptOut.objects.get()
        opt_hash = OptOut.objects._hash_email('foo@example.com')
        self.assertEqual(opt_out.__unicode__(), opt_hash)

    def test_opt_out_done(self):
        resp = self.client.get(reverse('opt-out-done'))
        self.assertEqual(200, resp.status_code, resp.status_code)
