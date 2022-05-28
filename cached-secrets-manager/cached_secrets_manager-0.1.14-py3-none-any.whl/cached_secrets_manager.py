import json
import logging

from botocore.exceptions import NoCredentialsError
from time import time
from typing import Dict

from cached_secrets_manager.cache import Cache
from cached_secrets_manager.no_secrets_found_error import NoSecretsFoundError
from cached_secrets_manager.secrets_manager import SecretsManager


class CachedSecretsManager:
    _VALID_UNTIL_KEY = 'valid_until'

    _LOGGER = logging.getLogger()
    _LOGGER.setLevel(logging.INFO)

    def __init__(self, cache_path: str, secret_name: str, region_name: str):
        self._secrets_cache: Cache = Cache(cache_path)
        self._secrets_manager: SecretsManager = SecretsManager(secret_name, region_name)

    def get(self, minutes_to_live: int = 60) -> Dict:
        """
        This method tries to retrieve a secret from cache first and falls back to secret manager otherwise.
        :return: secret of throws exception
        """
        try:
            secrets: Dict = self._get_secrets_from_cache()
            current_time = int(round(time()))
            valid_until = int(secrets.get(self._VALID_UNTIL_KEY, 0))
            if current_time > valid_until:
                self._LOGGER.info(f"Cache needs to be invalidated (Current time: {current_time}, valid until: {valid_until}).")
                self.reset_cache()
                raise NoSecretsFoundError
        except NoSecretsFoundError as error:
            self._LOGGER.info(f"No secrets found in cache {self._secrets_cache.cache_path}. Trying through secrets manager.")
            secrets = self._get_secrets_from_secrets_manager()
            valid_until = int(round(time())) + minutes_to_live*60
            secrets[self._VALID_UNTIL_KEY] = valid_until
            self._set_secrets_in_cache(secrets)
        secrets.pop(self._VALID_UNTIL_KEY, None)
        return secrets

    def set(self, secrets: Dict):
        self._secrets_manager.update(json.dumps(secrets))
        self.reset_cache()

    def reset_cache(self):
        self._secrets_cache.delete_all()

    def _get_secrets_from_cache(self):
        secrets = self._secrets_cache.get_all()
        if not secrets:
            raise NoSecretsFoundError("No secrets found in cache.")
        for secret_value in secrets.values():
            if not secret_value:
                raise NoSecretsFoundError("No secrets found in cache.")
        self._LOGGER.info('Found secrets in cache.')
        return secrets

    def _set_secrets_in_cache(self, secrets):
        self._secrets_cache.set_all(secrets)
        self._LOGGER.info('Set secrets in cache.')

    def _get_secrets_from_secrets_manager(self):
        self._LOGGER.info('Retrieving secrets from secrets manager.')
        try:
            secrets = json.loads(self._secrets_manager.get())
        except NoCredentialsError:
            raise NoSecretsFoundError(f"Secret missing in secrets manager.")
        if not secrets:
            raise NoSecretsFoundError(f"No secrets found in secret.")
        for secret_value in secrets.values():
            if not secret_value:
                raise NoSecretsFoundError(f"Incomplete secrets found through secrets manager.")
        return secrets
