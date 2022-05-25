from coreauth.AuthenticatedCredentials import AuthenticatedCredentials
from coreauth.exception.UnableToAuthenticateError import UnableToAuthenticateError

AUTH_URL = 'AUTH_URL'


class Authenticator(AuthenticatedCredentials):

    def __init__(self, options):
        super().__init__(options)
        self.auth_url = options[AUTH_URL]

    async def authenticate(self):
        pass

    async def terminate(self):
        pass

    async def refresh(self):
        pass

    @staticmethod
    def should_update_url() -> bool:
        return False

    def update_url(self, url) -> str:
        self.log.warning('Update URL needs to be implemented')
        raise UnableToAuthenticateError('Update URL needs to be implemented')
