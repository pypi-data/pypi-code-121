import encodings
import os
import pkgutil


class BaseEncoding(object):

    def __init__(self):
        pass

    def all_encodings(self):
        """

        :return:
        """
        modnames = set([modname for importer, modname, ispkg in pkgutil.walk_packages(
            path=[os.path.dirname(encodings.__file__)], prefix='')])
        aliases = set(encodings.aliases.aliases.values())
        return modnames.union(aliases)

    def is_encoding(self,text=b'\x96'):
        for enc in self.all_encodings():
            try:
                msg = text.decode(enc)
            except Exception:
                continue
            print('Decoding {t} with {enc} is {m}'.format(t=text, enc=enc, m=msg))

# BaseEncoding().is_encoding(b'\0\x93')