import json
import logging
import re
from functools import reduce
from http.cookies import SimpleCookie

from django.db import transaction
from django.test.client import Client as DjangoClient

logger = logging.getLogger(__name__)


def format_response(r, title="http response"):
    res = []
    res.append(f"\n******************** {title} ********************")
    if not r:
        res.append("Response is null")
    res.append(f"Status : {r.status_code} {r.reason_phrase}")
    res.append("Headers : ")
    res.append("\n".join(f"  {k}: {v}" for k, v in r.headers.items()))
    res.append("Content : ")
    if hasattr(r, 'json_content'):
        res.append(json.dumps(r.json_content, indent=4, sort_keys=True))
    elif hasattr(r, 'content') and r.content:
        res.append(r.content)
    elif hasattr(r, 'streaming_content'):
        res.append("Streaming content")
    else:
        res.append("Response is empty")
    res.append("*******************************************************")
    return '\n'.join(res)


class APIClient(DjangoClient):

    token = None
    default_locale = None
    auth_cookie = None

    def __init__(self, enforce_csrf_checks=False, raise_request_exception=True,
                 default_locale=None, with_cookie=False, **defaults):
        super().__init__(enforce_csrf_checks, raise_request_exception,
                         **defaults)
        self.default_locale = default_locale
        self.with_cookie = with_cookie

    def login(self, username, password='test',
              path='/api/auth/login', locale=None):
        self.token = None
        response = self.post(
            f"{path}{self.with_cookie and '?mode=cookie' or ''}", {
                'username': username,
                'password': password}, locale=locale)
        if response.status_code == 200:
            if self.with_cookie:
                self.auth_cookie = [
                    v for k, v in response.client.cookies.items()
                    if k == 'token'][0]
                regex = r".*token=([\w\._-]*);.*"
                self.token = re.findall(regex, str(self.auth_cookie))[0]
            else:
                self.token = response.json_content['token']
            return True
        return False

    def logout(self):
        self.token = None

    def generic(self, method, path, data='',
                content_type='application/octet-stream', secure=False,
                **extra):
        if self.token:
            if self.with_cookie:
                self.cookies = SimpleCookie(
                    {'token': self.token})
            else:
                extra.update(HTTP_AUTHORIZATION=f"Bearer {self.token}")
        return super().generic(
            method, path, data, content_type, secure, **extra)

    def update_locale(self, locale, extra):
        nextra = dict(extra)
        if locale:
            nextra.update(HTTP_X_CUSTOM_LANGUAGE=f"{locale}")
        elif self.default_locale:
            nextra.update(HTTP_X_CUSTOM_LANGUAGE=f"{self.default_locale}")
        return nextra

    @staticmethod
    def decode_response(response):
        if response.headers['Content-Type'] == 'application/json':
            response.json_content = response.json()
        response.formatted = lambda: format_response(response)
        response.print = lambda: print(format_response(response))
        return response

    def get(self, path, data=None, secure=False, locale=None, **extra):
        extra = self.update_locale(locale, extra)
        return self.decode_response(super().get(path, data, secure, **extra))

    def post(self, path, data=None, content_type='application/json',
             secure=False, locale=None, **extra):
        extra = self.update_locale(locale, extra)
        return self.decode_response(
            super().post(path, data, content_type, secure, **extra))

    def head(self, path, data=None, secure=False, locale=None, **extra):
        extra = self.update_locale(locale, extra)
        return self.decode_response(
            super().head(path, data, secure, **extra))

    def trace(self, path, secure=False, locale=None, **extra):
        extra = self.update_locale(locale, extra)
        return self.decode_response(super().trace(path, secure, **extra))

    def options(self, path, data='', content_type='application/json',
                secure=False, locale=None, **extra):
        extra = self.update_locale(locale, extra)
        return self.decode_response(
            super().options(path, data, content_type, secure, **extra))

    def put(self, path, data='', content_type='application/json',
            secure=False, locale=None, **extra):
        extra = self.update_locale(locale, extra)
        return self.decode_response(
            super().put(path, data, content_type, secure, **extra))

    def patch(self, path, data='', content_type='application/json',
              secure=False, locale=None, **extra):
        extra = self.update_locale(locale, extra)
        return self.decode_response(
            super().patch(path, data, content_type, secure, **extra))

    def delete(self, path, data='', content_type='application/json',
               secure=False, locale=None, **extra):
        extra = self.update_locale(locale, extra)
        return self.decode_response(
            super().delete(path, data, content_type, secure, **extra))


