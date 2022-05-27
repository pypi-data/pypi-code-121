import base64
import hashlib
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

from .file import check_path_is_exits


def to_encode(connect: str) -> str:
    return str(
        base64.b64encode(bytes(connect, encoding="utf8")),
        encoding="utf8",
    )


def to_decode(connect: str) -> str:
    return str(base64.b64decode(bytes(connect, encoding="utf8")), encoding="utf8")


def sum_md5(param_str: str) -> str:
    """计算字符串MD5值"""
    if isinstance(param_str, int):
        param_str = str(param_str)
    _hash = hashlib.md5()
    _hash.update(param_str.encode("UTF-8"))
    return _hash.hexdigest()


def md5sum(*, _file_path: str = None, _string: str = None):
    """计算文件md5值"""
    if _file_path:
        check_path_is_exits(_file_path, path_type="file")
        with open(_file_path, "rb") as _file:
            return hashlib.md5(_file.read()).hexdigest()

    if _string:
        m = hashlib.md5()
        m.update(_string.encode())
        return m.hexdigest()

    raise ValueError("参数_file_path与_string必须二选一，不能都为空")


class MyCrypto(object):
    @classmethod
    def encrypt(cls, data, xsrf_token=None, old_secret=None) -> str:
        """加密"""
        if xsrf_token:
            key = cls.sha256(xsrf_token)
        else:
            key = old_secret
        if len(key) >= 32:
            key = key[:32]
        else:
            key = cls.__add_to_32(key)
        cipher1 = AES.new(key=key.encode("utf-8"), mode=AES.MODE_ECB)
        ct = cipher1.encrypt(pad(data.encode("utf-8"), 16))
        encrypt_data = base64.b64encode(ct)
        return encrypt_data.decode("utf-8")

    @classmethod
    def decrypt(cls, data, xsrf_token=None, old_secret=None) -> str:
        """解密"""
        if xsrf_token:
            key = cls.sha256(xsrf_token)
        else:
            key = old_secret
        if len(key) >= 32:
            key = key[:32]
        else:
            key = cls.__add_to_32(key)
        ct = base64.b64decode(data)
        cipher2 = AES.new(key=key.encode("utf-8"), mode=AES.MODE_ECB)
        pt = unpad(cipher2.decrypt(ct), 16)
        return pt.decode("utf-8")

    @classmethod
    def __add_to_32(cls, text):
        while len(text) % 32 != 0:
            text += "\0"
        return text

    @classmethod
    def sha256(cls, data):
        """sha256加密"""
        return hashlib.sha256(data.encode("utf-8")).hexdigest()

    @staticmethod
    def aes_cbc_encrypt(key, content, iv):
        """AES CBC加密"""

        def __pad(text):
            bs = 16
            padding_size = len(text.encode("utf-8"))
            padding = bs - padding_size % bs
            padding_text = chr(padding) * padding
            return text + padding_text

        cipher = AES.new(key.encode("utf-8"), AES.MODE_CBC, iv.encode("utf-8"))
        # 处理明文
        content_padding = __pad(content)
        # 加密
        encrypt_bytes = cipher.encrypt(content_padding.encode("utf-8"))
        # 重新编码
        result = str(base64.b64encode(encrypt_bytes), encoding="utf-8")
        return result

    @staticmethod
    def aes_cbc_decrypt(key, content, iv):
        """AES CBC解密"""

        def __un_pad(_s):
            return _s[: -ord(_s[len(_s) - 1 :])]

        cipher = AES.new(key.encode("utf-8"), AES.MODE_CBC, iv.encode("utf-8"))
        content = base64.b64decode(content)
        text = cipher.decrypt(content).decode("utf-8")
        return __un_pad(text)
