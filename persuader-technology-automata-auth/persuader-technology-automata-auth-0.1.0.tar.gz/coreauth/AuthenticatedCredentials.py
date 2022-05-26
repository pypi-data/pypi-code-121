import logging

from coreutility.collection.dictionary_utility import as_data

from coreauth.exception.AuthenticatorError import AuthenticatorError
from coreauth.repository.AuthRepository import AuthRepository


class AuthenticatedCredentials:

    def __init__(self, options):
        self.log = logging.getLogger(__name__)
        self.repository = AuthRepository(options)

    def obtain_auth_value(self, value):
        auth_info = self.repository.retrieve()
        if auth_info is None or len(auth_info) == 0:
            self.log.warning('AUTH_INFO not available')
            raise AuthenticatorError('AUTH_INFO not available')
        auth_value = as_data(auth_info, value)
        if auth_value is None or len(auth_value) == 0:
            self.log.warning(f'AUTH_INFO does not contain {value}')
            raise AuthenticatorError(f'AUTH_INFO does not contain {value}')
        return auth_value
