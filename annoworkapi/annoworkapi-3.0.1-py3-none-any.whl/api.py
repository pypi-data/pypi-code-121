from __future__ import annotations

import copy
import functools
import json
import logging
from json import JSONDecodeError
from logging import Logger
from typing import Any, Optional

import backoff
import requests
from requests.auth import AuthBase

from annoworkapi.generated_api import AbstractAnnoworkApi

logger = logging.getLogger(__name__)

DEFAULT_ENDPOINT_URL = "https://annowork.com"


def _raise_for_status(response: requests.Response) -> None:
    """
    HTTP Status CodeがErrorの場合、``requests.exceptions.HTTPError`` を発生させる。
    そのとき ``response.text`` もHTTPErrorに加えて、HTTPError発生時にエラーの原因が分かるようにする。


    Args:
        response: Response

    Raises:
        requests.exceptions.HTTPError:

    """
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        http_error_msg = f"{e.args[0]} , {response.text}"
        e.args = (http_error_msg,)
        raise e


def _log_error_response(arg_logger: logging.Logger, response: requests.Response) -> None:
    """
    HTTP Statusが400以上ならば、loggerにresponse/request情報を出力する


    Args:
        arg_logger: logger
        response: Response

    """

    def mask_key(d, key: str):
        if key in d:
            d[key] = "***"

    if 400 <= response.status_code < 600:
        headers = copy.deepcopy(response.request.headers)
        # logにAuthorizationを出力しないようにマスクする
        mask_key(headers, "Authorization")

        # request_bodyのpassword関係をマスクして、logに出力する
        request_body = response.request.body
        request_body_for_logger: Optional[Any]
        if request_body is not None and request_body != "":
            try:
                dict_request_body = json.loads(request_body)
            except JSONDecodeError:
                request_body_for_logger = request_body
            else:
                request_body_for_logger = _create_request_body_for_logger(dict_request_body)
        else:
            request_body_for_logger = request_body

        arg_logger.error(
            "HTTP error occurred :: %s",
            {
                "response": {
                    "status_code": response.status_code,
                    "text": response.text,
                },
                "request": {
                    "http_method": response.request.method,
                    "url": response.request.url,
                    "body": request_body_for_logger,
                    "headers": headers,
                },
            },
        )


def ignore_http_error(
    func=None, /, *, status_code_list: list[int], logger: Optional[Logger] = None
):  # pylint: disable=redefined-outer-name
    """
    HTTPErrorが発生したとき、特定のstatus codeを無視して、処理する。
    無視した場合、Noneを返す。

    Args:
        status_code_list: 無視するステータスコードのリスト
        logger:
    """
    new_logger = logging.getLogger(__name__) if logger is None else logger

    def decorator(function):
        @functools.wraps(function)
        def wrapped(*args, **kwargs):
            try:
                return function(*args, **kwargs)

            except requests.exceptions.HTTPError as e:
                if e.response.status_code in status_code_list:
                    return None
                else:
                    _log_error_response(new_logger, e.response)
                    raise e

        return wrapped

    if func is None:
        # We're called with parens.
        return decorator

    # We're called as @dataclass without parens.
    return decorator(func)


def allow_404_error(func=None, /, *, logger: Optional[Logger] = None):  # pylint: disable=redefined-outer-name
    """
    Not Found Error(404)を無視(許容)して、処理するデコレータ。Not Found Errorが発生したときはNoneを返す。
    リソースの存在確認などに利用する。
    """

    def wrap(func):
        return ignore_http_error(func, status_code_list=[requests.codes.not_found], logger=logger)

    if func is None:
        return wrap

    return wrap(func)


