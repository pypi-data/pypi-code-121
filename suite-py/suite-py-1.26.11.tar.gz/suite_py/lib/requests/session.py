from requests_toolbelt.sessions import BaseUrlSession


class Session(BaseUrlSession):
    def request(self, method, url, *args, **kwargs):
        response = super().request(method, url, *args, **kwargs)

        response.raise_for_status()

        return response
