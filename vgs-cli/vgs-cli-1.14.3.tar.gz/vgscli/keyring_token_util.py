import jwt
import keyring
from cryptography.fernet import Fernet
from keyring.errors import PasswordDeleteError

from vgscli.errors import TokenNotValidError
from vgscli.file_token_util import FileTokenUtil
from vgscli.utils import expired


class KeyringTokenUtil:
    SERVICE_NAME = 'vgs-cli'

    ACCESS_TOKEN_KEY = 'access_token'
    REFRESH_TOKEN_KEY = 'refresh_token'
    ENCRYPT_TOKEN_SECRET_KEY = 'vgs_encrypt_secret_key'

    access_token_file = FileTokenUtil('vgs_access_token')
    refresh_token_file = FileTokenUtil('vgs_refresh_token')

    def put_encryption_secret(self, secret):
        keyring.set_password(self.SERVICE_NAME, self.ENCRYPT_TOKEN_SECRET_KEY, secret)

    def get_encryption_secret(self):
        return keyring.get_credential(self.SERVICE_NAME, self.ENCRYPT_TOKEN_SECRET_KEY)

    def remove_encryption_secret(self):
        try:
            keyring.delete_password(self.SERVICE_NAME, self.ENCRYPT_TOKEN_SECRET_KEY)
        except PasswordDeleteError:
            pass

    def tokens_exist(self):
        return self.access_token_file.exists and self.refresh_token_file.exists

    def clear_tokens(self):
        self.delete_access_token()
        self.delete_refresh_token()

    def validate_access_token(self):
        if self.get_access_token():
            token_json = jwt.decode(self.get_access_token(), verify=False)
            return not expired(token_json['exp'])
        else:
            raise TokenNotValidError("Access token not found")

    def validate_refresh_token(self):
        if self.get_refresh_token():
            token_json = jwt.decode(self.get_refresh_token(), verify=False)
            if expired(token_json['exp']):
                raise TokenNotValidError("Refresh token expired")
        else:
            raise TokenNotValidError("Refresh token not found")

    def is_access_token_valid(self) -> bool:
        try:
            return self.validate_access_token()
        except TokenNotValidError:
            return False

    def is_access_token_azp_changed(self, azp) -> bool:
        return jwt.decode(self.get_access_token(), verify=False).get('azp') != azp

    def put_tokens(self, response):
        key = Fernet.generate_key()
        cipher = Fernet(key)
        self.remove_encryption_secret()
        self.put_encryption_secret(str(key, 'utf-8'))
        self.access_token_file.write_token(str(cipher.encrypt(response[self.ACCESS_TOKEN_KEY].encode()), 'utf-8'))

        # https://datatracker.ietf.org/doc/html/rfc6749#section-4.4.3
        if self.REFRESH_TOKEN_KEY in response:
            self.refresh_token_file.write_token(str(cipher.encrypt(response[self.REFRESH_TOKEN_KEY].encode()), 'utf-8'))

    def put_access_token(self, token):
        self.access_token_file.write_token(str(self.fernet.encrypt(token.encode()), 'utf-8'))

    def get_access_token(self):
        try:
            return str(self.fernet.decrypt(self.access_token_file.read_token().encode()), 'utf-8')
        except FileNotFoundError:
            raise TokenNotValidError("Access token not found")

    def delete_access_token(self):
        self.access_token_file.remove_token()

    def put_refresh_token(self, token):
        self.refresh_token_file.write_token(str(self.fernet.encrypt(token.encode()), 'utf-8'))

    def get_refresh_token(self):
        try:
            return str(self.fernet.decrypt(self.refresh_token_file.read_token().encode()), 'utf-8')
        except FileNotFoundError:
            raise TokenNotValidError("Refresh token not found")

    def delete_refresh_token(self):
        self.refresh_token_file.remove_token()

    @property
    def fernet(self):
        secret = self.get_encryption_secret()
        if not secret:
            raise FileNotFoundError("Can't find secret in keystore")

        return Fernet(secret.password.encode())
