"""
Environment variables
"""
import os

BREVETTI_AI_USER = "BREVETTI_AI_USER"
"""Default user for 'PlatformAPI'"""

BREVETTI_AI_PW = "BREVETTI_AI_PW"
"""Password for 'PlatformAPI' user"""

BREVETTI_AI_CACHE = "BREVETTI_AI_CACHE"
"""Default cache location"""

BREVETTI_AI_CACHE_MAX_USAGE = "BREVETTI_AI_CACHE_MAX_USAGE"
"""Maximum percentage of disk to fill with cached remote data"""

def get_max_cache_usage(default=0.8):
    """Retrieve max cache usage percentage"""
    return float(os.getenv(BREVETTI_AI_CACHE_MAX_USAGE, default))
