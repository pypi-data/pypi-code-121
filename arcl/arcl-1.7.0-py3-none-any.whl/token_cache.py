from msal_extensions import (
    build_encrypted_persistence,
    FilePersistence,
    PersistedTokenCache,
)

from arcl.config import get_token_path


def build_persistence(location, fallback_to_plaintext=False):
    """Build a suitable persistence instance based your current OS"""
    try:
        return build_encrypted_persistence(location)
    except:
        if not fallback_to_plaintext:
            raise
        return FilePersistence(location)


def get_token_cache(env):
    persistence = build_persistence(get_token_path(env), True)
    token_cache = PersistedTokenCache(persistence)
    return token_cache
