from django.conf import settings


def get_setting_or_default(name: str, default):
    """Return setting if defined and has same type as default. Else return default."""
    if hasattr(settings, name):
        value = getattr(settings, name)
        return value if type(value) is type(default) else default
    else:
        return default


EVE_AUTH_LOGIN_SCOPES = get_setting_or_default("EVE_AUTH_LOGIN_SCOPES", [])
"""List of ESI scope names to be requested with every login.

Example for requesting two structure scopes: ``[‘esi-universe.read_structures.v1’,
‘esi-search.search_structures.v1’]``.

Do not request any scopes just provide an empty array: ``[]``
"""

EVE_AUTH_USER_ICON_DEFAULT_SIZE = get_setting_or_default(
    "EVE_AUTH_USER_ICON_DEFAULT_SIZE", 24
)
"""Default size of user icons in pixel."""
