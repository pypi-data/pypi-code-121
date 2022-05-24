#
#  Copyright (c) 2018-2021 Renesas Inc.
#  Copyright (c) 2018-2021 EPAM Systems Inc.
#

import os

# SDK home directory name
SDK_TOOL_DIR_NAME = '.aos'
# SDK home directory full path
SDK_FULL_PATH = os.path.join(os.path.expanduser("~"), SDK_TOOL_DIR_NAME)
# Default directory with user keys and certificates
SDK_SECURITY_PATH = os.path.join(SDK_FULL_PATH, 'security')

# Default user certificate filename
USER_CERTIFICATE_FILE_NAME = 'oem-client.pem'
# Default user key filename
USER_KEY_FILE_NAME = 'private_key.pem'

# Default user certificate full path
DEFAULT_USER_CERT_PATH = os.path.join(SDK_SECURITY_PATH, USER_CERTIFICATE_FILE_NAME)
# Default user key full path
DEFAULT_USER_KEY_PATH = os.path.join(SDK_SECURITY_PATH, USER_KEY_FILE_NAME)
