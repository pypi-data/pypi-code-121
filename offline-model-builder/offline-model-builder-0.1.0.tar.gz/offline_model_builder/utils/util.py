import base64


def encode_string(
        text: str
) -> str:
    """Hash plain string to base 64 text string
    :param text: string text
    :return: string encode text
    """
    return base64.b64encode(text.encode('utf-8')).decode("utf-8")


def decode_string(
        hash_str: str
) -> str:
    """Un hash text string to plain text string
    :param hash_str: base 64 encode string
    :return: plain text string
    """
    return base64.b64decode(hash_str).decode("utf-8")
