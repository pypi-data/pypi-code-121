class SHA256:
    @staticmethod
    def encrypt(string: str):
        import hashlib
        sha = hashlib.sha256(string.encode('utf-8'))
        encrypt_string = sha.hexdigest()
        return encrypt_string
