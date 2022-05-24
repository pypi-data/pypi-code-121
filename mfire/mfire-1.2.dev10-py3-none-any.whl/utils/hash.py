import os
import hashlib


class MD5:
    """ MD5: class for hashing objects using the MD5
    algorithm.

    Args:
        obj (object): object to hash
        length (Optional[int]): length of the hash key retrieved.
            Defaults to 8.
    """

    def __init__(self, obj: object, length: int = 8):
        self.obj = obj
        self.length = length

    @property
    def obj(self) -> bytes:
        """ obj: given object stored as bytes
        """
        return self._obj

    @obj.setter
    def obj(self, obj: object):
        """ obj.setter: setter of the obj property
        """
        if isinstance(obj, str) and os.path.isfile(obj):
            with open(obj, "rb") as obj_file:
                self._obj = obj_file.read()
        else:
            self._obj = str(obj).encode()

    @property
    def hash(self):
        """ hash: computed hash of the given object self.obj.
        """
        return hashlib.md5(self.obj).hexdigest()[: self.length]  # nosec
