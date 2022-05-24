import base64
from Crypto import Random
from Crypto.Cipher import AES
from simple_salesforce import Salesforce


class SalesForce(object):
    class Auth:
        def __init__(self, sf_username, sf_pwd, sf_security_token):
            self.sf_username = sf_username
            self.sf_pwd = sf_pwd
            self.sf_security_token = sf_security_token

        def salesforce_login(self):
            try:
                sf = Salesforce(
                    username=self.sf_username,
                    password=self.sf_pwd,
                    security_token=self.sf_security_token)

            except ValueError as e:
                print(e)

            return sf


class SentryBay(object):
    class EncodeData:
        def __init__(self, sb_key, sb_data):
            self.sb_key = sb_key
            self.sb_data = sb_data

        def encrypt_data(self):
            data = self.sb_data + self.padding()

            iv_created = Random.new().read(AES.block_size)

            cipher = AES.new(self.sb_key.encode('utf-8'), AES.MODE_CBC, iv_created)

            encrypted = cipher.encrypt(str.encode(data))

            result = base64.b64encode(iv_created).decode('utf-8'), base64.b64encode(encrypted).decode('utf-8')

            return result

        def padding(self):
            try:
                size = len(self.sb_data)

                i = int(size / AES.block_size)

                j = AES.block_size * i

                if j < size:
                    j += AES.block_size

                return "".ljust(j - size, '\x00')

            except Exception as e:
                raise Exception(str(e))
