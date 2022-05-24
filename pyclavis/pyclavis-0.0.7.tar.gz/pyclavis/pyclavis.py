from .credit import Credential
from .store import CredentialStore
from .backend import (
    FileBackend,
    XorCryptedFileBackend,
    CryptedFileBackend,
    DEFAULT_STORE,
)
from .conv import Conv, ConvTabCsv, ConvJson
from .keyconv import KeyBase64Conv
from .loginproc import LoginParam, Autofill, send_seq, DELAY_STD


class Formatter(object):
    def to2line(self, c):
        return c.user + "\n" + c.passwd

    def to2tuple(self, c):
        return c.user, c.passwd

    def to2tab(self, c):
        return c.user + "\t" + c.passwd


VERSION = "v0.0.7"
