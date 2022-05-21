import logging
import netrc
import os
from urllib.parse import urlparse

from annoworkapi.api import DEFAULT_ENDPOINT_URL, AnnoworkApi
from annoworkapi.exceptions import AnnoworkApiException
from annoworkapi.wrapper import Wrapper

logger = logging.getLogger(__name__)


class Resource:
    """

    Args:
        login_user_id: ログインするときのユーザID
        login_password:ログインするときのパスワード
        endpoint_url: annoworkのendpointであるURL

    """

    def __init__(self, login_user_id: str, login_password: str, endpoint_url: str = DEFAULT_ENDPOINT_URL):
        self.api = AnnoworkApi(login_user_id=login_user_id, login_password=login_password, endpoint_url=endpoint_url)
        self.wrapper = Wrapper(self.api)

        logger.debug(
            "Create annoworkapi resource instance :: %s", {"login_user_id": login_user_id, "endpoint_url": endpoint_url}
        )


def build_from_netrc(endpoint_url: str = DEFAULT_ENDPOINT_URL) -> Resource:
    """
    ``.netrc`` ファイルから、Resourceインスタンスを生成する。
    """
    try:
        netrc_hosts = netrc.netrc().hosts
    except FileNotFoundError as e:
        raise AnnoworkApiException(e) from e

    annowork_hostname = (urlparse(endpoint_url)).hostname

    if annowork_hostname not in netrc_hosts:
        raise AnnoworkApiException(f"The `.netrc` file does not contain the machine name '{annowork_hostname}'")

    host = netrc_hosts[annowork_hostname]
    login_user_id = host[0]
    login_password = host[2]
    if login_user_id is None or login_password is None:
        raise AnnoworkApiException("User ID or password in the .netrc file are None.")

    return Resource(login_user_id, login_password, endpoint_url=endpoint_url)


def build_from_env(endpoint_url: str = DEFAULT_ENDPOINT_URL) -> Resource:
    """
    環境変数 ``ANNOWORK_USER_ID`` , ``ANNOWORK_PASSWORD`` から、Resourceインスタンスを生成する。

    Args:
        endpoint_url: APIのエンドポイント。

    Returns:
        Resourceインスタンス

    """
    login_user_id = os.environ.get("ANNOWORK_USER_ID")
    login_password = os.environ.get("ANNOWORK_PASSWORD")
    if login_user_id is None or login_password is None:
        raise AnnoworkApiException("`ANNOWORK_USER_ID` or `ANNOWORK_PASSWORD`  environment variable are empty.")

    return Resource(login_user_id, login_password, endpoint_url=endpoint_url)


def build(endpoint_url: str = DEFAULT_ENDPOINT_URL) -> Resource:
    """
    ``.netrc`` ファイルまたは環境変数から認証情報を取得し、Resourceインスタンスを生成します。
    netrc, 環境変数の順に認証情報を読み込みます。

    """
    # '.netrc'ファイルから認証情報を取得する
    try:
        return build_from_netrc(endpoint_url)
    except AnnoworkApiException:
        pass

    # 環境変数から認証情報を取得する
    try:
        return build_from_env(endpoint_url)
    except AnnoworkApiException:
        pass

    raise AnnoworkApiException("`.netrc`ファイルまたは環境変数にAnnoWork認証情報はありませんでした。")
