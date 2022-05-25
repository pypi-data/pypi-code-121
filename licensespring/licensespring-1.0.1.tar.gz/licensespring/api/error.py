from requests import HTTPError


class ClientError(HTTPError):
    def __init__(
        self,
        response,
    ):

        response_json = response.json()

        self.status = response_json.get("status")
        self.code = response_json.get("code")
        self.message = response_json.get("message")

        super(ClientError, self).__init__(self.message)

    def __str__(self):
        return self.message

    def __repr__(self):
        return "{}(status={}, code={}, message={})".format(
            self.__class__.__name__,
            self.status,
            self.code,
            self.message,
        )
