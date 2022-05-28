from base64 import urlsafe_b64encode
from datetime import datetime, timedelta
from functools import cache
from hashlib import sha256
from os.path import exists
from sys import stderr
from time import gmtime, localtime, mktime
from typing import Optional
from urllib.parse import urlencode, urlparse, parse_qs
from uuid import uuid4
import json
import logging
import random

# from bs4 import BeautifulSoup
import requests

from splatnet import __version__

_NINTENDO_SWITCH_ONLINE_CLIENT_ID = "71b963c1b7b6d119"
_NINTENDO_SWITCH_ONLINE_APP_ID = "com.nintendo.znca"

log = logging.getLogger("splatnet.splatnet2")


@cache
def app_version() -> str:
    return "2.1.1"
    # JavaScript is needed to get app version from Play store at present.
    #
    # response = requests.get(
    #     "https://play.google.com/store/apps/details?id=com.nintendo.znca&hl=en"
    # )
    # soup = BeautifulSoup(response.text, "html.parser")
    # return soup.find("div", text="Current Version").next_sibling.text


@cache
def user_agent_for_nintendo_account():
    return f"OnlineLounge/{app_version()} NASDKAPI Android"


class NintendoAuthorizer:
    _CHARS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

    _code_verifier: str

    def __init__(self):
        self._code_verifier = self._random_string(128)

    def authorize(self) -> str:
        print(f"Navigate to this URL: {self._authorize_uri()}", file=stderr)
        print(
            "Copy the URL of 'Select this account' button, and past it: ",
            file=stderr,
            end="",
        )
        redirect_url = input()
        parse_result = urlparse(redirect_url)
        query = parse_qs(parse_result.fragment)
        session_token_code = query["session_token_code"][0]
        return self._get_session_token(session_token_code)

    def _random_string(self, length) -> str:
        return "".join(random.choices(self._CHARS, k=length))

    def _code_challenge(self) -> str:
        m = sha256()
        m.update(self._code_verifier.encode("ascii"))
        return urlsafe_b64encode(m.digest()).replace(b"=", b"")

    def _authorize_uri(self) -> str:
        params = {
            "state": self._random_string(50),
            "redirect_uri": "npf71b963c1b7b6d119://auth",
            "client_id": _NINTENDO_SWITCH_ONLINE_CLIENT_ID,
            "scope": "openid user user.birthday user.mii user.screenName",
            "response_type": "session_token_code",
            "session_token_code_challenge": self._code_challenge(),
            "session_token_code_challenge_method": "S256",
            "theme": "login_form",
        }

        encoded_params = urlencode(params)
        return f"https://accounts.nintendo.com/connect/1.0.0/authorize?{encoded_params}"

    def _get_session_token(
        self,
        session_token_code: str,
    ) -> str:
        url = "https://accounts.nintendo.com/connect/1.0.0/api/session_token"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": user_agent_for_nintendo_account(),
        }
        data = {
            "client_id": _NINTENDO_SWITCH_ONLINE_CLIENT_ID,
            "session_token_code": session_token_code,
            "session_token_code_verifier": self._code_verifier,
        }

        log.debug("_get_session_token request: headers=%s, data=%s", headers, data)

        response = requests.post(url, headers=headers, data=data)

        log.debug(
            "_get_session_token response: status=%s, headers=%s, body=%s",
            response.status_code,
            response.headers,
            response.text,
        )

        return json.loads(response.text)["session_token"]


