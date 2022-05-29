import glob
import os
import subprocess

import pydmt.helpers.general

protocol = "https"
codename = subprocess.check_output(["lsb_release", "--codename", "--short"]).decode().rstrip()
arch = subprocess.check_output(
    "dpkg-architecture | grep -e ^DEB_BUILD_ARCH= | cut -d = -f 2", shell=True
).decode().rstrip()
architectures = f"{arch} source"
component = "main"
folder = "apt"
service_dir = os.path.join(
    pydmt.helpers.general.homedir, "public_html/public", folder
)
pack_list = glob.glob(
    os.path.join(pydmt.helpers.general.homedir, "packages", "*.deb")
)
pack_str = " ".join(pack_list)
release_id = subprocess.check_output(["lsb_release", "--id", "--short"]).decode().rstrip()
key_file = "public_key.gpg"

personal_slug = 'veltzer'
exception = f'50{personal_slug}'
apache_site_file = f'{personal_slug}.apt'
