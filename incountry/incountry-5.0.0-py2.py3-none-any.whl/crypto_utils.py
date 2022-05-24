import hashlib
import json

from typing import Any, Dict, TypeVar

from pydantic import BaseModel

from .incountry_crypto import InCrypto
from .exceptions import StorageClientException

from .models import FindFilterOperators, Record, RecordFromServer, SERVICE_KEYS, SEARCH_KEYS, UTILITY_KEYS

TNormalize = TypeVar("TNormalize")
THashable = TypeVar("THashable", str, list, None)

KEYS_TO_HASH = SERVICE_KEYS + SEARCH_KEYS + UTILITY_KEYS
EXTRA_KEYS_TO_ENCRYPT = ["precommit_body"]

KEYS_TO_OMIT_ON_ENCRYPTION = ["created_at", "updated_at"]

RESERVED_KEYS_TO_SEND = ["body", "version", "is_encrypted"]


def validate_crypto(crypto: InCrypto) -> None:
    if not isinstance(crypto, InCrypto):
        raise StorageClientException(f"'crypto' argument should be an instance of InCrypto. Got {type(crypto)}")


def validate_is_string(value: str, arg_name: str) -> None:
    if not isinstance(value, str):
        raise StorageClientException(f"'{arg_name}' argument should be of type string. Got {type(value)}")


def is_json(data: str) -> bool:
    try:
        json.loads(data)
    except ValueError:
        return False
    return True


def hash(data: str) -> str:
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def normalize_key(key: TNormalize) -> TNormalize:
    if not isinstance(key, str):
        return key
    return key.lower()


def normalize_key_value(value: TNormalize) -> TNormalize:
    if value is None:
        return None
    if isinstance(value, list):
        return [normalize_key(x) for x in value]
    return normalize_key(value)


def get_salted_hash(value: str, salt: str) -> str:
    validate_is_string(value, "value")
    validate_is_string(salt, "salt")
    return hash(value + ":" + salt)


def hash_string_key_value(value: THashable, salt: str) -> THashable:
    if value is None:
        return None
    if isinstance(value, list):
        return [get_salted_hash(x, salt) for x in value]
    return get_salted_hash(value, salt)


def hash_object_record_keys(
    obj: Dict[str, Any],
    salt: str,
    hash_search_keys: bool = True,
    keys_to_hash: list = KEYS_TO_HASH,
    search_keys: list = SEARCH_KEYS,
) -> Dict[str, Any]:
    res = {}

    for key, value in obj.items():
        if key == FindFilterOperators.OR:
            res[key] = [
                hash_object_record_keys(
                    i,
                    salt=salt,
                    hash_search_keys=hash_search_keys,
                    keys_to_hash=keys_to_hash,
                    search_keys=search_keys,
                )
                for i in value
            ]
            continue

        should_hash_key = hash_search_keys or (not hash_search_keys and key not in search_keys)
        if (key not in keys_to_hash) or (value is None) or (not should_hash_key) or (FindFilterOperators.LIKE in value):
            res[key] = value
            continue

        if FindFilterOperators.NOT in value:
            res[key] = {FindFilterOperators.NOT: hash_string_key_value(value[FindFilterOperators.NOT], salt)}
        else:
            res[key] = hash_string_key_value(value, salt)

    return res


def normalize_object_record_keys(
    obj: Dict[str, Any],
    keys_to_normalize: list = KEYS_TO_HASH,
) -> Dict[str, Any]:
    res = {}

    for key, value in obj.items():
        if key not in keys_to_normalize or value is None:
            res[key] = value
            continue

        if FindFilterOperators.NOT in value:
            res[key] = {FindFilterOperators.NOT: normalize_key_value(value[FindFilterOperators.NOT])}
        else:
            res[key] = normalize_key_value(value)

    return res


def encrypt_record(
    crypto: InCrypto,
    record: Dict[str, Any],
    salt: str,
    keys_to_hash: list = KEYS_TO_HASH,
    keys_to_encrypt: list = EXTRA_KEYS_TO_ENCRYPT,
    search_keys: list = SEARCH_KEYS,
    hash_search_keys: bool = True,
    record_model: BaseModel = Record,
) -> Dict[str, Any]:
    validate_crypto(crypto)
    validate_is_string(salt, "salt")

    meta = {}
    for k in keys_to_hash:
        if k in record and record[k] is not None:
            meta[k] = record.get(k)

    res = hash_object_record_keys(
        record,
        salt,
        hash_search_keys=hash_search_keys,
        keys_to_hash=keys_to_hash,
        search_keys=search_keys,
    )

    body_to_enc = {"meta": meta, "payload": res.get("body", None)}

    (res["body"], res["version"], res["is_encrypted"]) = crypto.encrypt(json.dumps(body_to_enc))

    for key_to_encrypt in keys_to_encrypt:
        if key_to_encrypt in res and res[key_to_encrypt] is not None:
            (res[key_to_encrypt], *_) = crypto.encrypt(res[key_to_encrypt])

    return {
        key: value
        for key, value in res.items()
        if value is not None
        and key in record_model.__fields__
        and key not in KEYS_TO_OMIT_ON_ENCRYPTION
        or key in RESERVED_KEYS_TO_SEND
    }


def decrypt_record(
    crypto: InCrypto,
    record: dict,
    keys_to_hash: list = KEYS_TO_HASH,
    keys_to_decrypt: list = EXTRA_KEYS_TO_ENCRYPT,
    record_model: BaseModel = RecordFromServer,
) -> Dict[str, Any]:
    validate_crypto(crypto)
    res = dict(record)

    if res.get("body"):
        res["body"] = crypto.decrypt(res["body"], res["version"])
        for key_to_decrypt in keys_to_decrypt:
            if key_to_decrypt in res and res[key_to_decrypt] is not None:
                res[key_to_decrypt] = crypto.decrypt(res[key_to_decrypt], res["version"])
        if is_json(res["body"]):
            body = json.loads(res["body"])
            if "payload" in body:
                res["body"] = body.get("payload")
            else:
                res["body"] = None
            for k in keys_to_hash:
                if record.get(k) and k in body["meta"]:
                    res[k] = body["meta"][k]
            if body["meta"].get("key", None):
                res["record_key"] = body["meta"].get("key")

    return {key: value for key, value in res.items() if key in record_model.__fields__ or key in RESERVED_KEYS_TO_SEND}
