'''

    constants.py
 
    Copyright (C) 2022 by RStudio, PBC
 
'''

# This file shares variables with '../src/constants.ts'
# Changes made to this file may need to be duplicated there.

import os
from typing import List

# environment variables set by RSW
URI_SCHEME = os.getenv('RS_URI_SCHEME')
SESSION_URL = os.getenv('RS_SESSION_URL')
HOME_URL = os.getenv('RS_HOME_URL')
SERVER_URL = (os.getenv('RS_SERVER_URL')[:-1] 
    if os.getenv('RS_SERVER_URL') is not None and os.getenv('RS_SERVER_URL').endswith('/')
    else os.getenv('RS_SERVER_URL'))

# default process names
SHINY_APP = 'Shiny Project'
QUARTO_APP = 'Quarto Project'

# server extension endpoints
SERVER_ENDPOINT = 'servers'
URL_ENDPOINT = 'url'

# constants for processing processes
COMMANDS_TO_SKIP: List[str] = ['^$', 'rsession', 'code-server', 'jupyterlab_rsw']
PROC_DIR: str = '/proc/'
ARGS_TO_SKIP: List[str] = [
  'jupyter-lab|ipykernel_launcher|jupyter-notebook',
  "cat\\('---vsc---'",
  'debugpy/adapter',
]

# constants for environment variables
PORT_ENV = 'PORT'

# port tokens for generating secure URLs
DEFAULT_PORT_TOKEN = 'a433e59dc087'
PORT_TOKEN = (os.getenv('RS_PORT_TOKEN')
    if os.getenv('RS_PORT_TOKEN') is not None
    else DEFAULT_PORT_TOKEN)
