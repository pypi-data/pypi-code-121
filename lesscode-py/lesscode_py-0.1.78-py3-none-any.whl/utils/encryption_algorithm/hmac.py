import hmac


class HMAC:
    @staticmethod
    def encrypt(string: str, key: str, digestmod="MD5", encoding='utf-8', flag=True):
        h = hmac.new(key.encode(encoding), string.encode(encoding), digestmod=digestmod)
        if flag:
            encrypt_string = h.hexdigest()
        else:
            encrypt_string = h.digest()
        return encrypt_string