class TestAssertMixin:

    # assert response status code
    def assertRC(self, response, code, msg=None):
        msg = '\n'.join([msg or '', response.formatted()])
        return self.assertEqual(response.status_code, code, msg=msg)

    def get_val(self, response, key):
        def _p(k):
            return int(k[1:]) if k[0] == '@' else k
        try:
            return reduce(lambda c, k: c[_p(k)], key.split("."),
                          response.json_content)
        except IndexError:
            print(format_response(response, f'Index Error for key "{key}"'))
            raise Exception(f'Index Error for key "{key}"')
        except KeyError:
            print(format_response(response, f'Key Error for key "{key}"'))
            raise Exception(f'Key Error for key "{key}"')

    # assert JSON content at key equals value
    def assertJE(self, response, key, value, msg=None):
        msg = '\n'.join([msg or '', response.formatted()])
        return self.assertEqual(self.get_val(response, key), value, msg=msg)

    # assert JSON content at key not equals value
    def assertNJE(self, response, key, value, msg=None):
        msg = '\n'.join([msg or '', response.formatted()])
        return self.assertNotEqual(
            self.get_val(response, key), value, msg=msg)

    # assert JSON content at key exists
    def assertJEExists(self, response, key, msg=None):
        msg = '\n'.join([msg or '', response.formatted()])
        path, name = key.rsplit('.', 1)
        return self.assertIn(name, self.get_val(response, path), msg=msg)

    # assert JSON content at key not exists
    def assertJENotExists(self, response, key, msg=None):
        msg = '\n'.join([msg or '', response.formatted()])
        path, name = key.rsplit('.', 1)
        return self.assertNotIn(name, self.get_val(response, path), msg=msg)

    # assert JSON array size
    def assertSize(self, response, key, size, msg=None):
        msg = '\n'.join([msg or '', response.formatted()])
        return self.assertEqual(
            len(self.get_val(response, key)), size, msg=msg)

    # assert JSON array contains
    def assertJIn(self, response, key, element, msg=None):
        msg = '\n'.join([msg or '', response.formatted()])
        return self.assertIn(
            element, self.get_val(response, key), msg=msg)


class TestPermsAssertMixin(TestAssertMixin):
    USER_TESTS = {}

    def assertPerms(self, **methods):
        for method, result in methods.items():
            test = None
            if '__' in method:
                method, test = method.split('__')
            with transaction.atomic():
                sid = transaction.savepoint()
                with self.subTest(msg=method):
                    response = getattr(self, method)()
                    msg = (
                        hasattr(self, '_logged_user') and
                        f"User {self._logged_user}" or None)
                    if test == 'count':
                        self.assertJE(response, 'meta.count', result, msg)
                        self.assertSize(response, 'items', result, msg)
                    else:
                        self.assertRC(response, result, msg)
                transaction.savepoint_rollback(sid)

    def test_all_users(self):
        for user, perms in self.USER_TESTS.items():
            self.client.login(username=user)
            self._logged_user = user
            self.assertPerms(**perms)


class MockBoto3Client:
    def generate_presigned_url(self, *args, **kwargs):
        params = kwargs.get('Params', {})
        return f"http://{params.get('Bucket')}/{params.get('Key')}"

    def head_object(self, *args, **kwargs):
        return dict(ContentLength=1000, ContentType="image/png")

    def delete_object(self, *args, **kwargs):
        pass
