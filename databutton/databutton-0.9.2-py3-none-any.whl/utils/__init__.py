import json
import logging
import os
from dataclasses import dataclass, field
from pathlib import Path
from time import time
from typing import List, Optional, Union

import requests
import schedule

try:
    from urllib.parse import quote
except Exception:
    from urllib import quote


@dataclass
class LoginData:
    refreshToken: str
    uid: str


DEFAULT_GLOB_EXCLUDE = ["venv", ".venv", "__pycache__", ".databutton"]


@dataclass
class ProjectConfig:
    uid: str
    name: str
    # List of fnmatch patterns to exclude, similar to .gitignore
    exclude: Optional[List[str]] = field(default_factory=lambda: DEFAULT_GLOB_EXCLUDE)


CONFIG_PATH = "databutton.json"


def get_databutton_config(config_path=CONFIG_PATH, retries=2) -> ProjectConfig:
    try:
        with open(config_path, "r") as f:
            config = json.load(f)
            return ProjectConfig(
                name=config["name"], uid=config["uid"], exclude=config["exclude"]
            )
    except FileNotFoundError as e:
        if retries == 0:
            raise e
        return get_databutton_config(f"../{config_path}", retries=retries - 1)


def get_databutton_login_info() -> Union[LoginData, None]:
    if "DATABUTTON_TOKEN" in os.environ:
        config = get_databutton_config()
        return LoginData(uid=config.uid, refreshToken=os.environ["DATABUTTON_TOKEN"])

    auth_path = get_databutton_login_path()
    uids = [f for f in os.listdir(auth_path) if f.endswith(".json")]
    if len(uids) > 0:
        # Just take a random one for now
        with open(os.path.join(auth_path, uids[0])) as f:
            config = json.load(f)
            return LoginData(uid=config["uid"], refreshToken=config["refreshToken"])
    return None


def get_databutton_login_path():
    return os.path.join(Path.home(), ".config", "databutton")


def create_databutton_config(name: str, uid: str) -> ProjectConfig:
    config = ProjectConfig(name=name, uid=uid, exclude=DEFAULT_GLOB_EXCLUDE)
    with open(CONFIG_PATH, "w") as f:
        f.write(json.dumps(config.__dict__, indent=2))
        return config


FIREBASE_CONFIG = {
    "apiKey": "AIzaSyAdgR9BGfQrV2fzndXZLZYgiRtpydlq8ug",
    "authDomain": "databutton.firebaseapp.com",
    "projectId": "databutton",
    "storageBucket": "databutton.appspot.com",
    "databaseURL": "",
}
storage_bucket = (
    f"https://firebasestorage.googleapis.com/v0/b/{FIREBASE_CONFIG['storageBucket']}"
)


def upload_to_bucket(
    file_buf, config: ProjectConfig, key: str, content_type: str = "text/csv"
):
    upload_path = f"projects/{config.uid}/{key}"
    url = f"{storage_bucket}/o"
    token = get_auth_token()
    headers = {
        "Authorization": f"Firebase {token}",
        "Content-type": content_type,
    }
    response = requests.post(
        url, headers=headers, data=file_buf, params={"name": upload_path}
    )
    if not response.ok:
        raise Exception(f"Could not upload to path {key}")
    return response


def download_from_bucket(key: str, config: ProjectConfig):
    download_path = f"projects/{config.uid}/{key}"
    url = f"{storage_bucket}/o/{quote(download_path, safe='')}"
    token = get_auth_token()
    headers = {"Authorization": f"Firebase {token}"}
    response = requests.get(url, params={"alt": "media"}, headers=headers)
    if not response.ok:
        raise Exception(f"Could not download {key}")
    return response


def upload_archive(config: ProjectConfig, deployment_id: str, archive_path: str):
    upload_path = f"projects/{config.uid}/{deployment_id}"
    url = f"{storage_bucket}/o"
    token = get_auth_token()
    headers = {
        "Authorization": f"Firebase {token}",
        "Content-type": "application/tar+gzip",
    }
    with open(archive_path, "rb") as f:
        response = requests.post(
            url, headers=headers, data=f, params={"name": upload_path}
        )
        if not response.ok:
            raise Exception("Could not upload archive")
        metadata = {
            "deployment_id": deployment_id,
            "refresh_token": get_databutton_login_info().refreshToken,
        }
        meta_url = f"{storage_bucket}/o/{quote(upload_path, safe='')}"
        meta_res = requests.patch(
            meta_url,
            headers={"Authorization": headers["Authorization"]},
            json={"metadata": metadata},
        )
        if not meta_res.ok:
            raise Exception("Could not update metadata")


_cached_auth_token = None


def get_auth_token() -> str:
    global _cached_auth_token
    # This has a 15 minute cache
    if _cached_auth_token is not None and time() - _cached_auth_token[0] > 60 * 15:
        _cached_auth_token = None
    if _cached_auth_token is None:
        login_info = get_databutton_login_info()
        res = requests.post(
            f"https://securetoken.googleapis.com/v1/token?key={FIREBASE_CONFIG['apiKey']}",
            {"grant_type": "refresh_token", "refresh_token": login_info.refreshToken},
        )
        if not res.ok:
            raise Exception("Could not authenticate")
        json = res.json()
        _cached_auth_token = (time(), json["id_token"])
    return _cached_auth_token[1]


import functools


def catch_exceptions(cancel_on_failure=False):
    def catch_exceptions_decorator(job_func):
        @functools.wraps(job_func)
        def wrapper(*args, **kwargs):
            try:
                return job_func(*args, **kwargs)
            except Exception as e:
                import traceback

                logging.info(traceback.format_exc())
                if os.environ.get("SENTRY_DSN"):
                    import sentry_sdk

                    sentry_sdk.capture_exception(e)
                if cancel_on_failure:
                    return schedule.CancelJob

        return wrapper

    return catch_exceptions_decorator
