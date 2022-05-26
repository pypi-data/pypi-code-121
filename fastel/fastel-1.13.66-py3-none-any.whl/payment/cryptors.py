import base64
import json
import urllib.parse
from hashlib import md5, sha256
from typing import Any, Callable, Dict, Union

from Crypto.Cipher import AES


class BaseCryptor:
    def __init__(self, hash_key: str, hash_iv: str):
        self.hash_key = hash_key
        self.hash_iv = hash_iv

    def encrypt(self, data: Any) -> str:
        raise NotImplementedError

    def decrypt(self, data: Any) -> str:
        raise NotImplementedError

    def build_trade_sha(self, built_data: str) -> str:
        raise NotImplementedError


class EcInvoiceCryptor(BaseCryptor):
    def pad(self, str_data: str) -> str:
        length = AES.block_size - (len(str_data) % AES.block_size)
        if length == 0:
            length = AES.block_size
        str_data += chr(length) * length
        return str_data

    def encrypt(self, data: Dict[str, Any]) -> str:
        json_data = json.dumps(data)
        encode_str = urllib.parse.quote(json_data)
        cryptor = AES.new(self.hash_key, AES.MODE_CBC, self.hash_iv)
        result = cryptor.encrypt(self.pad(encode_str).encode())
        return base64.b64encode(result).decode()

    def decrypt(self, data: Union[str, bytes]) -> str:
        unpad: Callable[[str], str] = lambda s: s[: -ord(s[len(s) - 1 :])]
        data = base64.b64decode(data)
        cryptor = AES.new(self.hash_key, AES.MODE_CBC, self.hash_iv)
        aes_data = cryptor.decrypt(data).decode()
        unpad_data = unpad(aes_data)
        real_data = urllib.parse.unquote(unpad_data).replace("null", '""')
        real_data = eval(real_data)
        return real_data


class SHACryptor(BaseCryptor):
    def _format_str(self, _str: str) -> str:
        conflict_patterns = [
            ("%2d", "-"),
            ("%5f", "_"),
            ("%2e", "."),
            ("%21", "!"),
            ("%2a", "*"),
            ("%28", "("),
            ("%29", ")"),
            ("%20", "+"),
            ("/", "%2f"),
        ]
        for pattern, replacement in conflict_patterns:
            _str = _str.replace(pattern, replacement)
        return _str

    def encrypt(self, data: Dict[str, Any]) -> str:
        cipher = sha256
        real_data = json.loads(json.dumps(data, sort_keys=True))
        data_str = "&".join(map(lambda v: f"{v[0]}={v[1]}", real_data.items()))
        data_str = f"HashKey={self.hash_key}&{data_str}&HashIV={self.hash_iv}".lower()
        data_str = self._format_str(urllib.parse.quote(data_str).lower())
        d = cipher(data_str.encode())
        return d.hexdigest().upper()


class MD5Cryptor(SHACryptor):
    def encrypt(self, data: Dict[str, Any]) -> str:
        cipher = md5
        real_data = json.loads(json.dumps(data, sort_keys=True))
        data_str = "&".join(map(lambda v: f"{v[0]}={v[1]}", real_data.items()))
        data_str = f"HashKey={self.hash_key}&{data_str}&HashIV={self.hash_iv}".lower()
        data_str = self._format_str(urllib.parse.quote(data_str).lower())
        d = cipher(data_str.encode())

        return d.hexdigest().upper()


class AESCryptor(BaseCryptor):
    def pad(self, str_data: str) -> str:
        length = AES.block_size - (len(str_data) % AES.block_size)
        str_data += chr(length) * length
        return str_data

    def encrypt(self, data: Dict[str, Any]) -> str:
        info_str = urllib.parse.urlencode(data, quote_via=urllib.parse.quote)  # type: ignore
        cryptor = AES.new(self.hash_key.encode(), AES.MODE_CBC, self.hash_iv.encode())
        result = cryptor.encrypt(self.pad(info_str).encode())
        result = result.hex()
        assert isinstance(result, str)
        return result

    def decrypt(self, data: str) -> str:
        unpad: Callable[[str], str] = lambda s: s[: -ord(s[len(s) - 1 :])]
        cyrptor = AES.new(self.hash_key.encode(), AES.MODE_CBC, self.hash_iv.encode())
        return unpad(cyrptor.decrypt(bytes.fromhex(data)).decode())

    def build_trade_sha(self, built_data: str) -> str:
        key_data_iv = "HashKey={}&{}&HashIV={}".format(
            self.hash_key, built_data, self.hash_iv
        )
        return sha256(key_data_iv.encode()).hexdigest().upper()
