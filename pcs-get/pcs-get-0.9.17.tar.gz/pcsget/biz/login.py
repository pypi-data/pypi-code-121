# -*- coding: utf-8 -*-
import re

from lxml import etree
from requests import Session

from .config import *
from .log import *


def login(session, user, pw):
    """
    :type session: Session
    :type user: str
    :type pw: str
    :rtype: str
    """
    d("login invoked. n:" + user + " p:" + pw)
    redirected_login_page = session.get("http://release.bigo.local:8081/#/demand", allow_redirects=True)
    d("login page url:" + redirected_login_page.url)
    d("login page status_code:" + str(redirected_login_page.status_code))
    if redirected_login_page.status_code != 200:
        return False
    hidden_field = etree.HTML(redirected_login_page.text).xpath("//*[@id='fm1']/input[1]/@value")[0]
    d("login page hidden_field_val:" + str(hidden_field))
    login_res = session.post(
        url='https://auth.bigo.sg/cas/login?service=http://release.bigo.local:8081/accounts/login/?next=%2F',
        data={
            'username': user,
            'password': pw,
            'execution': hidden_field,
            '_eventId': 'submit',
            'geolocation': '',
        },
        headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/99.0.4844.83 Safari/537.36',
        },
        allow_redirects=True
    )
    d("login api url:" + login_res.url)
    d("login api status_code:" + str(login_res.status_code))
    if login_res.status_code != 200 or (
            login_res.url != 'http://release.bigo.local:8081/' and login_res.url != 'http://protocol.client.bigo.inner/'):
        return False
    for key, value in login_res.request.headers.items():
        d("login headers:" + key + "=" + value)
        if key == 'Cookie':
            if not value.endswith(';'):
                value += ';'
            d("login cookie" + "=" + value)
            r_token = re.match(r'.*csrftoken=(.*?);', value)
            r_session = re.match(r'.*sessionid=(.*?);', value)
            d("login r_token" + "=" + str(r_token))
            d("login r_session" + "=" + str(r_session))
            if r_token is not None and r_session is not None:
                t = r_token.group(1)
                s = r_session.group(1)
                d("login cookie headers parsed, token:" + t + " session:" + s)
                if len(t) > 0 and len(s) > 0:
                    nc = {K_TOKEN: t, K_SESSION: s}
                    update_config(**nc)
                    d("login success!")
                    return True
    return False


def is_session_login(session):
    """
    通过请求一个较小的协议来检查本地cookie是否仍然有效
    :type session: Session
    """
    response = session.get(
        url="http://protocol.client.bigo.inner/get_user_message/",
        allow_redirects=False
    )
    if response.status_code != 200:
        return False
    body = response.json()
    if 'status' not in body or body['status'] != 200:
        return False
    return True
