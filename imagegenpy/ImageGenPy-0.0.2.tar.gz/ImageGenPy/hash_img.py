import hashlib


def hash_img(fp):
    hash256 = hashlib.sha256()
    with open(fp, "rb") as f:
        for block in iter(lambda: f.read(4096), b""):
            hash256.update(block)
    return hash256.hexdigest()
