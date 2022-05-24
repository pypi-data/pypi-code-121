import os
import subprocess
import uuid
from hashlib import sha256, md5


def get_checksum(path):

    if not os.path.isfile(path) or not os.path.exists(path):
        return None

    checksum = subprocess.check_output("/usr/bin/sha256sum {}".format(path), shell=True)
    #'ffd4d29ee4019150cc308e46004d2f17105899983e7fb4ca7c27ffe981fb82d4  deploy.json\n'
    checksum = checksum.decode("utf-8").strip()
    checksum = checksum.split(" ")[0]
    return checksum


def get_file_size(path):

    if not os.path.isfile(path) or not os.path.exists(path):
        return 0

    statinfo = os.stat(path)
    return statinfo.st_size


def get_consistent_uuid(text):
    # https://stackoverflow.com/questions/41186818/how-to-generate-a-random-uuid-which-is-reproducible-with-a-seed-in-python

    for n in range(0, 10):
        m = md5()
        m.update((text + " " * n).encode("utf-8"))
        new_uuid = uuid.UUID(m.hexdigest())
        if str(new_uuid)[0] == "0":
            continue
        else:
            break

    assert str(new_uuid)[0] != "0"
    return new_uuid
