import json
import requests

from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.core.exceptions import ValidationError
from rest_framework.exceptions import AuthenticationFailed
from rest_framework import status
from django.core.validators import validate_email
from django.conf import settings
from jwkest import BadSyntax
from jwkest.jwt import JWT
from jwt.utils import (base64url_decode, base64url_encode)
from oidc_provider.lib.utils.dpop import verify_signature, verify_dpop_proof, verify_thumbprint
from oidc_provider.lib.errors import TokenError
from oidc_provider.views import JwksView

from djangoldp_account.auth.solid import Solid
from djangoldp_account.errors import LDPLoginError

UserModel = get_user_model()


class EmailOrUsernameAuthBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            validate_email(username)
            user = UserModel.objects.get(email=username)
            if user.check_password(password):
                return user
        except (ValidationError, UserModel.DoesNotExist):
            return super().authenticate(request, username, password, **kwargs)


class ExternalUserBackend(ModelBackend):
    def _get_or_create_then_authenticate(self, userinfo, webid):
        user = Solid.get_or_create_user(userinfo, webid)

        if self.user_can_authenticate(user):
            return user

    def validate_bearer_token(self, token):
        _jwt = JWT()
        try:
            unpacked = json.loads(_jwt.unpack(token).part[1])
        except BadSyntax:
            return
        try:
            id_token = json.loads(_jwt.unpack(unpacked['id_token']).part[1])
        except KeyError:
            id_token = unpacked
        try:
            Solid.check_id_token_exp(id_token['exp'])
            Solid.confirm_webid(id_token['sub'], id_token['iss'])
        except LDPLoginError as e:
            raise AuthenticationFailed(detail=e.description, code=status.HTTP_401_UNAUTHORIZED)

        userinfo = {
            'sub': id_token['sub']
        }

        return self._get_or_create_then_authenticate(userinfo, userinfo['sub'])

    def validate_dpop_access_token_claims(self, access_token):
        # check expiry
        Solid.check_id_token_exp(access_token['exp'])

        # check issuer has authority
        Solid.confirm_webid(access_token['webid'], access_token['iss'])

        # check audience
        Solid.check_aud_claim(access_token)

    def validate_dpop_proof_claims(self, request, dpop_claims):
        # if the htu does not match the protocol, origin and path of the request reject request
        Solid.check_htu_claim(request, dpop_claims)

        # if the htm does not correspond to the http method of the request then reject it
        Solid.check_htm_claim(request, dpop_claims)

        # TODO: (Optional) Checks DPoP token unique identifier (jti)

    def verify_access_token_signature(self, token_raw, token_claims):
        def retrieve_op_keys():
            try:
                # this server is also the OIDC provider
                # TODO: tight coupling with django-webidoidc-provider
                if token_claims['iss'] == settings.SITE_URL:
                    keys = JwksView().get_all_keys()
                # the OIDC provider is remote
                else:
                    config = requests.get(token_claims['iss'] + '/.well-known/openid-configuration').json()
                    keys = requests.get(config['jwks_uri']).json()

                return keys

            except (requests.ConnectionError, requests.Timeout):
                raise LDPLoginError('unable to connect to open-id provider')

        def find_key(keys):
            try:
                # extract token key from header
                body = token_raw.split('.')[0]
                header = json.loads(base64url_decode(body))

                return [key for key in keys['keys'] if key['kid'] == header['kid']][0]

            except IndexError:
                raise LDPLoginError('access token key not matching OP')

        # retrieve OP's public keys and find the access token key with this
        keys = retrieve_op_keys()
        jwk = find_key(keys)

        try:
            verify_signature(jwk, token_raw, token_claims['aud'])
        except TokenError:
            raise LDPLoginError('access token signature invalid')

    def validate_dpop_token(self, request, token):
        # the RS first checks that the DPoP token was signed by the public key from the header jwk
        dpop_proof = request.headers.get('dpop')
        if dpop_proof is None:
            raise AuthenticationFailed(detail='DPoP proof missing', code=status.HTTP_401_UNAUTHORIZED)
        try:
            jwk = verify_dpop_proof(dpop_proof)
        except TokenError:
            raise AuthenticationFailed(detail='DPoP proof invalid', code=status.HTTP_401_UNAUTHORIZED)

        # DPoP proof signature confirmed. Extract the DPoP header claims
        body = dpop_proof.split('.')[1]
        dpop_claims = json.loads(base64url_decode(body))

        # extract the access token body
        body = token.split('.')[1]
        jwt = json.loads(base64url_decode(body))

        try:
            # The RS checks if the public key in the DPoP header corresponds to the thumbprint in the access token
            verify_thumbprint(jwk, jwt['cnf']['jkt'])
        except KeyError:
            raise AuthenticationFailed(detail='missing thumbprint claim', code=status.HTTP_401_UNAUTHORIZED)

        try:
            # verify claims
            self.validate_dpop_proof_claims(request, dpop_claims)
            self.validate_dpop_access_token_claims(jwt)

            # finally, verify the access token signature
            self.verify_access_token_signature(token, jwt)

        except (LDPLoginError, KeyError) as e:
            print('error validating claims ' + str(e))
            raise AuthenticationFailed(detail='unable to validate claims', code=status.HTTP_401_UNAUTHORIZED)

        # validation complete, we can complete the authentication
        return self._get_or_create_then_authenticate({}, jwt['webid'])

    def authenticate(self, request, username=None, password=None, **kwargs):
        if 'HTTP_AUTHORIZATION' in request.META:
            jwt = request.META['HTTP_AUTHORIZATION']
            if jwt.lower().startswith("dpop"):
                jwt = jwt[5:]
                return self.validate_dpop_token(request, jwt)

            elif jwt.lower().startswith("bearer"):
                jwt = jwt[7:]

            # make an attempt assuming Bearer token if not recognised or not specified
            return self.validate_bearer_token(jwt)
