import os

from django.conf import settings
from django.urls import reverse

from jwt import decode as jwt_decode, DecodeError, ExpiredSignatureError, get_unverified_header
from social_core.backends.azuread_b2c import AzureADB2COAuth2
from social_core.backends.azuread_tenant import AzureADTenantOAuth2
from social_core.exceptions import AuthTokenError


class UNICEFAzureADTenantOAuth2Ext(AzureADTenantOAuth2):
    name = 'unicef-azuread-tenant-oauth2'

    def user_data(self, access_token, *args, **kwargs):
        response = kwargs.get('response')
        id_token = response.get('id_token')

        # get key id and algorithm
        key_id = get_unverified_header(id_token)['kid']
        key = ''
        verify = os.environ.get('OAUTH2_VERIFY', False)
        try:
            # retrieve certificate for key_id
            if verify:
                certificate = self.get_certificate(key_id)
                key = certificate.public_key()

            options = {'verify_signature': verify}
            return jwt_decode(
                id_token,
                key=key,
                algorithms=['RS256'],
                audience=self.setting('KEY'),
                options=options,
            )
        except (DecodeError, ExpiredSignatureError) as error:
            raise AuthTokenError(self, error)


class UNICEFAzureADB2COAuth2(AzureADB2COAuth2):
    """UNICEF Azure ADB2C Custom Backend"""

    name = 'unicef-azuread-b2c-oauth2'
    BASE_URL = 'https://{tenant_name}.b2clogin.com/{tenant_id}'

    @property
    def base_url(self):
        return self.BASE_URL.format(tenant_name=self.tenant_name, tenant_id=self.tenant_id)

    @property
    def tenant_name(self):
        return self.setting('TENANT_NAME', 'unicef')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.redirect_uri = settings.HOST + reverse('social:complete', kwargs={'backend': 'unicef-azuread-b2c-oauth2'})
