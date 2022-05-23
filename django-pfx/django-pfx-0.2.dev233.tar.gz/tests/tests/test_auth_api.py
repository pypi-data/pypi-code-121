import logging
import re
from datetime import datetime, timedelta
from http.cookies import SimpleCookie

from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core import mail
from django.test import TransactionTestCase, modify_settings, override_settings
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

import jwt

from pfx.pfxcore.test import APIClient, TestAssertMixin
from tests.models import User

logger = logging.getLogger(__name__)


class AuthAPITest(TestAssertMixin, TransactionTestCase):

    def setUp(self):
        self.client = APIClient(default_locale='en')
        self.cookie_client = APIClient(default_locale='en', with_cookie=True)
        self.user1 = User.objects.create_user(
            username='jrr.tolkien',
            email="jrr.tolkien@oxford.com",
            password='RIGHT PASSWORD',
            first_name='John Ronald Reuel',
            last_name='Tolkien',
        )

    def test_invalid_login(self):
        response = self.client.post(
            '/api/auth/login', {
                'username': 'jrr.tolkien',
                'password': 'WRONG PASSWORD'})
        self.assertRC(response, 401)

    def test_emtpy_login(self):
        response = self.client.post(
            '/api/auth/login', {})
        self.assertRC(response, 401)

    def test_valid_login(self):
        response = self.client.post(
            '/api/auth/login', {
                'username': 'jrr.tolkien',
                'password': 'RIGHT PASSWORD'})

        self.assertRC(response, 200)
        decoded = jwt.decode(
            response.json_content['token'], settings.PFX_SECRET_KEY,
            algorithms="HS256")
        self.assertEqual(decoded['pfx_user_pk'], self.user1.pk)

    def test_valid_login_with_cookie(self):
        response = self.client.post(
            '/api/auth/login?mode=cookie', {
                'username': 'jrr.tolkien',
                'password': 'RIGHT PASSWORD'})

        cookie = [v for k, v in response.client.cookies.items()
                  if k == 'token'][0]
        regex = r".*token=([\w\._-]*);.*"
        token = re.findall(regex, str(cookie))[0]

        self.assertRC(response, 200)
        decoded = jwt.decode(
            token, settings.PFX_SECRET_KEY,
            algorithms="HS256")
        self.assertEqual(decoded['pfx_user_pk'], self.user1.pk)

    def test_logout(self):
        self.client.login(
            username='jrr.tolkien',
            password='RIGHT PASSWORD')
        response = self.client.get('/api/auth/logout')
        self.assertRC(response, 200)
        cookie = [v for k, v in response.client.cookies.items()
                  if k == 'token'][0]
        regex = r".*token=([\"\"]*);.*"
        token = re.findall(regex, str(cookie))[0]
        self.assertEqual(token, '""')

    def test_valid_change_password(self):
        self.client.login(
            username='jrr.tolkien',
            password='RIGHT PASSWORD')
        response = self.client.post(
            '/api/auth/change-password', {
                'old_password': 'RIGHT PASSWORD',
                'new_password': 'NEW RIGHT PASSWORD'})
        self.assertRC(response, 200)

        self.cookie_client.login(
            username='jrr.tolkien',
            password='RIGHT PASSWORD')
        response = self.client.post(
            '/api/auth/change-password', {
                'old_password': 'NEW RIGHT PASSWORD',
                'new_password': 'RIGHT PASSWORD'})
        self.assertRC(response, 200)

    @override_settings(AUTH_PASSWORD_VALIDATORS=[{
        'NAME':
            'django.contrib.auth.password_validation.'
            'UserAttributeSimilarityValidator',
    }, {
        'NAME': 'django.contrib.auth.password_validation.'
                'MinimumLengthValidator',
    }])
    def test_change_password_validation(self):
        self.client.login(
            username='jrr.tolkien',
            password='RIGHT PASSWORD')
        response = self.client.post(
            '/api/auth/change-password', {
                'old_password': 'RIGHT PASSWORD',
                'new_password': 'jrr'})
        self.assertRC(response, 422)
        self.assertJE(response, 'new_password.@0',
                      "The password is too similar to the username.")
        self.assertJE(response, 'new_password.@1',
                      "This password is too short. "
                      "It must contain at least 8 characters.")
        response = self.client.post(
            '/api/auth/change-password', {
                'old_password': 'RIGHT PASSWORD',
                'new_password': '9ashff8za-@#asd'})
        self.assertRC(response, 200)

    def test_invalid_change_password(self):
        self.client.login(
            username='jrr.tolkien',
            password='RIGHT PASSWORD')

        # Wrong old password
        response = self.client.post(
            '/api/auth/change-password', {
                'old_password': 'WRONG PASSWORD',
                'new_password': 'NEVER APPLIED PASSWORD'})
        self.assertRC(response, 422)
        self.assertJE(response, "old_password.@0", "Incorrect password")

    def test_empty_change_password(self):
        self.client.login(
            username='jrr.tolkien',
            password='RIGHT PASSWORD')
        response = self.client.post(
            '/api/auth/change-password', {})
        self.assertRC(response, 422)
        self.assertJE(response, "old_password.@0", "Incorrect password")
        self.assertJE(
            response, "new_password.@0", "Empty password is not allowed")

        # No new password
        response = self.client.post(
            '/api/auth/change-password', {
                'old_password': 'RIGHT PASSWORD'})
        self.assertRC(response, 422)
        self.assertJE(
            response, "new_password.@0", "Empty password is not allowed")

        # Empty new password
        response = self.client.post(
            '/api/auth/change-password', {
                'old_password': 'RIGHT PASSWORD',
                'new_password': ''})
        self.assertRC(response, 422)
        self.assertJE(
            response, "new_password.@0", "Empty password is not allowed")

        # None new password
        response = self.client.post(
            '/api/auth/change-password', {
                'old_password': 'RIGHT PASSWORD',
                'new_password': None})
        self.assertRC(response, 422)
        self.assertJE(
            response, "new_password.@0", "Empty password is not allowed")

    @override_settings(PFX_TOKEN_VALIDITY={'minutes': 30})
    def test_valid_token_with_expiration(self):
        self.client.login(
            username='jrr.tolkien',
            password='RIGHT PASSWORD')
        response = self.client.get(
            '/api/books')
        self.assertRC(response, 200)

    @override_settings(PFX_TOKEN_VALIDITY={'minutes': 30})
    def test_valid_cookie_token_with_expiration(self):
        self.cookie_client.login(
            username='jrr.tolkien',
            password='RIGHT PASSWORD')

        regex = r".*expires=([^;]*);.*"
        expires = re.findall(regex, str(self.cookie_client.auth_cookie))[0]
        d = datetime.strptime(expires, '%a, %d %b %Y %H:%M:%S %Z')

        regex = r".*Max-Age=([^;]*);.*"
        max_age = re.findall(regex, str(self.cookie_client.auth_cookie))[0]

        # cookie expires in 30 minutes +/- 5 minutes.
        self.assertTrue(
            datetime.utcnow() + timedelta(minutes=25) <
            d < datetime.utcnow() + timedelta(minutes=35))
        self.assertEqual(int(max_age), 1800)

        response = self.cookie_client.get(
            '/api/books')
        self.assertRC(response, 200)

    @override_settings(
        PFX_TOKEN_VALIDITY={'minutes': 30}, PFX_COOKIE_DOMAIN='example.com')
    def test_valid_cookie_token_with_domain(self):
        self.cookie_client.login(
            username='jrr.tolkien',
            password='RIGHT PASSWORD')
        regex = r".*Domain=([^;]*);.*"
        domain = re.findall(regex, str(self.cookie_client.auth_cookie))[0]
        self.assertEqual('example.com', domain)
        response = self.cookie_client.get(
            '/api/books')
        self.assertRC(response, 200)

    @override_settings(PFX_TOKEN_VALIDITY={'minutes': -30})
    def test_expired_token(self):
        self.client.login(
            username='jrr.tolkien',
            password='RIGHT PASSWORD')

        response = self.client.get(
            '/api/books')
        self.assertRC(response, 401)

    @override_settings(PFX_TOKEN_VALIDITY={'minutes': -30})
    def test_expired_cookie_token(self):
        self.cookie_client.login(
            username='jrr.tolkien',
            password='RIGHT PASSWORD')

        regex = r".*expires=([^;]*);.*"
        expires = re.findall(regex, str(self.cookie_client.auth_cookie))[0]
        d = datetime.strptime(expires, '%a, %d %b %Y %H:%M:%S %Z')

        regex = r".*Max-Age=([^;]*);.*"
        max_age = re.findall(regex, str(self.cookie_client.auth_cookie))[0]

        # cookie expires now +/- 5 minutes.
        self.assertTrue(
            datetime.utcnow() - timedelta(minutes=5) <
            d < datetime.utcnow() + timedelta(minutes=5))
        self.assertEqual(int(max_age), 0)

        response = self.cookie_client.get(
            '/api/books')
        self.assertRC(response, 401)

    def test_invalid_auth_header(self):
        logging.disable(logging.CRITICAL)
        response = self.client.get(
            '/api/books',
            HTTP_AUTHORIZATION='Beer here',
            content_type='application/json')
        logging.disable(logging.NOTSET)
        self.assertRC(response, 401)

    def test_valid_token_with_invalid_user(self):
        user = User.objects.create_user(
            username='invisible.man',
            email="iv@invisible.com",
            password='RIGHT PASSWORD',
            first_name='Peter',
            last_name='Invisible',
        )
        self.client.login(
            username='invisible.man',
            password='RIGHT PASSWORD')
        user.delete()
        response = self.client.get(
            '/api/books')
        self.assertRC(response, 401)

    def test_valid_cookie_with_invalid_user(self):
        user = User.objects.create_user(
            username='invisible.man',
            email="iv@invisible.com",
            password='RIGHT PASSWORD',
            first_name='Peter',
            last_name='Invisible',
        )
        self.cookie_client.login(
            username='invisible.man',
            password='RIGHT PASSWORD')
        user.delete()
        response = self.cookie_client.get(
            '/api/books')
        self.assertRC(response, 401)

    def test_invalid_token(self):
        token = jwt.encode(
            {'pfx_user_pk': 1}, "A WRONG SECRET", algorithm="HS256")
        logging.disable(logging.CRITICAL)
        response = self.client.get(
            '/api/books',
            HTTP_AUTHORIZATION='Bearer ' + token,
            content_type='application/json')
        logging.disable(logging.NOTSET)
        self.assertRC(response, 401)

    def test_invalid_cookie_token(self):
        token = jwt.encode(
            {'pfx_user_pk': 1}, "A WRONG SECRET", algorithm="HS256")
        logging.disable(logging.CRITICAL)
        self.client.cookies = SimpleCookie({'token': token})
        response = self.client.get(
            '/api/books',
            content_type='application/json')
        logging.disable(logging.NOTSET)
        self.assertRC(response, 401)

    def test_signup(self):
        # Try to create with an existing username
        response = self.client.post(
            '/api/auth/signup', {
                'username': 'jrr.tolkien',
                'email': "jrr.tolkien@oxford.com",
                'first_name': 'John Ronald Reuel',
                'last_name': 'Tolkien',
            })

        self.assertRC(response, 422)
        self.assertEqual(response.json_content['username'],
                         ['A user with that username already exists.'])

        # Then create another valid user
        response = self.client.post(
            '/api/auth/signup', {
                'username': 'isaac.asimov',
                'email': 'isaac.asimov@bu.edu',
                'first_name': 'Isaac',
                'last_name': 'Asimov',
            })

        self.assertRC(response, 200)

        # Must send a welcome email
        self.assertEqual(
            mail.outbox[0].subject,
            f'Welcome on {settings.PFX_SITE_NAME}')

        self.client.logout()

        # Test that the token and uid are valid.
        regex = r"token=(.*)&uidb64=(.*)"
        token, uidb64 = re.findall(regex, mail.outbox[0].body)[0]
        response = self.client.post(
            '/api/auth/set-password', {
                'token': token,
                'uidb64': uidb64,
                'password': 'test'
            })
        self.assertRC(response, 200)
        self.assertJE(response, 'message', 'password updated successfully')

    def test_empty_signup(self):
        # Try empty signup
        response = self.client.post(
            '/api/auth/signup', {})
        self.assertRC(response, 422)
        self.assertJE(response, 'username.@0', 'This field cannot be blank.')

    def test_forgotten_password(self):
        # Try with an nonexistent email
        response = self.client.post(
            '/api/auth/forgotten-password', {
                'email': 'isaac.asimov@bu.edu',
            })

        self.assertRC(response, 200)
        self.assertJE(response, 'message',
                      'If the email address you entered is correct, '
                      'you will receive an email from us with '
                      'instructions to reset your password.')

        # Then try with a valid email
        response = self.client.post(
            '/api/auth/forgotten-password', {
                'email': 'jrr.tolkien@oxford.com',
            })

        self.assertRC(response, 200)
        self.assertJE(response, 'message',
                      'If the email address you entered is correct, '
                      'you will receive an email from us with '
                      'instructions to reset your password.')

        # Must send a reset password email
        self.assertEqual(
            mail.outbox[0].subject,
            f'Password reset on {settings.PFX_SITE_NAME}')

        self.client.logout()

        # Test that the token and uid are valid.
        regex = r"token=(.*)&uidb64=(.*)"
        token, uidb64 = re.findall(regex, mail.outbox[0].body)[0]
        response = self.client.post(
            '/api/auth/set-password', {
                'token': token,
                'uidb64': uidb64,
                'password': 'test'
            })
        self.assertRC(response, 200)
        self.assertJE(response, 'message', 'password updated successfully')

    def test_empty_forgotten_password(self):
        # Try with an nonexistent email
        response = self.client.post(
            '/api/auth/forgotten-password', {
            })
        self.assertRC(response, 200)
        self.assertJE(response, 'message',
                      'If the email address you entered is correct, '
                      'you will receive an email from us with '
                      'instructions to reset your password.')

    def test_set_password(self):
        # Try with a wrong token and uid
        response = self.client.post(
            '/api/auth/set-password', {
                'token': 'WRONG TOKEN',
                'uidb64': 'WRONG UID',
                'password': 'NEW PASSWORD',
            })

        self.assertRC(response, 401)

        # Then try with a valid token and uid
        token = default_token_generator.make_token(self.user1)
        uid = urlsafe_base64_encode(force_bytes(self.user1.pk))
        response = self.client.post(
            '/api/auth/set-password', {
                'token': token,
                'uidb64': uid,
                'password': 'NEW PASSWORD',
            })
        self.assertRC(response, 200)
        self.assertJE(response, 'message', "password updated successfully")

    @override_settings(AUTH_PASSWORD_VALIDATORS=[{
        'NAME':
            'django.contrib.auth.password_validation.'
            'UserAttributeSimilarityValidator',
    }, {
        'NAME': 'django.contrib.auth.password_validation.'
                'MinimumLengthValidator',
    }])
    def test_set_password_validation(self):
        token = default_token_generator.make_token(self.user1)
        uid = urlsafe_base64_encode(force_bytes(self.user1.pk))

        # Missing password
        response = self.client.post(
            '/api/auth/set-password', {
                'token': token,
                'uidb64': uid,
            })
        self.assertRC(response, 422)
        self.assertJE(
            response, "password.@0", "Empty password is not allowed")

        # Empty string password
        response = self.client.post(
            '/api/auth/set-password', {
                'token': token,
                'uidb64': uid,
                'password': ''
            })
        self.assertRC(response, 422)
        self.assertJE(
            response, "password.@0", "Empty password is not allowed")

        # None password
        response = self.client.post(
            '/api/auth/set-password', {
                'token': token,
                'uidb64': uid,
                'password': None
            })
        self.assertRC(response, 422)
        self.assertJE(
            response, "password.@0", "Empty password is not allowed")

        # Invalid password according to UserAttributeSimilarityValidator and
        # MinimumLengthValidator
        response = self.client.post(
            '/api/auth/set-password', {
                'token': token,
                'uidb64': uid,
                'password': 'jrr'
            })
        self.assertRC(response, 422)
        self.assertJE(response, 'password.@0',
                      "The password is too similar to the username.")
        self.assertJE(response, 'password.@1',
                      "This password is too short. "
                      "It must contain at least 8 characters.")

        # Finally, a valid password
        response = self.client.post(
            '/api/auth/set-password', {
                'token': token,
                'uidb64': uid,
                'password': '9ashff8za-@#asd'
            })
        self.assertRC(response, 200)

    def test_set_password_autologin_jwt(self):
        token = default_token_generator.make_token(self.user1)
        uid = urlsafe_base64_encode(force_bytes(self.user1.pk))
        response = self.client.post(
            '/api/auth/set-password', {
                'token': token,
                'uidb64': uid,
                'password': 'NEW PASSWORD',
                'autologin': 'jwt'
            })
        self.assertRC(response, 200)
        self.assertIn('token', response.json_content)
        token = response.json_content['token']
        decoded = jwt.decode(
            token, settings.PFX_SECRET_KEY,
            algorithms="HS256")
        self.assertEqual(decoded['pfx_user_pk'], self.user1.pk)

    def test_set_password_autologin_cookies(self):
        token = default_token_generator.make_token(self.user1)
        uid = urlsafe_base64_encode(force_bytes(self.user1.pk))
        response = self.client.post(
            '/api/auth/set-password', {
                'token': token,
                'uidb64': uid,
                'password': 'NEW PASSWORD',
                'autologin': 'cookie'
            })

        self.assertRC(response, 200)
        cookie = [v for k, v in response.client.cookies.items()
                  if k == 'token'][0]
        regex = r".*token=([\w\._-]*);.*"
        token = re.findall(regex, str(cookie))[0]

        self.assertRC(response, 200)
        decoded = jwt.decode(
            token, settings.PFX_SECRET_KEY,
            algorithms="HS256")
        self.assertEqual(decoded['pfx_user_pk'], self.user1.pk)

    def test_set_password_autologin_wrong_value(self):
        token = default_token_generator.make_token(self.user1)
        uid = urlsafe_base64_encode(force_bytes(self.user1.pk))
        response = self.client.post(
            '/api/auth/set-password', {
                'token': token,
                'uidb64': uid,
                'password': 'NEW PASSWORD',
                'autologin': 'qwertz'
            })
        self.assertRC(response, 200)
        self.assertJE(response, 'message', "password updated successfully")

    def test_token_anonymous(self):
        self.client.logout()
        response = self.client.get(
            '/api/books')
        self.assertRC(response, 200)

    @modify_settings(
        MIDDLEWARE={
            'remove': [
                'pfx.pfxcore.middleware.AuthenticationMiddleware']})
    def test_cookie_anonymous(self):
        self.cookie_client.logout()
        response = self.cookie_client.get(
            '/api/books')
        self.assertRC(response, 200)
