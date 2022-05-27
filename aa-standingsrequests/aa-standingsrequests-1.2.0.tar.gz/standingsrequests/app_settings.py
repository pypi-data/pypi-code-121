from django.conf import settings

from app_utils.django import clean_setting

from .constants import OperationMode

# switch to enable/disable ability to request standings for corporations
SR_CORPORATIONS_ENABLED = clean_setting("SR_CORPORATIONS_ENABLED", True)

# Number of seconds to cache heavy pages like character and groups standing
SR_PAGE_CACHE_SECONDS = clean_setting("SR_PAGE_CACHE_SECONDS", 600)

# whether ESI requests have a timeout
SR_ESI_TIMEOUT_ENABLED = clean_setting("SR_ESI_TIMEOUT_ENABLED", True)

# Send notifications to users about the results of standings requests
SR_NOTIFICATIONS_ENABLED = clean_setting("SR_NOTIFICATIONS_ENABLED", True)

# Automatically sync standing for alt characters known to Auth
# that have standing in-game
SR_SYNC_BLUE_ALTS_ENABLED = clean_setting("SR_SYNC_BLUE_ALTS_ENABLED", True)

# Select the entity type of your standings master
SR_OPERATION_MODE = clean_setting(
    "SR_OPERATION_MODE", str(OperationMode.ALLIANCE), choices=OperationMode.values
)

# This is a map, where the key is the State the user is in
# and the value is a list of required scopes to check
SR_REQUIRED_SCOPES = getattr(
    settings,
    "SR_REQUIRED_SCOPES",
    {"Member": ["publicData"], "Blue": [], "": []},  # no state
)

# Standing data will be considered stale and removed from the local
# database after the configured hours.
# The latest standings data will never be purged, no matter how old it is
SR_STANDINGS_STALE_HOURS = clean_setting("SR_STANDINGS_STALE_HOURS", 48)

# Max hours to wait for a standing to be effective after being marked actioned
# Non effective standing requests will be reset when this timeout expires.
SR_STANDING_TIMEOUT_HOURS = clean_setting("SR_STANDING_TIMEOUT_HOURS", 24)

# id of character to use for updating alliance contacts - needs to be set
STANDINGS_API_CHARID = clean_setting("STANDINGS_API_CHARID", None, required_type=int)

# charaters belonging to these alliances are considered to be "in organization"
STR_ALLIANCE_IDS = clean_setting("STR_ALLIANCE_IDS", [], required_type=list)

# charaters belonging to these corporations are considered to be "in organization"
STR_CORP_IDS = clean_setting("STR_CORP_IDS", [], required_type=list)
