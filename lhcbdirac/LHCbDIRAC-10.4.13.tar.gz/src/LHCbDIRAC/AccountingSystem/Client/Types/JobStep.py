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
"""JobStep Type."""
from DIRAC.AccountingSystem.Client.Types.BaseAccountingType import BaseAccountingType


class JobStep(BaseAccountingType):
    """JobStep as extension of BaseAccountingType."""

    def __init__(self):

        super(JobStep, self).__init__()

        self.definitionKeyFields = [
            ("JobGroup", "VARCHAR(32)"),
            ("RunNumber", "VARCHAR(32)"),
            ("EventType", "VARCHAR(32)"),
            ("ProcessingType", "VARCHAR(256)"),
            ("ProcessingStep", "VARCHAR(256)"),
            ("Site", "VARCHAR(32)"),
            ("FinalStepState", "VARCHAR(32)"),
        ]

        self.definitionAccountingFields = [
            ("CPUTime", "INT UNSIGNED"),  # utime + stime + cutime + cstime
            ("NormCPUTime", "INT UNSIGNED"),  # CPUTime * CPUNormalizationFactor
            ("ExecTime", "INT UNSIGNED"),  # elapsed_time (wall time) * numberOfProcessors
            ("InputData", "BIGINT UNSIGNED"),
            ("OutputData", "BIGINT UNSIGNED"),
            ("InputEvents", "BIGINT UNSIGNED"),
            ("OutputEvents", "BIGINT UNSIGNED"),
        ]

        self.bucketsLength = [
            (86400 * 7, 3600),  # <1w = 1h
            (86400 * 35, 3600 * 4),  # <35d = 4h
            (86400 * 30 * 6, 86400),  # <6m = 1d
            (86400 * 365, 86400 * 2),  # <1y = 2d
            (86400 * 600, 604800),  # >1y = 1w
        ]

        self.checkType()
