import json
import uuid
from urllib.parse import urlencode
from jwkest.jwk import KEYS

try:
    from django.urls import reverse
except ImportError:
    from django.core.urlresolvers import reverse
from django.test import RequestFactory
from django.core.management import call_command

from rest_framework.test import APITestCase, APIClient
from oidc_provider.views import TokenView, JwksView
from oidc_provider.lib.utils.token import create_code
from oidc_provider.tests.app.utils import create_fake_client, FAKE_NONCE, create_fake_dpop_proof

from djangoldp_account.models import LDPUser
from djangoldp_account.tests.models import OwnedResource


class AuthBackendTestCase(APITestCase):
    def setUp(self):
        call_command('creatersakey')
        self.client = APIClient()
        self.user = LDPUser.objects.create(email='{}@test.co.uk'.format(str(uuid.uuid4())), first_name='Test',
                                           last_name='Test', username=str(uuid.uuid4()))
        self.factory = RequestFactory()
        self.password = 'test'
        self.user.set_password(self.password)
        self.user.save()

    def setUpResource(self):
        self.resource = OwnedResource.objects.create(user=self.user)
        self.request_url = '/ownedresources/{}/'.format(self.resource.pk)

    def _post_login(self):
        data = {
            'username': self.user.username,
            'password': self.password
        }

        return self.client.post('/auth/login/', data=urlencode(data), content_type='application/x-www-form-urlencoded')

    def test_auth_login_username_password(self):
        response = self._post_login()
        self.assertEqual(response.status_code, 302)

    def _get_access_from_op(self, dpop_proof):
        '''gets a hold of an access token & id token'''

        def _get_code(user, client):
            code = create_code(
                user=user,
                client=client,
                scope=(['openid', 'email']),
                nonce=FAKE_NONCE,
                is_authentication=True)
            code.save()
            return code

        def _get_post_data(client, code):
            return  {
                'client_id': client.client_id,
                'client_secret': client.client_secret,
                'redirect_uri': client.default_redirect_uri,
                'grant_type': 'authorization_code',
                'code': code,
                'state': uuid.uuid4().hex,
            }

        url = reverse('oidc_provider:token')

        client = create_fake_client(response_type='code')
        code = _get_code(self.user, client)

        request = self.factory.post(
            url,
            data=urlencode(_get_post_data(client, code.code)),
            content_type='application/x-www-form-urlencoded',
            HTTP_DPOP=dpop_proof
        )

        return TokenView.as_view()(request)

    def _get_keys(self):
        """
        Get public key from discovery.
        """
        request = self.factory.get(reverse('oidc_provider:jwks'))
        response = JwksView.as_view()(request)
        jwks_dic = json.loads(response.content.decode('utf-8'))
        SIGKEYS = KEYS()
        SIGKEYS.load_dict(jwks_dic)
        return SIGKEYS

    def _get_dpop_headers(self, htu, htm):
        dpop_proof = create_fake_dpop_proof(htu=htu, htm=htm)
        op_auth = self._get_access_from_op(dpop_proof)

        SIGKEYS = self._get_keys()

        response_dic = json.loads(op_auth.content.decode('utf-8'))
        access_token = 'DPoP ' + response_dic['access_token']

        auth_headers = {
            'HTTP_AUTHORIZATION': access_token,
            'HTTP_DPOP': dpop_proof
        }

        return auth_headers

    # the test where all with the request is as it should be
    def test_auth_login_dpop_token(self):
        # confirm that this is a request which requires my authorization
        self.setUpResource()

        request = self.factory.get(self.request_url)
        response = self.client.get(self.request_url)
        self.assertEqual(response.status_code, 403)

        # get DPoP authorization headers
        headers = self._get_dpop_headers(htu=request.build_absolute_uri(), htm=request.method)

        # make a request that requires my authorization
        response = self.client.get(self.request_url, **headers)
        self.assertEqual(response.status_code, 200)

    def test_missing_dpop_proof(self):
        # confirm that this is a request which requires my authorization
        self.setUpResource()

        request = self.factory.get(self.request_url)
        response = self.client.get(self.request_url)
        self.assertEqual(response.status_code, 403)

        # get DPoP authorization headers
        headers = self._get_dpop_headers(htu=request.build_absolute_uri(), htm=request.method)
        # NO DPoP proof
        headers.pop('HTTP_DPOP')

        # make a request that requires my authorization
        response = self.client.get(self.request_url, **headers)
        self.assertEqual(response.status_code, 401)

    # testing the HTU/HTM claims in the DPoP header

    def test_invalid_htu_claim_url_mismatch(self):
        self.setUpResource()

        # get DPoP authorization headers
        request = self.factory.get(self.request_url)
        headers = self._get_dpop_headers(htu=None, htm=request.method)

        response = self.client.get(self.request_url, **headers)
        self.assertEqual(response.status_code, 401)

    def test_invalid_htu_claim_invalid_url(self):
        self.setUpResource()

        # get DPoP authorization headers - HTU isnt a valid url
        request = self.factory.get(self.request_url)
        headers = self._get_dpop_headers(htu='not a url', htm=request.method)

        response = self.client.get(self.request_url, **headers)
        self.assertEqual(response.status_code, 401)

    def test_invalid_htu_claim_error_url(self):
        self.setUpResource()

        # get DPoP authorization headers - HTU is an integer
        request = self.factory.get(self.request_url)
        headers = self._get_dpop_headers(htu=100, htm=request.method)

        response = self.client.get(self.request_url, **headers)
        self.assertEqual(response.status_code, 401)

    def test_invalid_htm_claim_none(self):
        self.setUpResource()

        # get DPoP authorization headers - HTM is None
        request = self.factory.get(self.request_url)
        headers = self._get_dpop_headers(htu=request.build_absolute_uri(), htm=None)

        response = self.client.get(self.request_url, **headers)
        self.assertEqual(response.status_code, 401)

    # if I claim authorization then it should be rejected regardless of the view's permissions
    def test_invalid_auth_rejects_on_unauthenticated_view(self):
        self.setUpResource()

        # get DPoP authorization headers - HTM is None
        request = self.factory.get('/users/')
        headers = self._get_dpop_headers(htu=request.build_absolute_uri(), htm=None)

        response = self.client.get('/users/', **headers)
        self.assertEqual(response.status_code, 401)

    # TODO (optional)
    #  The RS can optionally keep track of all DPoP jti claims it received. Because a new DPoP token must be generated
    #  each time a request is made, no two tokens should have the same jti. If the RS receives a DPoP token with a jti
    #  it has already encountered it may reject the request with a 403.
