class MD5:
    @staticmethod
    def encrypt(string: str):
        import hashlib
        md5 = hashlib.md5(string.encode('utf-8'))
        encrypt_string = md5.hexdigest()
        return encrypt_string
