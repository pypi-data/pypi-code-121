from datetime import datetime
import urllib
import socket
import json
from urllib import request, parse
from urllib.error import HTTPError, URLError


class ContentType:
    JSON = "application/json"
    XML = "text/xml"
    FORMDATA = "multipart/form-data"
    URLENCODED = "application/x-www-form-urlencoded"


def translateDict2queryStr(post_data: any, enCoding="utf-8"):
    if isinstance(post_data, dict):
        post_data_params = ""
        m_result = post_data.items()
        m_count = 0
        for k, v in m_result:
            if isinstance(v, dict):
                post_data_params += k + "=" + json.dumps(v)
            elif isinstance(v, str):
                post_data_params += k + "=" + parse.quote(str(v))
            else:
                post_data_params + k + "=" + v
            m_count += 1
            if m_count < len(m_result):
                post_data_params += "&"
        return post_data_params
    else:
        return post_data


def serializePostData(post_data: any, isBytes=True, enCoding="utf-8"):
    """
    transformation dict to post data string.
    """
    if isinstance(post_data, dict):
        return json.dumps(post_data).encode(encoding=enCoding)
    if isinstance(post_data, str):
        return bytes(post_data, encoding=enCoding)
    if isinstance(post_data, bytes):
        return post_data
    else:
        raise("REST_HTTP serializePostData type error.")


def requestContentType(header: dict, type):
    if "Content-Type" not in header:
        header["Content-Type"] = type
    return header


def GET(
    uri: str,
    post_data={},
    http_headers: dict = None,
    content_type=ContentType.URLENCODED,
    time_out: int = 1,
    charset="utf-8",
):
    """
    http GET method

    - Parameters:
        uri: an uri, it can be an domain or ip, type must is cls<str>.
        post_data: <dict>, params.
        http_headers: set request's headers, default is None.
        time_out: time out for access remote uri , default value is 1 seconds.

    - Returs:
        stauts, body

        example:

            200, <html><body>this is an example</body></html>
    """
    try:
        req = None
        if post_data:
            m_params_data_str = serializePostData(
                translateDict2queryStr(post_data,enCoding=charset), isBytes=False, enCoding=charset
            )
            if uri.find("?") > -1:
                uri += "&" + m_params_data_str
            else:
                uri += "?" + m_params_data_str
        if http_headers:
            http_headers = requestContentType(http_headers, content_type)
            req = request.Request(uri, headers=http_headers, method="GET")
        else:
            req = request.Request(uri, method="GET")
        with request.urlopen(req, timeout=time_out) as response:
            return response.getcode(), response.read()
    except HTTPError as e:
        return e.code, e.reason
    except URLError as e:
        if isinstance(e.reason, socket.timeout):
            return 408, None
        else:
            return e.reason, None


def POST(
    uri,
    post_data: any,
    http_headers=None,
    content_type=ContentType.URLENCODED,
    time_out=1,
    charset="utf-8",
):
    """
    http POST method

    - Paramters:
        uri: an uri, it can be an domain or ip, type must is cls<str>.
        data: submit request post data.
        http_headers: set request's headers, default is None.
        time_out: time out for access remote uri , default value is 1 seconds.
        charset: set the http charset, default is UTF-8

    - Returns:
        status, body

        example:

            200, <html><body>this is an example</body></html>
    """
    try:
        req = None
        if post_data:
            if content_type== ContentType.URLENCODED:
                post_data = serializePostData(
                translateDict2queryStr(post_data,enCoding=charset), isBytes=False, enCoding=charset
                )
            else:
                post_data= serializePostData(post_data=post_data,enCoding=charset)
        if http_headers:
            http_headers = requestContentType(http_headers, content_type)
            req = request.Request(uri, data=post_data, headers=http_headers)
        else:
            req = request.Request(uri, data=post_data, method="POST")
        with request.urlopen(req, timeout=time_out) as response:
            return response.getcode(), response.read()
    except HTTPError as e:
        return e.code, e.reason
    except URLError as e:
        if isinstance(e.reason, socket.timeout):
            return 408, None
        else:
            return e.reason.errno, e.reason.strerror


def DELETE(uri, post_data={}, http_headers=None, content_type=ContentType.URLENCODED ,time_out=1, charset="utf-8"):
    try:
        req = None
        if post_data:
            m_params_data_str = serializePostData(
                translateDict2queryStr(post_data,enCoding=charset), isBytes=False, enCoding=charset
                )
            if uri.find("?") > -1:
                uri += "&" + m_params_data_str
            else:
                uri += "?" + m_params_data_str
        if http_headers:
            http_headers = requestContentType(http_headers, content_type)
            req = request.Request(uri, headers=http_headers, method=u"DELETE")
        else:
            req = request.Request(uri, method=u"DELETE")
        with request.urlopen(req, timeout=time_out) as response:
            return response.getcode(), response.read()
    except HTTPError as e:
        return e.code, e.reason
    except URLError as e:
        if isinstance(e.reason, socket.timeout):
            return 408, None
        else:
            return e.reason, None


def PUT(uri, post_data: bytes, http_headers=None, content_type= ContentType.URLENCODED, time_out=1, charset="UTF-8"):
    try:
        req = None
        if post_data:
            post_data = serializePostData(
                translateDict2queryStr(post_data,enCoding=charset), isBytes=False, enCoding=charset
                )
        if http_headers:
            http_headers = requestContentType(http_headers, content_type)
            req = request.Request(
                uri, data=post_data, headers=http_headers, method=u"PUT"
            )
        else:
            req = request.Request(uri, data=post_data, method=u"PUT")
        with request.urlopen(req, timeout=time_out) as response:
            return response.getcode(), response.read()
    except HTTPError as e:
        return e.code, e.reason
    except URLError as e:
        if isinstance(e.reason, socket.timeout):
            return 408, None
        else:
            return e.reason, None
