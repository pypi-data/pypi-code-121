from requests import Response

from .exceptions import AuthorizationError

API_ENDPOINT = "https://discord.com/api"
API_VERSION = 9
API_URL = f"{API_ENDPOINT}/v{API_VERSION}"


class ResponseChecker():

    def __init__(self, res: Response):
        self.res = res

    def check(self):

        if self.res.status_code >= 500 and self.res.status_code < 600:
            return self.server()

        elif self.res.status_code >= 400 and self.res.status_code < 500:
            return self.client()

        elif self.res.status_code >= 300 and self.res.status_code < 400:
            return self.redirect()

        elif self.res.status_code >= 200 and self.res.status_code < 300:
            return self.success()

        elif self.res.status_code >= 100 and self.res.status_code < 200:
            return self.info()

    def info(self):
        pass

    def success(self):
        pass

    def client(self):

        res = self.res

        if res.status_code == 401:
            raise AuthorizationError("Provided token isn't valid")

    def server(self):
        pass

    def redirect(self):
        pass
