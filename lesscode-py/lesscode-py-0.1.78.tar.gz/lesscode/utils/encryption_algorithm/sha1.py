class SHA1:
    @staticmethod
    def encrypt(string: str):
        import hashlib
        sha = hashlib.sha1(string.encode('utf-8'))
        encrypt_string = sha.hexdigest()
        return encrypt_string
