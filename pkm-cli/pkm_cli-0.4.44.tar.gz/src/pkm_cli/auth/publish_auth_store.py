import base64
from pathlib import Path
from typing import Dict, Optional, Any

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from pkm.api.pkm import pkm
from pkm.config import toml
from pkm.utils.files import mkdir
from pkm_cli.display.display import Display

_PUBLISH_AUTH_CONFIG_PATH = "etc/pkm-cli/repositories-publish-auth.toml.enc"
_PA_SALT = b'\xc5U\xed\xd1\xe9\x89\x10\xe07\x86\xf8&a\xf6\xb8\xc7'
_PA_MAGIC = "REPOSITORIES_PUBLISH_AUTH"


def _make_cipher(password: str) -> Fernet:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(), length=32, salt=_PA_SALT, iterations=100_000, backend=default_backend())
    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    return Fernet(key)


class PublishAuthenticationStore:

    def __init__(self, configuration_path: Optional[Path] = None):
        self.configuration_path = configuration_path or (pkm.home / _PUBLISH_AUTH_CONFIG_PATH)
        self._unlocked_configuration: Optional[Dict[str, Any]] = None
        self._cipher: Optional[Fernet] = None

    def unlock(self, password: Optional[str] = None):
        configuration_path = self.configuration_path
        if not configuration_path.exists():
            if not password:
                while True:
                    password = Display.ask_password(
                        "First time use of authentication store, please provide password to use")
                    password2 = Display.ask_password("Please repeat the password")
                    if password != password2:
                        Display.print("Passwords did not match, retrying process.")
                        continue
                    break
            self._cipher = _make_cipher(password)
            self._unlocked_configuration = {}
        else:
            if not password:
                password = Display.ask_password("Please provide the authentication store password")
            self._cipher = _make_cipher(password)
            try:
                configuration_str = self._cipher.decrypt(configuration_path.read_bytes()).decode()
            except InvalidToken:
                configuration_str = ""
            if not configuration_str.startswith(_PA_MAGIC):
                raise IOError("Wrong password provided")

            configuration, _ = toml.loads(configuration_str[len(_PA_MAGIC):])
            self._unlocked_configuration = configuration

    def is_unlocked(self):
        return self._cipher is not None

    def _ensure_unlocked(self):
        if not self.is_unlocked():
            self.unlock()

    def is_configuration_exists(self) -> bool:
        return self.configuration_path.exists()

    def auth_args_for(self, repository_name: str) -> Optional[Dict[str, str]]:
        self._ensure_unlocked()
        return self._unlocked_configuration.get(repository_name)

    def _save(self):
        configuration_path = self.configuration_path
        mkdir(configuration_path.parent)
        configuration_str = _PA_MAGIC + toml.dumps(self._unlocked_configuration)
        configuration_path.write_bytes(self._cipher.encrypt(configuration_str.encode()))

    def add_auth_args(self, repository_name: str, args: Dict[str, str]):
        self._ensure_unlocked()
        self._unlocked_configuration[repository_name] = args
        self._save()

    def rm_auth_args(self, repository_name: str):
        self._ensure_unlocked()
        del self._unlocked_configuration[repository_name]
        self._save()
