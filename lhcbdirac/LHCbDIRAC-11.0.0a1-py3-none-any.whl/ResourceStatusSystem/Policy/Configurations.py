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
"""LHCbDIRAC.ResourceStatusSystem.Policy.Configurations.

POLICIESMETA_LHCB policies POLICIESMETA
"""

from DIRAC.ResourceStatusSystem.Policy.Configurations import POLICIESMETA

# LHCb Policies

POLICIESMETA_LHCB = {
    "TransferQualitySource": {
        "description": "Transfers from element, quality measure",
        "module": "TransferQualityPolicy",
        "command": ("TransferCommand", "TransferCommand"),
        "args": {"direction": "Source", "metric": "Quality", "hours": 2},
    },
    "TransferQualityDestination": {
        "description": "Transfers to element, quality measure",
        "module": "TransferQualityPolicy",
        "command": ("TransferCommand", "TransferCommand"),
        "args": {"direction": "Destination", "metric": "Quality", "hours": 2},
    },
}

################################################################################
# Old stuff

policies = {
    "DTScheduled": {
        "description": "Ongoing and scheduled down-times",
        "module": "DTPolicy",
        "commandInNewRes": ("GOCDBStatusCommand", "GOCDBStatusCommand"),
        # 'command'         : ( 'GOCDBStatusCommand', 'DTCachedCommand' ),
        "command": ("GOCDBStatusCommand", "GOCDBStatusCommand"),
        "args": {"hours": 12},  # Fix to avoid querying the CS on load time, to be fixed
        "Site_Panel": [{"WebLink": {"CommandIn": ("GOCDBStatusCommand", "DTInfoCachedCommand"), "args": None}}],
        "Resource_Panel": [{"WebLink": {"CommandIn": ("GOCDBStatusCommand", "DTInfoCachedCommand"), "args": None}}],
    },
    "OnStorageElementPropagation": {
        "description": "How the storage element's nodes are behaving in the RSS",
        "module": "DownHillPropagationPolicy",
        "command": ("RSCommand", "MonitoredStatusCommand"),
        "args": ("Resource",),
        "SE_Panel": [{"RSS": "ResOfStorEl"}],
    },
    "TransferQuality": {
        "description": "SE transfer quality",
        "module": "TransferQualityPolicy",
        "commandInNewRes": ("DIRACAccountingCommand", "TransferQualityCommand"),
        "argsNewRes": None,
        "command": ("DIRACAccountingCommand", "TransferQualityFromCachedPlotCommand"),
        "args": ("DataOperation", "TransferQualityByDestSplitted_2"),
        "SE_Panel": [
            {
                "FillChart - Transfer quality in the last 24 hours": {
                    "CommandIn": ("DIRACAccountingCommand", "CachedPlotCommand"),
                    "args": ("DataOperation", "TransferQualityByDestSplitted_24"),
                    "CommandInNewRes": ("DIRACAccountingCommand", "DIRACAccountingCommand"),
                    "argsNewRes": (
                        "DataOperation",
                        "Quality",
                        {"Format": "LastHours", "hours": 24},
                        "Destination",
                        {"OperationType": "putAndRegister"},
                    ),
                }
            },
        ],
    },
}

# Update DIRAC policies with LHCbDIRAC policies
POLICIESMETA.update(POLICIESMETA_LHCB)
