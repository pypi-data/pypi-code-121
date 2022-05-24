import os

from .logging import log, print_t, print_e
from .pyclavis import KeyBase64Conv, ConvJson, CryptedFileBackend


def expand_path(fpath):
    if type(fpath) in [list, tuple]:
        fpath = os.path.join(*fpath)
    fpath = os.path.expandvars(fpath)
    fpath = os.path.expanduser(fpath)
    fpath = os.path.abspath(fpath)
    return fpath


def readkeyfile():
    clavis = expand_path("~/.pyclavis_key")
    try:
        with open(clavis) as f:
            clavis = f.read().strip()
            print_t("read clavis key")
    except:
        clavis = None
    return clavis


def createkeystorage(passphrase):
    pp = KeyBase64Conv().convert(passphrase)
    conv = ConvJson()
    storage = CryptedFileBackend(conv=conv, passphrase=pp)
    return storage


def readkeystore(secman, storage):
    loaded = None
    secman.clear()

    if storage.exists():
        try:
            _credits = storage.load()

            print_t("loaded", _credits)

            secman.fromlist(_credits)
            loaded = True

        except Exception as ex:
            print_e(ex, "load credits")
    else:
        print_t("no storage file found")
        loaded = False

    return loaded
