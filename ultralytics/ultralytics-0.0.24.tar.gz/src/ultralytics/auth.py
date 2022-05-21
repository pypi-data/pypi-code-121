import getpass
import json

import requests

from .config import HUB_API_ROOT
from .yolov5_utils.general import PREFIX, emojis


class Auth:
    secure_token = id_token = api_key = False

    def __init__(self):
        return

    def attempt_signin(self, attempts=1):
        tries = f"Attempt {str(attempts)} of 3" if attempts > 1 else ""
        print(f"{PREFIX}Login. {tries}")
        email = input(f"{PREFIX}Enter your account email address: ")
        password = getpass.getpass("Enter your account email password: ")
        self.signin_email(email, password)
        if self.id_token:
            return True

        attempts += 1
        print(f"{PREFIX}Incorrect Login Details.\n")
        if attempts <= 3:
            return self.attempt_signin(attempts)
        print(f"{PREFIX}Failed to authenticate. Exiting...")
        return False

    def signin_email(self, email, password):
        firebase_rest_url = "https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword"
        firebase_web_api_key = "AIzaSyDrFrqlV1sr3yK_-w8-cwrKGS9SLdEjW3U"

        payload = json.dumps({
            "email": email,
            "password": password,
            "returnSecureToken": True, })

        r = requests.post(firebase_rest_url, params={"key": firebase_web_api_key}, data=payload)

        if "error" in r.json():
            self.secure_token = False
            self.id_token = False
        else:
            self.secure_token = r.json()
            self.id_token = self.secure_token.get("idToken")

    def attempt_api_key(self, api_key='', attempts=1):
        if not api_key:
            s = f'. Attempt {attempts} of 3' if attempts > 1 else ' from https://hub.ultralytics.com/settings/api-keys'
            print(PREFIX, end='')
            api_key = getpass.getpass(f"Enter API key{s}: ")
        self.validate_api_key(api_key)
        if not self.api_key:
            attempts += 1
            print(emojis(f"{PREFIX}Invalid API key ⚠️\n"))

            if attempts <= 3:
                return self.attempt_api_key(attempts=attempts)
            print(emojis(f"{PREFIX}Failed to authenticate ❌"))
            return False
        else:
            print(emojis(f"{PREFIX}Authenticated ✅"))
            return True

    def validate_api_key(self, api_key):
        auth_endpoint = f"{HUB_API_ROOT}/authorise"

        payload = {"apiKey": api_key}

        r = requests.post(auth_endpoint, json=payload)

        self.secure_token = False
        self.id_token = False
        self.api_key = api_key if r.status_code == 200 else False

    def get_auth_string(self):
        if self.id_token:
            return {"idToken": self.id_token}
        elif self.api_key:
            return {"apiKey": self.api_key}
        else:
            return None
