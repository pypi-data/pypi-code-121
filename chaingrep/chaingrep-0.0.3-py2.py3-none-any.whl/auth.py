from requests.auth import AuthBase


class ChaingrepAuth(AuthBase):
    def __init__(self, api_key):
        self.api_key = api_key

    def __call__(self, request):
        request.headers.update({"Content-Type": "Application/JSON", "X-API-KEY": self.api_key})

        return request
