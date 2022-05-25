import hashlib

def sha1(x: str) -> str:
    hash_obj = hashlib.sha1(x.encode('utf-8'))
    return hash_obj.hexdigest()