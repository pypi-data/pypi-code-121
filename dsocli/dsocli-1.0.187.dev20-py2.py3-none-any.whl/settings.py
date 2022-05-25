import os
import platform
WIN_PLATFORM = platform.system() == 'Windows'
MAC_PLATFORM = platform.system() == 'Darwin'
NIX_PLATFORM = platform.system() == 'Linux'

COLORED_LOGS = os.getenv('DSO_COLORED_LOGS', 'Yes').lower() in ['yes', 'true']
BOLD_LOGS = os.getenv('DSO_BOLD_LOGS', 'No').lower() in ['yes', 'True']
TIMESTAMP_LOGS = os.getenv('DSO_TIMESTAMP_LOGS', 'Yes').lower() in ['yes', 'true']
LABEL_LOG_LEVELS = os.getenv('DSO_LABEL_LOG_LEVELS', 'Yes').lower() in ['yes', 'true']
USE_PAGER = os.getenv('DSO_USE_PAGER', 'Yes').lower() in ['yes', 'true']
ALLOW_STAGE_TEMPLATES = os.getenv('DSO_ALLOW_STAGE_TEMPLATES', 'No').lower() in ['yes', 'true']
PAGER = os.getenv('DSO_PAGER') or os.getenv('PAGER')
EDITOR = os.getenv('DSO_EDITOR') or os.getenv('EDITOR')
DEFAULT_LOG_LEVEL = os.getenv('DSO_DEFAULT_LOG_LEVEL', 'INFO').upper()
RESPONSE_FORMAT = os.getenv('DSO_RESPONSE_FORMAT', 'json').lower()
LOG_TIME_FORMAT = os.getenv('DSO_LOG_TIME_FORMAT', '%Y-%m-%d %H:%M:%S')


