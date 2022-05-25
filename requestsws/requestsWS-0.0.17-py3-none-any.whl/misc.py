import gzip
import zlib

def decompress(message, encryption):
    if type(encryption) == str:
        if encryption.lower() == "zlib":
            _zlib = zlib.decompressobj()
            return _zlib.decompress(message).decode("utf-8")
        elif encryption.lower() == "gzip":
            return str(gzip.decompress(message), encoding="utf8")
    elif encryption == None:
        return message
    else:
        exit(f"requestsWS | Error: {encryption} is not supported yet, if you would like for it to be supported please open an issue on Github")