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
"""Extension of DIRAC SiteDirector.

Simply defines what to send.
"""

from DIRAC import S_OK
from DIRAC.WorkloadManagementSystem.Agent.SiteDirector import SiteDirector as DIRACSiteDirector


class SiteDirector(DIRACSiteDirector):
    """Simple extension of the DIRAC site director to send LHCb specific pilots
    (with a custom list of commands)"""

    def beginExecution(self):
        """just simple redefinition."""
        res = DIRACSiteDirector.beginExecution(self)
        if not res["OK"]:
            return res

        self.lbRunOnly = self.am_getOption("lbRunOnly", False)

        return S_OK()

    def _getPilotOptions(self, queue):
        """Adding LHCb specific options."""
        pilotOptions = super(SiteDirector, self)._getPilotOptions(queue)

        if self.lbRunOnly:
            pilotOptions.append("-o lbRunOnly")

        return pilotOptions
