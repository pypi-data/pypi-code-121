from google.cloud import secretmanager

from ssb_altinn3_util.clients.decorators.simple_exception_wrapper import exception_handler


class SecretManagerClient:
    def __init__(self, secret_path: str):
        self.secret_path = secret_path
        self.client = secretmanager.SecretManagerServiceClient()

    @exception_handler('Secret Client')
    def get_secret(self):
        encoded = self.client.access_secret_version(name=self.secret_path)
        return encoded.payload.data.decode('UTF-8')
