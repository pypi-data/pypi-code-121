import json
from datetime import datetime, timedelta

import jwt
from django.http.response import JsonResponse
from mock import Mock
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.test import APITestCase


class APITestCaseWrapper(APITestCase):
    default_response_headers = {'Content-Type': 'application/json'}

    def __init__(self, *args, **kwargs):
        super(APITestCaseWrapper, self).__init__(*args, **kwargs)

        def to_json(response):
            self.assertEqual(response['Content-Type'], 'application/json')
            response._json = getattr(response, '_json', None) or json.loads(response.content)
            return response._json

        Response.json = to_json
        JsonResponse.json = to_json

    def mocked_response(self, status_code, json_return_value=None, content=None, response_headers=None):
        response = Mock()

        response.status_code = status_code
        response.json.return_value = json_return_value
        response.content = content
        response.headers = response_headers or self.default_response_headers

        return response

    def generate_auth_header(self, **kwargs):
        token = self.jwt_encode(**kwargs)
        self.client.credentials(HTTP_AUTHORIZATION=token)

    @staticmethod
    def jwt_encode(jwt_secret='', algorithm='HS256', ttl=None, **kwargs):
        data = kwargs.copy()
        data['iat'] = datetime.utcnow()
        data['exp'] = datetime.utcnow() + (ttl or timedelta(minutes=10))
        return jwt.encode(data, jwt_secret, algorithm).decode('utf-8')

    def assertExists(self, cls, **kwargs):
        self.assertTrue(cls.objects.filter(**kwargs).exists(), '%s %s does not exist.' % (cls, kwargs))

    def assertDoesntExist(self, cls, **kwargs):
        self.assertFalse(cls.objects.filter(**kwargs).exists(), '%s %s exists, but expected not to.' % (cls, kwargs))

    @staticmethod
    def format_datetime(dt):
        return JSONRenderer().render(dt).strip('"')
