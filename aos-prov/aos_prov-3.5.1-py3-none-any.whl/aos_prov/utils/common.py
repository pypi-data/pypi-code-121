#
#  Copyright (c) 2018-2022 Renesas Inc.
#  Copyright (c) 2018-2022 EPAM Systems Inc.
#

import random
import string
from pathlib import Path

from rich.console import Console

CONTENT_ENCRYPTION_ALGORITHM = 'aes256_cbc'
DOWNLOADS_PATH = Path.home() / '.aos' / 'downloads'
AOS_DISK_PATH = DOWNLOADS_PATH / 'aos-disk.vmdk'
VBOX_SDK_PATH = DOWNLOADS_PATH / 'vbox-sdk.zip'

DISK_IMAGE_DOWNLOAD_URL = 'https://epam-my.sharepoint.com/:u:/p/volodymyr_mykytiuk1/ERK4_JGBmGJApEwupIlxq7sBaU' \
                          '-hqEyxJbACTsiP8KP9qw?e=cK2hfi&download=1'
VIRTUAL_BOX_DOWNLOAD_URL = 'https://download.virtualbox.org/virtualbox/6.1.32/VirtualBoxSDK-6.1.32-149290.zip'

console = Console()


def generate_random_password() -> str:
    """
    Generate random password from letters and digits.

    Returns:
        str: Random string password
    """
    dictionary = string.ascii_letters + string.digits
    password_length = random.randint(10, 15)
    return ''.join(random.choice(dictionary) for _ in range(password_length))
