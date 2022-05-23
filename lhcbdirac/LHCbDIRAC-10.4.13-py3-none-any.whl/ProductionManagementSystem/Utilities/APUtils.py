###############################################################################
# (c) Copyright 2021 CERN for the benefit of the LHCb Collaboration           #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "LICENSE".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################
"""Helpers used by the Analysis Productions code."""
from enum import Enum


class APStates(str, Enum):
    ARCHIVED = "ARCHIVED"
    PUBLISHED = "PUBLISHED"
    WAITING = "WAITING"
    ACTIVE = "ACTIVE"
    REPLICATING = "REPLICATING"
    READY = "READY"
