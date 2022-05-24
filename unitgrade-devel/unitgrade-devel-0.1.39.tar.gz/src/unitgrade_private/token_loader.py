import os
import zipfile
import io


def unpack_sources_from_token(token_file, destination=None):
    from unitgrade_private import load_token

    rs, _ = load_token(token_file)
    if destination is None:
        destination = os.path.dirname(token_file)
    destination = os.path.normpath(destination)

    for k, data in rs['sources'].items():
        out = destination + "/" + os.path.basename(token_file)[:-6] + f"_{k}/"
        if not os.path.exists(out):
            zf = zipfile.ZipFile(io.BytesIO(data['zipfile']))
            zf.extractall(out)
