import binascii


class KeyConv(object):
    def convert(self, passphrase):
        raise NotImplementedError


class KeyNoConv(KeyConv):
    def convert(self, passphrase):
        return passphrase


class KeyBase64Conv(KeyConv):
    def convert(self, passphrase):
        return binascii.b2a_base64(passphrase.encode()).decode()
