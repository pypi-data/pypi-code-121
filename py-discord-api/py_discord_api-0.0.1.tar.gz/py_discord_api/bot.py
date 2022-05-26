from requests import Response, Request, request as make_request

from .http import API_URL, ResponseChecker
from .exceptions import AuthorizationError
from .message import DirectMessage, GuildMessage, Message

class Bot():

    def __init__(self, token: str):
        self.token = token

        self.info_json: dict = self.request("get", "users/@me").json()

        self.id = self.info_json.get("id")
        self.username = self.info_json.get("username")
        self.dicriminator = self.info_json.get("dicriminator")
        self.avatar_hash = self.info_json.get("avatar")
        self.avatar_url = f"https://cdn.discordapp.com/avatars/{self.id}/{self.avatar_hash}.webp"

    def request(self, method: str, path: str, headers: dict = None, payload: dict = None):

        url = f"{API_URL}/{path}"
        auth_header = {"Authorization": f"Bot {self.token}"}

        if payload is None:
            payload = {}

        if headers is None:
            headers = {} | auth_header

        res: Response = make_request(
            method=method,
            url=url,
            headers=headers,
            data=payload
        )

        ResponseChecker(res).check()

        return res

    def send_message(self, message: Message):
        self.request("post", "/")