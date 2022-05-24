import os
import json

from .logging import log, print_t, print_e

from .conv import Conv
from .backend import FileBackend, CryptedFileBackend

from .downloads import CONFIG_HOME

FAVORITES = os.path.join(CONFIG_HOME, "favorites.crypt.json")


class JsonConv(Conv):
    def decode(self, s):
        para = json.loads(s)
        fav = Favorite()
        fav.__dict__.update(para)
        return fav

    def encode(self, fav):
        s = json.dumps(fav.__dict__)
        return s


class Favorite(object):
    def __init__(self, name=None, url=None):
        self.name = name
        self.url = url

    def __repr__(self):
        return f"{self.__class__.__name__}( { self.__dict__ } )"


def get_backend(passphrase):
    return CryptedFileBackend(passphrase, JsonConv(), FAVORITES)


def load_favorites(passphrase):
    try:
        fb = get_backend(passphrase)
        favs = dict(map(lambda x: (x.name, x), fb.load()))
        return favs
    except Exception as ex:
        print(ex)
        print("defaulting empty fav list")
        return {}


def save_favorites(favs, passphrase):
    print_t("save_favorites", favs)
    fb = get_backend(passphrase)
    favs = favs.values()
    print_t("save_favorites", favs)
    fb.save(favs)
