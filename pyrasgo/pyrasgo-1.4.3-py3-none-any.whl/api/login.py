import requests

from pyrasgo.schemas.user import UserLogin
from .error import APIError
from .session import Environment


class Login:
    def login(self, payload: UserLogin):
        url = self._url(resource="/pyrasgo-login", api_version=1)
        response = requests.post(url, json=payload.__dict__)
        status_code = response.status_code
        if status_code == 200:
            return response.json()
        if status_code == 401 or status_code == 403:
            raise APIError(
                "Username or password are incorrect. Please check your credentials "
                "or use pyrasgo.register() to create a new account."
            )
        elif status_code == 400:
            raise APIError("Credentials Expired. Contact Rasgo Support.")

    def _url(self, resource, api_version=None):
        env = Environment.from_environment()
        if '/' == resource[0]:
            resource = resource[1:]
        protocol = 'http' if env.value == 'localhost' else 'https'
        return f"{protocol}://{env.value}/{'' if api_version is None else f'v{api_version}/'}{resource}"
