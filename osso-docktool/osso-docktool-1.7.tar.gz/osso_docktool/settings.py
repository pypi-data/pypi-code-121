import sys

__author__ = 'osso'

DEBUG = False

LABELPRINTER_BASE_URL = 'https://labelprinter.example.com/'
LABELPRINTER_LOGIN_URL = 'https://labelprinter.example.com/api-auth/login/'
LABELPRINTER_AUTH_TOKEN = '<key-here>'

DASHBOARD_BASE_URL = 'https://dashboard.example.com/'
DASHBOARD_SCHEME_URL = 'https://dashboard.example.com/api/auth/scheme/'
DASHBOARD_AUTH_TOKEN = '<key-here>'

ATA_TO_BAY_NR = {
    'ata-6': 1,
    'ata-5': 2,
    'ata-4': 3,
    'ata-3': 4,
}

# disk empty sample settings
# - divide disk in sample_count regions
# - sample sample_size bytes randomly per region
POST_WIPE_SAMPLE_COUNT = 1000
POST_WIPE_SAMPLE_SIZE = 100 * 1024

# Find local_settings.py in /etc/osso-docktool or next to this file.
sys.path.insert(0, '/etc/osso-docktool')
try:
    from local_settings import *  # noqa
except ImportError:
    pass
