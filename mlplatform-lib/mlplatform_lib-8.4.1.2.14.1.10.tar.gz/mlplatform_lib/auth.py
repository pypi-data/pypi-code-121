import os
from mlplatform_lib.api_client import RunMode


class Auth:
    SECRET_LIST = ["projectId", "userId", "accessToken", "refreshToken", "authorizationType"]

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "instance"):
            cls.instance = super(Auth, cls).__new__(cls)
        return cls.instance

    def __init__(self, *args, **kwargs):
        api_client = kwargs.get("api_client")

        if api_client.run_mode == RunMode.LOCAL:
            self.secret_mount_path = None
            self.authorization = api_client.Authorization
            self.projectId = api_client.projectId
            self.userId = api_client.userId
            self.refreshToken = api_client.refreshToken
        else:
            self.secret_mount_path = os.environ["secretMountPath"]
            self.load_env(self.secret_mount_path)

    def load_env(self, secret_mount_path):
        file_list = [f for f in os.listdir(self.secret_mount_path)]
        for secret in self.SECRET_LIST:
            if secret not in file_list:
                print(f'Cannot found "{secret}" in secret path "{self.secret_mount_path}".')
                exit(1)

        for file in file_list:
            if file in self.SECRET_LIST:
                setattr(self, file, open(os.path.join(self.secret_mount_path, file), "r").read())
        self.authorization = self.accessToken