class IksmSessionGetter:
    session_token: str
    _guid: str
    _timestamp: str
    _access_token: Optional[str]
    _id_token: Optional[str]
    _language: Optional[str]
    _country: Optional[str]
    _birthday: Optional[str]
    _api_token: Optional[str]
    _web_service_token: Optional[str]
    _iksm_session: Optional[str]

    def __init__(self, session_token: str):
        self.session_token = session_token
        self._guid = str(uuid4())
        self._timestamp = str(int(datetime.now().timestamp()))

    def get(self) -> str:
        self._get_api_tokens()
        self._get_user_info()
        self._login_api()
        self._get_web_service_token()
        self._get_iksm_session()
        return self._iksm_session

    def _get_api_tokens(self):
        headers = {
            "Accept": "application/json",
            "User-Agent": user_agent_for_nintendo_account(),
        }
        data = {
            "client_id": _NINTENDO_SWITCH_ONLINE_CLIENT_ID,
            "session_token": self.session_token,
            "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer-session-token",
        }

        response = requests.post(
            "https://accounts.nintendo.com/connect/1.0.0/api/token",
            headers=headers,
            json=data,
        )

        self._access_token = response.json()["access_token"]
        self._id_token = response.json()["id_token"]

    def _get_user_info(self):
        headers = {
            "Accept": "application/json",
            "User-Agent": user_agent_for_nintendo_account(),
            "Authorization": f"Bearer {self._access_token}",
        }

        response = requests.get(
            "https://api.accounts.nintendo.com/2.0.0/users/me", headers=headers
        )

        self._language = response.json()["language"]
        self._country = response.json()["country"]
        self._birthday = response.json()["birthday"]

    def _get_s2_hash(self, token: str) -> str:
        headers = {"User-Agent": f"splatnet.py/{__version__}"}
        data = {"naIdToken": token, "timestamp": self._timestamp}
        response = requests.post(
            "https://elifessler.com/s2s/api/gen2", headers=headers, data=data
        )
        log.debug(
            "_get_s2_hash response: status=%s, headers=%s, body=%s",
            response.status_code,
            response.headers,
            response.text,
        )
        return json.loads(response.text)["hash"]

    def _get_f_token(self, token: str, iid: str) -> str:
        headers = {
            "x-token": token,
            "x-time": self._timestamp,
            "x-guid": self._guid,
            "x-hash": self._get_s2_hash(token),
            "x-ver": "3",
            "x-iid": iid,
        }

        response = requests.get(
            "https://flapg.com/ika2/api/login?public", headers=headers
        )
        return json.loads(response.text)["result"]

    def _api_headers(self, token: Optional[str] = None) -> dict:
        return {
            "Accept": "application/json",
            "Authorization": f"Bearer {token}",
            "Host": "api-lp1.znc.srv.nintendo.net",
            "User-Agent": f"{_NINTENDO_SWITCH_ONLINE_APP_ID}/{app_version()} (Android 7.1.2)",
            "X-Platform": "Android",
            "X-ProductVersion": app_version(),
        }

    def _login_api(self):
        f = self._get_f_token(self._access_token, "nso")
        data = {
            "parameter": {
                "f": f["f"],
                "naIdToken": f["p1"],
                "timestamp": f["p2"],
                "requestId": f["p3"],
                "naCountry": self._country,
                "naBirthday": self._birthday,
                "language": self._language,
            }
        }

        response = requests.post(
            "https://api-lp1.znc.srv.nintendo.net/v1/Account/Login",
            headers=self._api_headers(),
            json=data,
        )

        log.debug(
            "_login_api response: status=%s, headers=%s, body=%s",
            response.status_code,
            response.headers,
            response.text,
        )

        self._api_token = response.json()["result"]["webApiServerCredential"][
            "accessToken"
        ]

    def _get_web_service_token(self):
        f = self._get_f_token(self._api_token, "app")
        data = {
            "parameter": {
                "id": "5741031244955648",
                "f": f["f"],
                "registrationToken": f["p1"],
                "timestamp": f["p2"],
                "requestId": f["p3"],
            }
        }

        response = requests.post(
            "https://api-lp1.znc.srv.nintendo.net/v2/Game/GetWebServiceToken",
            headers=self._api_headers(self._api_token),
            json=data,
        )

        self._web_service_token = response.json()["result"]["accessToken"]

    def _get_iksm_session(self):
        headers = {
            "X-IsAppAnalyticsOptedIn": "false",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "X-GameWebToken": self._web_service_token,
            "X-Requested-With": "com.nintendo.znca",
        }
        response = requests.get(
            "https://app.splatoon2.nintendo.net/?lang=en-US", headers=headers
        )
        self._iksm_session = response.cookies["iksm_session"]


class Config:
    path: str
    _session_token: Optional[str]
    _iksm_session: Optional[str]
    _session_expires: Optional[datetime]
    _language: str
    _timezone_offset: int

    def __init__(self, path: str = "./config.json", language: Optional[str] = None):
        self.path = path
        self._session_token = None
        self._iksm_session = None
        self._session_expires = None
        self._language = "en-US"
        self._timezone_offset = self._calculate_timezone_offset()

        self._load(path)

        if language is not None:
            self.set_language(language)

    def iksm_session(self) -> str:
        if self.iksm_session is None or self._is_expired():
            self._get_iksm_session()

        return self._iksm_session

    def language(self) -> str:
        return self._language

    def timezone_offset(self) -> str:
        return str(self._timezone_offset)

    def set_language(self, language) -> None:
        self.language = language
        self._store()

    def _is_expired(self) -> bool:
        if self._session_expires is None:
            return True

        return self._session_expires < datetime.now()

    def _get_session_token(self) -> None:
        self._session_token = NintendoAuthorizer().authorize()

    def _get_iksm_session(self) -> None:
        if self._session_token is None:
            self._get_session_token()

        self._iksm_session = IksmSessionGetter(self._session_token).get()
        self._session_expires = datetime.now() + timedelta(hours=1)
        self._store()

    def _calculate_timezone_offset(self) -> int:
        int((mktime(gmtime()) - mktime(localtime())) / 60)

    def _load(self, path: Optional[str]) -> None:
        if path is None or not exists(path):
            return

        with open(path) as f:
            config_json: dict = json.loads(f.read())
            self._session_token = config_json.get("session_token", None)
            self._iksm_session = config_json.get("iksm_session", None)
            if "session_expires" in config_json:
                self._session_expires = datetime.fromisoformat(
                    config_json["session_expires"]
                )
            if "language" in config_json:
                self._language = config_json["language"]

            if "timezone_offset" in config_json:
                self._timezone_offset = config_json["timezone_offset"]

    def _store(self):
        with open(self.path, "w") as f:
            f.write(json.dumps(self.data()))

    def data(self):
        data = {
            "session_token": self._session_token,
            "iksm_session": self._iksm_session,
            "language": self._language,
            "timezone_offset": self._timezone_offset,
        }

        if self._session_expires is not None:
            data["session_expires"] = self._session_expires.isoformat()

        return data

    def __repr__(self):
        return (
            f"<splatnet.splatnet2.config.Config path='{self.path}' data={self.data()}>"
        )


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    config = Config()
    print(config.iksm_session())
