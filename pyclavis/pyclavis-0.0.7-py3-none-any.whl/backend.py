import os
import binascii
import hashlib
from cryptography.fernet import Fernet
from .passgen import Hash256

DEFAULT_STORE = "~/.pyclavis_store"
EOL = "\n"


class Backend(object):
    def load(self):
        raise NotImplementedError

    def save(self, cfg):
        raise NotImplementedError

    def filename(self):
        return DEFAULT_STORE

    def exists(self):
        raise NotImplementedError

    def load_defaults(self, default_cfg={}):
        # use this only when errors really can be omitted
        try:
            return self.load()
        except:
            pass
        return default_cfg


class FileBackend(Backend):
    def __init__(self, conv, fnam=None):
        self.conv = conv
        fnam = self.filename() if fnam == None else fnam
        fnam = os.path.expandvars(fnam)
        fnam = os.path.expanduser(fnam)
        self.fnam = os.path.abspath(fnam)

    def load(self):
        elem = []
        content = self._load().decode()
        for line in content.splitlines():
            c = self.conv.decode(line)
            elem.append(c)
        return elem

    def _load(self):
        with open(self.fnam, "rb") as fd:
            return fd.read()

    def exists(self):
        return os.path.exists(self.fnam)

    def save(self, cfg):
        s = ""
        for c in cfg:
            s += self.conv.encode(c)
            s += EOL
        self._save(s.encode())

    def _save(self, s):
        with open(self.fnam, "wb") as fd:
            fd.write(s)


class XorCryptedFileBackend(FileBackend):
    def __init__(self, passphrase, conv=None, fnam=None):
        super().__init__(conv=conv, fnam=fnam)
        if type(passphrase) == str:
            self.passphrase = passphrase.encode()

    def _load(self):
        return bytes(self._xor(super()._load()))

    def _save(self, s):
        super()._save(bytes(self._xor(s)))

    def _xor(self, content):
        if type(content) == str:
            content = content.encode()
        content = list(content)
        lenpass = len(self.passphrase)
        for i in range(0, len(content)):
            content[i] ^= self.passphrase[i % lenpass]
        return content


class CryptedFileBackend(FileBackend):
    def __init__(self, passphrase, conv=None, fnam=None):
        super().__init__(conv=conv, fnam=fnam)
        if type(passphrase) == str:
            self.passphrase = passphrase.encode()

        h256 = Hash256()
        h256.update(self.passphrase)
        digest64b = h256.base64_digest()

        self._crypt = Fernet(digest64b)

    def _load(self):
        return bytes(self.decrypt(super()._load()))

    def _save(self, s):
        super()._save(bytes(self.encrypt(s)))

    def encrypt(self, content):
        if type(content) == str:
            content = content.encode()
        return self._crypt.encrypt(content)

    def decrypt(self, content):
        if type(content) == str:
            content = content.encode()
        return self._crypt.decrypt(content)
