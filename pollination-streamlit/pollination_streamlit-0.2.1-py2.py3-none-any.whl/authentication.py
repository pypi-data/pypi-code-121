import base64
import os
import re
import typing as t

import extra_streamlit_components as stx
import streamlit as st

COOKIE_NAME = os.getenv('COOKIE_NAME', 'pollination-authz')


@st.cache(allow_output_mutation=True)
def get_manager():
    return stx.CookieManager()


def _decode_base64(data, altchars=b'+/'):
    """Decode base64, padding being optional.

    :param data: Base64 data as an ASCII byte string
    :returns: The decoded byte string.

    """
    data = re.sub(rb'[^a-zA-Z0-9%s]+' % altchars, b'', data)  # normalize
    missing_padding = len(data) % 4
    if missing_padding:
        data += b'=' * (4 - missing_padding)
    return base64.b64decode(data, altchars)


def _decrypt_cookie(cookie: str):
    b64_bytes = _decode_base64(str.encode(cookie))
    parts = b64_bytes.split(b'|')
    value = parts[1]
    token_bytes = _decode_base64(value)
    return token_bytes.decode('utf-8')


def get_jwt_from_browser() -> t.Optional[str]:
    cookies = get_manager().get_all()
    cookie = cookies.get(COOKIE_NAME)
    if cookie is None:
        return cookie
    return _decrypt_cookie(cookie)
