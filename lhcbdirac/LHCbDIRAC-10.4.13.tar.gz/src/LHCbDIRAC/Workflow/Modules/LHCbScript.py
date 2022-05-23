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
"""LHCbScript is very similar to DIRAC Script module, but consider LHCb
environment."""
import os

from DIRAC import gLogger
from DIRAC.Core.Utilities import DErrno
from DIRAC.Workflow.Modules.Script import Script


class LHCbScript(Script):
    """A simple extension to the DIRAC script module."""

    def __init__(self):
        """c'tor."""
        self.log = gLogger.getSubLogger("LHCbScript")
        super(LHCbScript, self).__init__(self.log)

        self.systemConfig = "ANY"
        self.environment = {}

    def _resolveInputVariables(self):
        """By convention the workflow parameters are resolved here."""

        super(LHCbScript, self)._resolveInputVariables()
        super(LHCbScript, self)._resolveInputStep()

        self.systemConfig = self.step_commons.get("SystemConfig", self.systemConfig)

    def _executeCommand(self):
        """Executes the self.command (uses systemCall) with binary tag (CMTCONFIG)
        requested (if not 'ANY')"""

        if self.systemConfig != "ANY":
            self.environment = os.environ
            self.environment["CMTCONFIG"] = self.systemConfig

        super(LHCbScript, self)._executeCommand()

    def _exitWithError(self, status):
        """Extended here for treating case of lb-run error codes (and executable
        name)."""
        # pylint doesn't like this as it's now Python 3 only
        from LHCbDIRAC.Core.Utilities.RunApplication import LbRunError  # pylint: disable=import-error,no-name-in-module

        # this is an lb-run specific error
        if status & 0x40 and not status & 0x80:
            self.log.error("Exit status is an lb-run specific error", "(%s)" % status)
            raise LbRunError("Problem setting the environment: lb-run exited with status %d" % status, DErrno.EWMSRESC)
        else:
            super(LHCbScript, self)._exitWithError(status)
