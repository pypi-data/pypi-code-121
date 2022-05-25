import base64


def encode(source, encoding='gbk'):
    source_bytes = source.encode(encoding)

    base64_bytes = base64.b64encode(source_bytes)
    base64_string = base64_bytes.decode(encoding)
    base64_string = base64_string.replace('=', '_')
    return base64_string


def decode(source, encoding='gbk'):
    source = source.replace('_', '=')
    base64_bytes = source.encode(encoding)

    string_bytes = base64.b64decode(base64_bytes)
    string = string_bytes.decode(encoding)
    return string

