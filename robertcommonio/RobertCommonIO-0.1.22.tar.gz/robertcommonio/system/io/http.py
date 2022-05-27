import logging
import json
from typing import Optional, Union, NamedTuple

import requests
from requests.auth import AuthBase
from requests.packages.urllib3.exceptions import InsecureRequestWarning
# 禁用安全请求警告
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

from robertcommonbasic.basic.error.utils import E_INTERNAL, InputDataError, S_OK
from robertcommonbasic.basic.data.type import JsonType
from robertcommonbasic.basic.validation import input
from robertcommonbasic.basic.log import utils as logutils


class Response(NamedTuple):
    success: bool
    code: str
    msg: Optional[str]
    data: Optional[JsonType]


class HttpTool:
    def __init__(self):
       pass

    def send_json(self,
                  url: str,
                  data: Union[str, JsonType, None] = None,
                  extra_headers: Optional[dict] = None,
                  auth: Optional[AuthBase] = None,
                  method: Optional[str] = None,
                  encoding: Optional[str] = None,
                  raise_error: Optional[bool] = None,
                  log_input: Optional[bool] = None,
                  log_output: Optional[bool] = None,
                  log_error: Optional[bool] = None,
                  retry: Optional[int] = None,
                  timeout: Optional[int] = None) -> Response:
        return self._send_json(
            url=url, data=data, extra_headers=extra_headers, method=method, auth=auth,
            encoding=encoding, raise_error=raise_error, log_input=log_input,
            log_output=log_output, log_error=log_error, retry=retry,
            timeout=timeout)

    @classmethod
    def _send_json(cls,
                   url: str,
                   data: Union[str, JsonType, None] = None,
                   extra_headers: Optional[dict] = None,
                   method: Optional[str] = None,
                   auth: Optional[AuthBase] = None,
                   encoding: Optional[str] = None,
                   raise_error: Optional[bool] = None,
                   log_input: Optional[bool] = None,
                   log_output: Optional[bool] = None,
                   log_error: Optional[bool] = None,
                   retry: Optional[int] = None,
                   timeout: Optional[int] = None) -> Response:
        args_log = f"encoding={encoding}, raise_error={raise_error}, " \
                   f"log_input={log_input}, log_output={log_output}," \
                   f"log_error={log_error}, retry={retry}, method={method}, " \
                   f"timeout={timeout}"

        max_log_size = 32767
        if extra_headers is None:
            extra_headers = {}
        if not isinstance(extra_headers, dict):
            raise InputDataError(
                f"extra_headers is not a dict: {extra_headers}.")
        raise_error = input.ensure_bool(
            'raise_error', raise_error, default_to=False)
        log_input = input.ensure_bool('log_input', log_input, default_to=False)
        log_output = input.ensure_bool('log_input', log_output, default_to=False)
        log_error = input.ensure_bool('log_error', log_error, default_to=False)
        retry = input.ensure_int('retry', retry, default_to=4)
        method = input.ensure_str('method', method, default_to='POST').upper()
        timeout = input.ensure_int('timeout', timeout, default_to=60)
        encoding = input.ensure_str('encoding', encoding, default_to='utf-8')

        if data is None:
            payload = None
        elif isinstance(data, str):
            payload = data
        else:
            payload = json.dumps(data)

        if log_input:
            logging.info(f'Calling {url} with {args_log} and '
                         f'{payload[:max_log_size] if payload else payload}...')

        last_error = None
        for i in range(0, retry):
            if i > 0 and log_input:
                logging.info(f'Retrying {i}(th) time...', i)
            try:
                headers = {"content-type": f"application/json"}
                headers.update(extra_headers)
                if method == 'GET':
                    response = requests.get(
                        url=url, headers=headers, timeout=timeout, auth=auth, verify=False)
                elif method == 'POST':
                    response = requests.post(
                        url=url, headers=headers, data=payload, timeout=timeout, auth=auth, verify=False)
                else:
                    raise NotImplementedError(
                        f"Method {method} is not supported yet.")

                if response.status_code == 200:
                    response.encoding = encoding
                    if log_output:
                        logging.info(f'Result: {response.text}')
                    return Response(True, S_OK, '', response.text)
                raise Exception(f'Unexpected result: {response.status_code} {response.text[:max_log_size]}')
            except Exception as e:
                last_error = e
                if log_error:
                    logutils.log_unhandled_error()

        last_error_msg = f'Failed to post JSON request after all retries! {last_error.__str__()}'
        if log_error:
            logging.error(last_error_msg)
        if raise_error:
            raise last_error
        else:
            return Response(False, E_INTERNAL, last_error.__str__(), None)

    def send_request(self,
                  url: str,
                  method: Optional[str] = None,
                  params: Union[str, JsonType, None] = None,
                  data: Union[str, JsonType, None] = None,
                  files: Union[str, JsonType, None] = None,
                  headers: Optional[dict] = None,
                  cookies: Optional[dict] = None,
                  auth: Optional[AuthBase] = None,
                  encoding: Optional[str] = None,
                  raise_error: Optional[bool] = None,
                  log_input: Optional[bool] = None,
                  log_output: Optional[bool] = None,
                  log_error: Optional[bool] = None,
                  retry: Optional[int] = None,
                  timeout: Optional[int] = None) -> Response:
        return self._send_request(
            url=url, method=method, params=params, files=files, data=data, headers=headers, cookies=cookies, auth=auth,
            encoding=encoding, raise_error=raise_error, log_input=log_input,
            log_output=log_output, log_error=log_error, retry=retry,
            timeout=timeout)

    @classmethod
    def _send_request(cls,
                   url: str,
                   method: Optional[str] = None,
                   params: Union[str, JsonType, None] = None,
                   data: Union[str, JsonType, None] = None,
                   files: Union[str, JsonType, None] = None,
                   headers: Optional[dict] = None,
                   cookies: Optional[dict] = None,
                   auth: Optional[AuthBase] = None,
                   encoding: Optional[str] = None,
                   raise_error: Optional[bool] = None,
                   log_input: Optional[bool] = None,
                   log_output: Optional[bool] = None,
                   log_error: Optional[bool] = None,
                   retry: Optional[int] = None,
                   timeout: Optional[int] = None) -> Response:
        args_log = f"encoding={encoding}, raise_error={raise_error}, " \
                   f"log_input={log_input}, log_output={log_output}," \
                   f"log_error={log_error}, retry={retry}, method={method}, " \
                   f"timeout={timeout}"

        max_log_size = 32767
        if headers is None:
            headers = {}
        raise_error = input.ensure_bool('raise_error', raise_error, default_to=False)
        log_input = input.ensure_bool('log_input', log_input, default_to=False)
        log_output = input.ensure_bool('log_input', log_output, default_to=False)
        log_error = input.ensure_bool('log_error', log_error, default_to=False)
        retry = input.ensure_int('retry', retry, default_to=4)
        method = input.ensure_str('method', method, default_to='POST').upper()
        timeout = input.ensure_int('timeout', timeout, default_to=60)
        encoding = input.ensure_str('encoding', encoding, default_to='utf-8')

        payload = data

        if log_input:
            logging.info(f'Calling {url} with {args_log} and {payload[:max_log_size] if payload else payload}...')

        last_error = None
        for i in range(0, retry):
            if i > 0 and log_input:
                logging.info(f'Retrying {i}(th) time...', i)
            try:
                if method == 'GET':
                    response = requests.get(
                        url=url, headers=headers, timeout=timeout, auth=auth, verify=False)
                elif method == 'POST':
                    response = requests.post(
                        url=url, headers=headers, files=files, data=payload, params=params, timeout=timeout, auth=auth, verify=False)
                else:
                    raise NotImplementedError(
                        f"Method {method} is not supported yet.")

                if response.status_code == 200:
                    response.encoding = encoding
                    if log_output:
                        logging.info(f'Result: {response.text}')
                    return Response(True, S_OK, '', response.text)
                raise Exception(f'Unexpected result: {response.status_code} {response.text[:max_log_size]}')
            except Exception as e:
                last_error = e
                if log_error:
                    logutils.log_unhandled_error()

        last_error_msg = f'Failed to post JSON request after all retries! {last_error.__str__()}'
        if log_error:
            logging.error(last_error_msg)
        if raise_error:
            raise last_error
        else:
            return Response(False, E_INTERNAL, last_error.__str__(), None)
