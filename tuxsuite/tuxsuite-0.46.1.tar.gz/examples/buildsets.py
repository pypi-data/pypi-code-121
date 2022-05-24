# -*- coding: utf-8 -*-

import requests

response = requests.get("https://api.tuxbuild.com/v1/supportmatrix")
matrix = response.json()

output = """sets:
  - name: tinyconfigs
    # Build with e.g.:
    # tuxsuite build-set --git-repo 'https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git' --git-ref master --tux-config https://gitlab.com/Linaro/tuxsuite/-/raw/master/examples/buildsets.yaml --set-name tinyconfigs
    builds:
"""  # noqa: E501

for toolchain, architectures in matrix.items():
    for architecture in architectures:
        output += f"      - {{toolchain: {toolchain}, target_arch: {architecture}, kconfig: tinyconfig}}\n"

print(output.strip())
