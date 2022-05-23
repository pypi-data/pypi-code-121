#!/usr/bin/env python
###############################################################################
# (c) Copyright 2019 CERN for the benefit of the LHCb Collaboration           #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "LICENSE".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################
"""Use dirac-proxy-init to get a proxy."""
import os
import sys
from DIRAC.Core.Utilities.DIRACScript import DIRACScript


@DIRACScript()
def main():
    if os.getenv("X509_CERT_DIR") is None:
        sys.exit("the variable X509_CERT_DIR do not exist")

    if not os.path.isdir(os.environ["X509_CERT_DIR"]):
        sys.exit("the directory %s does not exist" % os.environ["X509_CERT_DIR"])

    if os.getenv("X509_VOMS_DIR") is None:
        sys.exit("the variable X509_VOMS_DIR do not exist")

    if not os.path.isdir(os.environ["X509_VOMS_DIR"]):
        sys.exit("the directory %s does not exist" % os.environ["X509_VOMS_DIR"])

    out = os.system("dirac-proxy-init -o LogLevel=NOTICE --strict --rfc '%s'" % "' '".join(sys.argv[1:]))
    sys.exit(int(out / 256))


if __name__ == "__main__":
    main()
