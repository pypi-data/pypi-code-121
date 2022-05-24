import os
import time
import random
import string
import binascii
import hashlib
import uuid
import secrets

# from cryptography.fernet import Fernet


class AbstractMethodError(NotImplementedError):
    pass


#


class Salt(object):
    """the generic container class"""

    def __init__(self, salt, gen):
        self._gen = gen
        self._salt = salt

    def get(self):
        """get the internal salt object"""
        return self._salt

    def tobytes(self):
        return self._gen.tobytes(self._salt)

    def __repr__(self):
        return str(self._salt)


class SaltGen(object):
    """the abstract generator class"""

    def create(self):
        raise AbstractMethodError()

    def tobytes(self):
        raise AbstractMethodError()

    def frombytes(self, b):
        raise AbstractMethodError()


#


class UuidSalt(SaltGen):
    def create(self):
        return Salt(uuid.uuid4(), self)

    def tobytes(self, salt):
        return salt.bytes

    def frombytes(self, b):
        return Salt(uuid.UUID(bytes=b), self)


#


class NumSalt(SaltGen):
    def create(self):
        return Salt(self.rand(), self)

    def rand(self):
        raise AbstractMethodError()


class FloatSalt(NumSalt):
    def rand(self):
        """creates a random salt between 0.0 and 1.0"""
        return random.random()

    def tobytes(self, salt):
        return salt.hex().encode()

    def frombytes(self, b):
        return Salt(float.fromhex(b.decode()), self)


class IntSalt(NumSalt):

    ORDER = "big"

    def __init__(self, minval=0, maxval=100, signed=True):
        self._min = minval
        self._max = maxval
        self._signed = signed

    def rand(self):
        return random.randint(self._min, self._max)

    def tobytes(self, salt):
        return salt.to_bytes(8, byteorder=self.ORDER, signed=self._signed)

    def frombytes(self, b):
        return Salt(int.from_bytes(b, byteorder=self.ORDER, signed=self._signed), self)


#


class TimeSalt(FloatSalt):
    """creates the salt directly from the current utc time"""

    def rand(self):
        return time.time()


class TimeNanoSalt(IntSalt):
    """creates the salt directly from the current nano time"""

    def rand(self):
        return time.time_ns()


#


class HashGen(object):
    def __init__(self):
        self._hash = self._create()
        if self._hash == None:
            raise Exception("hash is null")

    def _create(self):
        raise AbstractMethodError()

    def update(self, bytes_):
        self._hash.update(bytes_)
        return self

    def digest(self):
        return self._hash.digest()

    def base64_digest(self):
        return binascii.b2a_base64(self.digest())


#


class Hash256(HashGen):
    def _create(self):
        return hashlib.sha256()


class Hash512(HashGen):
    def _create(self):
        return hashlib.sha512()


# https://docs.python.org/3/library/hashlib.html#hashlib.blake2b


class HashBlake2b(HashGen):
    def __init__(self, key=None, salt=None, person=None):
        self._key = key if key else b""
        self._salt = salt if salt else b""
        self.person = person if person else b""
        super().__init__()

    def _create(self):
        return hashlib.blake2b(key=self._key, salt=self._salt, person=self.person)


# https://docs.python.org/3/library/string.html

# e.g.
# string.ascii_letters, string.punctuation and some unusual removed...

# string.ascii_letters -> 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
# string.punctuation -> '!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~'


predef_alphabet = string.ascii_lowercase
predef_alphabet += string.ascii_uppercase
predef_alphabet += string.digits
predef_alphabet += "!#$%&()*+-?@"  # some removed...

# traditional


class PassGen(object):
    def __init__(self, baseset=None, passlen=8, shuffled=True):
        self.baseset = list(set(baseset if baseset else predef_alphabet))
        self.passlen = passlen
        self.shuffled = shuffled
        if self.shuffled:
            random.shuffle(self.baseset)

    def create(self):
        slt = IntSalt(0, len(self.baseset) - 1)
        pw = [self.baseset[slt.rand()] for x in range(self.passlen)]
        pw = "".join(pw)
        return pw


# https://docs.python.org/3/library/secrets.html#recipes-and-best-practices


class SecretGen(PassGen):
    def create(self):
        pw = [secrets.choice(self.baseset) for i in range(self.passlen)]
        pw = "".join(pw)
        return pw


# todo
# https://en.wikipedia.org/wiki/Password_strength
# https://www.uic.edu/apps/strong-password/
#
