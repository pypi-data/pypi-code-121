

'''
    EntryPoint
'''

import os
from app import create_app

config_file = os.getenv('APP_CONFIG_FILE', "config.py")

app = create_app(config_file)

