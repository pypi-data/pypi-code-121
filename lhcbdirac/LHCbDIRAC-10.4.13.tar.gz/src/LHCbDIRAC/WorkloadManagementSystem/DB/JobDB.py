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
"""LHCbDIRAC Job DB.

Extends the DIRAC JobDB with minor things
"""
from DIRAC import S_OK
from DIRAC.Core.Utilities import Time

from DIRAC.WorkloadManagementSystem.DB.JobDB import JobDB as DIRACJobDB


class JobDB(DIRACJobDB):
    """Extension of the DIRAC Job DB."""

    def __init__(self):
        """The standard constructor takes the database name (dbname) and the name
        of the configuration section (dbconfig)"""
        DIRACJobDB.__init__(self)
        self.jdl2DBParameters += ["runNumber"]

    def getTimings(self, site, period=3600):
        """Get CPU and wall clock times for the jobs finished in the last hour."""
        ret = self._escapeString(site)
        if not ret["OK"]:
            return ret
        site = ret["Value"]

        date = str(Time.dateTime() - Time.second * period)
        req = "SELECT JobID from Jobs WHERE Site=%s and EndExecTime > '%s' " % (site, date)
        result = self._query(req)
        jobList = [str(x[0]) for x in result["Value"]]
        jobString = ",".join(jobList)

        req = "SELECT SUM(Value) from JobParameters WHERE Name='TotalCPUTime(s)' and JobID in (%s)" % jobString
        result = self._query(req)
        if not result["OK"]:
            return result
        cpu = result["Value"][0][0]
        if not cpu:
            cpu = 0.0

        req = "SELECT SUM(Value) from JobParameters WHERE Name='WallClockTime(s)' and JobID in (%s)" % jobString
        result = self._query(req)
        if not result["OK"]:
            return result
        wctime = result["Value"][0][0]
        if not wctime:
            wctime = 0.0

        return S_OK({"CPUTime": int(cpu), "WallClockTime": int(wctime)})
