import datetime
import hmac
from Crypto.Hash import SHA512

from src.exceptions import IntegrityException
from src.parameters import timestamp2b
from src.parameters import require_bytes, require_timestamp_bytes


class SecureIntegrityEntity:
    """
    This is an implementation of an Integrity-based secure entity. Note, that it does not
    protect against lookups. The data in this entity is not encrypted. In addition,
    the identifier in the default is hashed without a salt. If you want the preimage resistance
    against hash database lookup attacks, you should provide a random sequence as an identifier.
    """

    @staticmethod
    def _check_hmac_key(hmac_key):
        if len(hmac_key) < 32:
            raise AttributeError("Length of HMACKey has to be at least 32.")

    @staticmethod
    def hash_identifier(identifier, salt=None):
        salt = require_bytes(salt) if salt is not None else b""
        identifier_hash = SHA512.new(
            salt + require_bytes(identifier), truncate="256"
        ).digest()
        return identifier_hash

    @classmethod
    def create(cls, hmac_key, expire_interval, identifier, *extra_data, salt=None):
        SecureIntegrityEntity._check_hmac_key(hmac_key)
        creation_timestamp = datetime.datetime.now()
        salt = require_bytes(salt) if salt is not None else b""
        expire_interval = require_timestamp_bytes(expire_interval)
        identifier_hash = SecureIntegrityEntity.hash_identifier(identifier, salt=salt)
        extra_data_hash = b"".join([SecureIntegrityEntity.hash_identifier(require_bytes(a)) for a in extra_data])
        mac = hmac.new(
            hmac_key,
            identifier_hash
            + salt
            + expire_interval
            + extra_data_hash
            + timestamp2b(creation_timestamp),
            digestmod="sha512",
        ).digest()
        return cls(creation_timestamp, identifier, identifier_hash, salt, mac)

    @classmethod
    def verify_mac(
        cls,
        hmac_key,
        creation_timestamp,
        expire_interval,
        identifier_hash,
        mac,
        *extra_data,
        salt=None,
    ):
        SecureIntegrityEntity._check_hmac_key(hmac_key)
        creation_timestamp = timestamp2b(creation_timestamp)
        expire_interval = require_timestamp_bytes(expire_interval)
        salt = require_bytes(salt) if salt is not None else b""
        extra_data_hash = b"".join([SecureIntegrityEntity.hash_identifier(require_bytes(a)) for a in extra_data])
        computed_mac = hmac.new(
            hmac_key,
            identifier_hash
            + salt
            + expire_interval
            + extra_data_hash
            + creation_timestamp,
            digestmod="sha512",
        ).digest()
        if not hmac.compare_digest(computed_mac, mac):
            raise IntegrityException("Invalid Integrity")

    def __init__(self, creation_timestamp, identifier, identifier_hash, salt, mac):
        self.creation_timestamp = creation_timestamp
        self.identifier = identifier
        self.identifier_hash = identifier_hash
        self.salt = salt
        self.mac = mac
