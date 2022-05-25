"""
Copyright (c) 2021 Synopsys, Inc.
Use subject to the terms and conditions of the Synopsys End User Software License and Maintenance Agreement.
All rights reserved worldwide.
"""


def parse_go_pseudoversion(version):
    # Pseudoversion
    if version.startswith("v") and "." in version:
        tail = version.split(".")[-1]
        tailparts = tail.split("-")
        # Check if matches pseudoversion format
        if (
            len(tailparts) > 1
            and len(tailparts[-2]) == 14
            and len(tailparts[-1]) == 12
            and tailparts[-2].isdigit()
        ):
            return tailparts[-2], tailparts[-1]
    raise ValueError("Not pseudo-version")