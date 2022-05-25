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
"""Popularity Type."""
from DIRAC.AccountingSystem.Client.Types.BaseAccountingType import BaseAccountingType


class Popularity(BaseAccountingType):
    """Popularity as extension of BaseAccountingType."""

    def __init__(self):

        super(Popularity, self).__init__()

        self.definitionKeyFields = [
            ("DataType", "VARCHAR(64)"),
            ("Activity", "VARCHAR(64)"),
            ("FileType", "VARCHAR(64)"),
            ("Production", "VARCHAR(32)"),
            ("ProcessingPass", "VARCHAR(256)"),
            ("Conditions", "VARCHAR(64)"),
            ("EventType", "VARCHAR(64)"),
            ("StorageElement", "VARCHAR(32)"),
        ]

        self.definitionAccountingFields = [("Usage", "BIGINT UNSIGNED"), ("NormalizedUsage", "BIGINT UNSIGNED")]

        self.bucketsLength = [
            (86400 * 30 * 6, 86400),  # <6m = 1d
            (31104000, 604800),  # >6m = 1w
        ]
        self.checkType()
