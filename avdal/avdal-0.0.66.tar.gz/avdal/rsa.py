import os
import stat
import secrets
import cryptography
from glob import glob
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKeyWithSerialization, RSAPublicKeyWithSerialization


class InvalidKeyID(Exception):
    pass


class InvalidSignature(Exception):
    pass


class InvalidCiphertext(Exception):
    pass


class Store:
    KID_SIZE = 16
    KEY_SIZE = 2048
    PUBLIC_EXPONENT = 65537
    KEY_FILE_MODE = stat.S_IRUSR | stat.S_IRGRP

    def __init__(self, keys_root: str, storage_key: bytes = None):
        self.keys_root = os.path.expanduser(keys_root)
        self.priv_root = os.path.join(self.keys_root, "priv")

        if not os.path.isdir(self.priv_root):
            os.makedirs(self.priv_root)

        self._kids = set()
        self._private_keys = {}
        self._public_keys = {}

        self.storage_key = storage_key or None

        self._load_keys()

    def _add_key(self, kid, priv_key):
        self._kids.add(kid)
        self._private_keys[kid] = priv_key
        self._public_keys[kid] = priv_key.public_key()

    def _load_keys(self):
        pattern = os.path.join(self.priv_root, "*.pem")
        for filename in glob(pattern):
            _, file = os.path.split(filename)
            kid, _ = os.path.splitext(file)

            priv_key = self._load_key(filename)
            self._add_key(kid, priv_key)

    def _load_key(self, filename) -> RSAPrivateKeyWithSerialization:
        with open(filename, "rb") as f:
            private_key = serialization.load_pem_private_key(
                f.read(),
                password=self.storage_key,
            )

            return private_key

    def _key_filename(self, kid: str) -> str:
        return os.path.join(self.priv_root, f"{kid}.pem")

    def _save_file(self, filename: str, content: bytes):
        if os.path.exists(filename):
            raise FileExistsError(filename)

        with open(filename, "wb") as f:
            f.write(content)

        os.chmod(filename, Store.KEY_FILE_MODE)

    def _save_key(self, kid, private_key: RSAPrivateKeyWithSerialization):
        if not self.storage_key:
            enc_alg = serialization.NoEncryption()
        else:
            enc_alg = serialization.BestAvailableEncryption(self.storage_key)

        pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=enc_alg
        )

        self._save_file(self._key_filename(kid), pem)

    @property
    def kids(self) -> set:
        return self._kids

    def get_public_key(self, kid: str) -> RSAPublicKeyWithSerialization:
        if not kid in self._public_keys:
            raise InvalidKeyID(kid)

        return self._public_keys[kid]

    def get_private_key(self, kid: str) -> RSAPrivateKeyWithSerialization:
        if not kid in self._private_keys:
            raise InvalidKeyID(kid)

        return self._private_keys[kid]

    def generate_key(self, key_size=KEY_SIZE) -> str:
        private_key = rsa.generate_private_key(
            public_exponent=Store.PUBLIC_EXPONENT,
            key_size=key_size,
        )

        kid = secrets.token_bytes(Store.KID_SIZE).hex()
        assert kid not in self._private_keys

        self._save_key(kid, private_key)
        self._add_key(kid, private_key)

        return kid

    def well_known(self):
        def pem(key):
            decoded = key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            ).decode()

            return '\n'.join(decoded.splitlines()[1:-1])

        keys = [{
            "kid": k,
            "public_key": pem(v),
            "size": v.key_size
        }
            for k, v in self._public_keys.items()]

        return {
            "keys": keys
        }


class Signer:
    def __init__(self, store: Store):
        self.store = store

    def sign(self, kid: str, data: bytes) -> bytes:
        private_key = self.store.get_private_key(kid)
        sig = private_key.sign(
            data,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )

        return sig

    def verify(self, kid: str, signature: bytes, data: bytes):
        public_key = self.store.get_public_key(kid)

        try:
            public_key.verify(
                signature,
                data,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )

        except cryptography.exceptions.InvalidSignature as e:
            raise InvalidSignature("invalid signature")


class Encryptor:
    def __init__(self, store: Store):
        self.store = store

    def encrypt(self, kid: str, data: bytes) -> bytes:
        public_key = self.store.get_public_key(kid)

        return public_key.encrypt(
            data,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

    def decrypt(self, kid: str, data: bytes) -> bytes:
        private_key = self.store.get_private_key(kid)

        try:
            return private_key.decrypt(
                data,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )

        except ValueError as e:
            raise InvalidCiphertext(e)