def my_backoff(function):
    """
    リトライが必要な場合はリトライする
    """

    @functools.wraps(function)
    def wrapped(*args, **kwargs):
        def fatal_code(e):
            """
            リトライするかどうか
            status codeが5xxのときまたはToo many Requests(429)のときはリトライする。
            ただし500はリトライしない
            https://requests.kennethreitz.org/en/master/user/quickstart/#errors-and-exceptions

            Args:
                e: exception

            Returns:
                True: give up(リトライしない), False: リトライする

            """
            if isinstance(e, requests.exceptions.HTTPError):
                if e.response is None:
                    return True

                # status_codeの範囲は4XX ~ 5XX
                status_code = e.response.status_code

                if status_code == requests.codes.internal_server_error:
                    return True
                elif status_code == requests.codes.too_many_requests:
                    return False
                elif 400 <= status_code < 500:
                    return True
                elif 500 <= status_code < 600:
                    return False

            return False

        return backoff.on_exception(
            backoff.expo,
            (requests.exceptions.RequestException, ConnectionError),
            jitter=backoff.full_jitter,
            max_time=300,
            giveup=fatal_code,
            logger=logger,
            # giveup時のレベルがデフォルトのERRORだと、`wrapper.get_job_or_none` などを実行したときに不要なログが出力されるため、ログレベルをDEBUG以下に下げておく
            giveup_log_level=logging.NOTSET,
        )(function)(*args, **kwargs)

    return wrapped


def _create_request_body_for_logger(data: Any) -> Any:
    """
    ログに出力するためのreqest_bodyを生成する。
     * パスワードやトークンなどの機密情報をマスクする
     * bytes型の場合は `(bytes)`と記載する。


    Args:
        data: request_body

    Returns:
        ログ出力用のrequest_body
    """

    def mask_key(d, key: str):
        if key in d:
            d[key] = "***"

    if not isinstance(data, dict):
        return data
    elif isinstance(data, bytes):
        # bytes型のときは値を出力しても意味がないので、bytesであることが分かるようにする
        return "(bytes)"

    MASKED_KEYS = {
        "password",
        "confirmation_code",
        "new_password",
    }
    diff = MASKED_KEYS - set(data.keys())
    if len(diff) == len(MASKED_KEYS):
        # マスク対象のキーがない
        return data

    copied_data = copy.deepcopy(data)
    for key in MASKED_KEYS:
        mask_key(copied_data, key)

    return copied_data


