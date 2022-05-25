import json
import os
import datetime
import threading
import logging
from typing import Union

from ipfabric_httpx_auth.errors import AuthenticationFailed

logger = logging.getLogger(__name__)


def _is_expired(expiry: float, early_expiry: float) -> bool:
    return (
        datetime.datetime.utcfromtimestamp(expiry - early_expiry)
        < datetime.datetime.utcnow()
    )


class TokenMemoryCache:
    """
    Class to manage tokens using memory storage.
    """

    def __init__(self):
        self.tokens = {}
        self.forbid_concurrent_cache_access = threading.Lock()
        self.forbid_concurrent_missing_token_function_call = threading.Lock()

    def _add_token(self, key: str, token: str, refresh: str, expiry: int):
        """
        Set the bearer token and save it
        :param key: key identifier of the token
        :param token: value
        :param expiry: UTC timestamp of expiry
        """
        with self.forbid_concurrent_cache_access:
            self.tokens[key] = token, refresh, expiry
            self._save_tokens()
            logger.debug(
                f'Inserting token expiring on {datetime.datetime.utcfromtimestamp(expiry)} (UTC) with "{key}" key: {token}'
            )

    def get_token(
        self,
        key: str,
        *,
        early_expiry: float = 30.0,
        on_missing_token=None,
    ) -> str:
        """
        Return the bearer token.
        :param key: key identifier of the token
        :param early_expiry: As the time between the token extraction from cache and the token reception on server side
        might not higher than one second, on slow networks, token might be expired when received by the actual server,
        even if still valid when fetched.
        This is the number of seconds to subtract to the actual token expiry. Token will be considered as
        expired 30 seconds before real expiry by default.
        :param on_missing_token: function to call when token is expired or missing (returning token and expiry tuple)
        :return: the token
        :raise AuthenticationFailed: in case token cannot be retrieved.
        """
        logger.debug(f'Retrieving token with "{key}" key.')
        bearer, refresh = None, None
        with self.forbid_concurrent_cache_access:
            self._load_tokens()
            if key in self.tokens:
                bearer, refresh, expiry = self.tokens[key]
                if _is_expired(expiry, early_expiry):
                    logger.debug(f'Authentication token with "{key}" key is expired.')
                    del self.tokens[key]
                else:
                    logger.debug(
                        f"Using already received authentication, will expire on {datetime.datetime.utcfromtimestamp(expiry)} (UTC)."
                    )
                    return bearer

        logger.debug("Token cannot be found in cache or expired.")
        if on_missing_token is not None:
            with self.forbid_concurrent_missing_token_function_call:
                new_token = on_missing_token(bearer, refresh)
                state, token, refresh, expires_in = new_token
                self._add_token(state, token, refresh, expires_in)
                if key != state:
                    logger.warning(
                        f"Using a token received on another key than expected. Expecting {key} but was {state}."
                    )
            with self.forbid_concurrent_cache_access:
                if state in self.tokens:
                    bearer, refresh, expiry = self.tokens[state]
                    logger.debug(
                        f"Using newly received authentication, expiring on {datetime.datetime.utcfromtimestamp(expiry)} (UTC)."
                    )
                    return bearer

        logger.debug(
            f"User was not authenticated: key {key} cannot be found in {self.tokens}."
        )
        raise AuthenticationFailed()

    def clear(self):
        """Remove tokens from the cache."""
        with self.forbid_concurrent_cache_access:
            logger.debug("Clearing token cache.")
            self.tokens = {}
            self._clear()

    def _save_tokens(self):
        pass

    def _load_tokens(self):
        pass

    def _clear(self):
        pass


class JsonTokenFileCache(TokenMemoryCache):
    """
    Class to manage tokens using a cache file.
    """

    def __init__(self, tokens_path: str):
        TokenMemoryCache.__init__(self)
        self.tokens_path = tokens_path
        self.last_save_time = 0
        self._load_tokens()

    def _clear(self):
        self.last_save_time = 0
        try:
            os.remove(self.tokens_path)
        except:
            logger.debug("Cannot remove tokens file.")

    def _save_tokens(self):
        try:
            with open(self.tokens_path, "w") as tokens_cache_file:
                json.dump(self.tokens, tokens_cache_file)
            self.last_save_time = os.path.getmtime(self.tokens_path)
        except:
            logger.exception("Cannot save tokens.")

    def _load_tokens(self):
        if not os.path.exists(self.tokens_path):
            logger.debug("No token loaded. Token cache does not exists.")
            return
        try:
            last_modification_time = os.path.getmtime(self.tokens_path)
            if last_modification_time > self.last_save_time:
                self.last_save_time = last_modification_time
                with open(self.tokens_path, "r") as tokens_cache_file:
                    self.tokens = json.load(tokens_cache_file)
        except:
            logger.exception("Cannot load tokens.")
