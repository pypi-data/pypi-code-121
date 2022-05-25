import requests as req
from .iam import IAM
from ..env import Environment
from typing import TypeVar, Dict

T = TypeVar('T')


class Configs:
    def __init__(self, env: Environment):
        iam = IAM(env)
        configs_protocol = env.get("CONFIGS_PROTOCOL", default="https")
        configs_host = env.get("CONFIGS_HOST", default="configs.avd.al")

        self.role_uri = f"{configs_protocol}://{configs_host}/api/v1/roles/{{}}/configs"
        self.token = iam.access_token()

    def load_role(self, name) -> Dict[str, T]:
        res = req.get(self.role_uri.format(name), headers={
            "Authorization": f"Bearer {self.token}",
        })

        if not res.ok:
            raise Exception(res.json())

        return res.json()