class AnnoworkApi(AbstractAnnoworkApi):
    """
    Web APIに対応したメソッドが存在するクラス。

    Args:
        login_user_id: AnnoWorkにログインするときのユーザID
        login_password: AnnoWorkにログインするときのパスワード
        endpoint_url: WebAPI URLのbase部分
    """

    def __init__(self, login_user_id: str, login_password: str, endpoint_url: str = DEFAULT_ENDPOINT_URL):

        if not login_user_id or not login_password:
            raise ValueError("login_user_id or login_password is empty.")

        self.login_user_id = login_user_id
        self.login_password = login_password
        self.base_url = f"{endpoint_url}/api/v1"
        self.session = requests.Session()

        self.token_dict: Optional[dict[str, Any]] = None

    class __MyToken(AuthBase):
        """
        requestsモジュールのauthに渡す情報。
        http://docs.python-requests.org/en/master/user/advanced/#custom-authentication
        """

        def __init__(self, id_token: str):
            self.id_token = id_token

        def __call__(self, req):
            req.headers["Authorization"] = self.id_token
            return req

    #########################################
    # Private Method
    #########################################
    def _create_kwargs(
        self,
        params: Optional[dict[str, Any]] = None,
        headers: Optional[dict[str, Any]] = None,
        request_body: Optional[Any] = None,
    ) -> dict[str, Any]:
        """
        requestsモジュールのget,...メソッドに渡すkwargsを生成する。

        Args:
            params: クエリパラメタに設定する情報
            headers: リクエストヘッダに設定する情報

        Returns:
            kwargs情報

        """

        # query_param
        new_params = {}
        if params is not None:
            for key, value in params.items():
                if isinstance(value, (list, dict)):
                    new_params[key] = json.dumps(value)
                else:
                    new_params[key] = value

        kwargs: dict[str, Any] = {
            "params": new_params,
            "headers": headers,
        }
        if self.token_dict is not None:
            kwargs.update({"auth": self.__MyToken(self.token_dict["id_token"])})

        if request_body is not None:
            if isinstance(request_body, (dict, list)):
                kwargs.update({"json": request_body})

            elif isinstance(request_body, str):
                kwargs.update({"data": request_body.encode("utf-8")})

            else:
                kwargs.update({"data": request_body})

        return kwargs

    @staticmethod
    def _response_to_content(response: requests.Response) -> Any:
        """
        Responseのcontentを、Content-Typeに対応した型に変換する。

        Args:
            response:

        Returns:
            JSONの場合はdict, textの場合はstringのcontent

        """

        content_type = response.headers["Content-Type"]
        # `Content-Type: application/json;charset=utf-8`などcharsetが含まれている場合にも対応できるようにする。
        tokens = content_type.split(";")
        media_type = tokens[0].strip()

        if media_type == "application/json":
            content = response.json() if len(response.content) != 0 else {}

        elif media_type.find("text/") >= 0:
            content = response.text

        else:
            content = response.content

        return content

    @my_backoff
    def _execute_http_request(
        self,
        http_method: str,
        url: str,
        *,
        params: Optional[dict[str, Any]] = None,
        data: Optional[Any] = None,
        json: Optional[Any] = None,  # pylint: disable=redefined-outer-name
        headers: Optional[dict[str, Any]] = None,
        **kwargs,
    ) -> requests.Response:
        """Session情報を使って、HTTP Requestを投げる。
        引数は ``requests.Session.request`` にそのまま渡す。

        Args:
            raise_for_status: Trueの場合HTTP Status Codeが4XX,5XXのときはHTTPErrorをスローします

        Returns:
            requests.Response: [description]

        Raises:
            requests.exceptions.HTTPError: http status codeが4XXX,5XXXのとき

        """
        response = self.session.request(
            method=http_method, url=url, params=params, data=data, headers=headers, json=json, **kwargs
        )

        # response.requestよりメソッド引数のrequest情報の方が分かりやすいので、メソッド引数のrequest情報を出力する。
        logger.debug(
            "Sent a request :: %s",
            {
                "requests": {
                    "http_method": http_method,
                    "url": url,
                    "query_params": params,
                    "request_body_json": _create_request_body_for_logger(json) if json is not None else None,
                    "request_body_data": _create_request_body_for_logger(data) if data is not None else None,
                    "header_params": headers,
                },
                "response": {
                    "status_code": response.status_code,
                    "content_length": len(response.content),
                },
            },
        )
        _log_error_response(logger, response)
        _raise_for_status(response)

        return response

    @my_backoff
    def _request_wrapper(
        self,
        http_method: str,
        url_path: str,
        *,
        query_params: Optional[dict[str, Any]] = None,
        header_params: Optional[dict[str, Any]] = None,
        request_body: Optional[Any] = None,
        log_response_with_error: bool = True,
    ) -> Any:
        """
        HTTP Requestを投げて、Responseを返す。

        Args:
            http_method:
            url_path:
            query_params:
            header_params:
            request_body:
            log_response_with_error: HTTP Errorが発生したときにレスポンスの中身をログに出力するか否か

        Returns:
            responseの中身。content_typeにより型が変わる。
            application/jsonならdict型, text/*ならばstr型, それ以外ならばbite型。

        """
        url = f"{self.base_url}{url_path}"

        kwargs = self._create_kwargs(query_params, header_params, request_body)

        response = getattr(self.session, http_method.lower())(url, **kwargs)

        logger.debug(
            "Sent a request :: %s",
            {
                "request": {
                    "http_method": http_method.lower(),
                    "url": url,
                    "query_params": query_params,
                    "header_params": header_params,
                    "request_body": _create_request_body_for_logger(request_body) if request_body is not None else None,
                },
                "response": {
                    "status_code": response.status_code,
                    "content_length": len(response.content),
                },
            },
        )

        # Unauthorized Errorならば、ログイン後に再度実行する
        if response.status_code == requests.codes.unauthorized:
            self.login()
            return self._request_wrapper(
                http_method,
                url_path,
                query_params=query_params,
                header_params=header_params,
                request_body=request_body,
                log_response_with_error=log_response_with_error,
            )

        response.encoding = "utf-8"
        content = self._response_to_content(response)

        if log_response_with_error:
            _log_error_response(logger, response)
        _raise_for_status(response)
        return content

    #########################################
    # Public Method : Login
    #########################################
    @my_backoff
    def login(self) -> dict[str, Any]:
        """
        ログイン


        Returns:
            Token情報

        """
        request_body = {"user_id": self.login_user_id, "password": self.login_password}

        url = f"{self.base_url}/login"

        response = self._execute_http_request(http_method="post", url=url, json=request_body)
        json_obj = response.json()
        self.token_dict = json_obj

        return json_obj
