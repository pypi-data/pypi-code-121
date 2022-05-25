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
""" WMSSecureGW service -  a generic gateway service

    Mostly used by BOINC
"""
import six
import json
from DIRAC import S_OK, S_ERROR, gLogger
from DIRAC.Core.Security import Properties
from DIRAC.ConfigurationSystem.Client.Helpers.Registry import getDNForUsername, findDefaultGroupForDN
from DIRAC.AccountingSystem.Client.DataStoreClient import DataStoreClient
from DIRAC.Core.DISET.RequestHandler import RequestHandler
from DIRAC.RequestManagementSystem.Client.Request import Request
from DIRAC.RequestManagementSystem.Client.Operation import Operation
from DIRAC.RequestManagementSystem.Client.ReqClient import ReqClient
from DIRAC.ConfigurationSystem.Client.Helpers import Registry
from DIRAC.ConfigurationSystem.Client.Helpers.Operations import Operations
from DIRAC.ConfigurationSystem.Client.Helpers import cfgPath
from DIRAC.Core.DISET.RPCClient import RPCClient
from DIRAC.WorkloadManagementSystem.Client.MatcherClient import MatcherClient
from DIRAC.WorkloadManagementSystem.Client.JobStateUpdateClient import JobStateUpdateClient
from DIRAC.WorkloadManagementSystem.Client.JobManagerClient import JobManagerClient
from DIRAC.WorkloadManagementSystem.Client.PilotManagerClient import PilotManagerClient
from DIRAC.WorkloadManagementSystem.Client.JobMonitoringClient import JobMonitoringClient

# pylint: disable=no-self-use


class WMSSecureGWHandler(RequestHandler):
    """WMSSecure class."""

    @classmethod
    def initializeHandler(cls, serviceInfo):  # pylint: disable=unused-argument
        """Handler initialization."""
        from DIRAC.DataManagementSystem.Service.FileCatalogHandler import FileCatalogHandler

        if FileCatalogHandler.types_hasAccess != cls.types_hasAccess:
            raise Exception("FileCatalog hasAccess types has been changed.")
        if FileCatalogHandler.types_exists != cls.types_exists:
            raise Exception("FileCatalog exists types has been changed.")
        if FileCatalogHandler.types_addFile != cls.types_addFile:
            raise Exception("FileCatalog addFile types has been changed.")
        from DIRAC.WorkloadManagementSystem.Service.MatcherHandler import MatcherHandler

        if MatcherHandler.types_requestJob != cls.types_requestJob:
            raise Exception("Matcher requestJob types has been changed.")
        from DIRAC.WorkloadManagementSystem.Service.JobStateUpdateHandler import JobStateUpdateHandler

        if JobStateUpdateHandler.types_setJobStatus != cls.types_setJobStatus:
            raise Exception("JobStateUpdate setJobStatus types has been changed.")
        if JobStateUpdateHandler.types_setJobSite != cls.types_setJobSite:
            raise Exception("JobStateUpdate setJobSite types has been changed.")
        if JobStateUpdateHandler.types_setJobParameter != cls.types_setJobParameter:
            raise Exception("JobStateUpdate setJobParameter types has been changed.")
        if JobStateUpdateHandler.types_setJobStatusBulk != cls.types_setJobStatusBulk:
            raise Exception("JobStateUpdate setJobStatusBulk types has been changed.")
        if JobStateUpdateHandler.types_setJobParameters != cls.types_setJobParameters:
            raise Exception("JobStateUpdate setJobParameters types has been changed.")
        if JobStateUpdateHandler.types_sendHeartBeat != cls.types_sendHeartBeat:
            raise Exception("JobStateUpdate sendHeartBeat types has been changed.")
        from DIRAC.WorkloadManagementSystem.Service.JobManagerHandler import JobManagerHandler

        if JobManagerHandler.types_rescheduleJob != cls.types_rescheduleJob:
            raise Exception("JobManager rescheduleJob types has been changed.")
        from DIRAC.WorkloadManagementSystem.Service.PilotManagerHandler import PilotManagerHandler

        if PilotManagerHandler.types_setPilotStatus != cls.types_setPilotStatus:
            raise Exception("PilotManager setPilotStatus types has been changed.")
        if PilotManagerHandler.types_setJobForPilot != cls.types_setJobForPilot:
            raise Exception("PilotManager setJobForPilot types has been changed.")
        if PilotManagerHandler.types_setPilotBenchmark != cls.types_setPilotBenchmark:
            raise Exception("PilotManager setPilotBenchmark types has been changed.")
        from DIRAC.WorkloadManagementSystem.Service.JobMonitoringHandler import JobMonitoringHandler

        if JobMonitoringHandler.types_getJobParameter != cls.types_getJobParameter:
            raise Exception("JobMonitoring getJobParameter types has been changed.")
        from DIRAC.FrameworkSystem.Service.ProxyManagerHandler import ProxyManagerHandler

        if ProxyManagerHandler.types_getVOMSProxy != cls.types_getVOMSProxy:
            raise Exception("ProxyManagerHandler getVOMSProxy types has been changed.")
        if ProxyManagerHandler.types_getProxy != cls.types_getProxy:
            raise Exception("ProxyManagerHandler getProxy types has been changed.")
        from DIRAC.RequestManagementSystem.Service.ReqManagerHandler import ReqManagerHandler

        if ReqManagerHandler.types_putRequest != cls.types_putRequest:
            raise Exception("ReqManagerHandler putRequest types has been changed.")
        from DIRAC.AccountingSystem.Service.DataStoreHandler import DataStoreHandler

        if DataStoreHandler.types_commitRegisters != cls.types_commitRegisters:
            raise Exception("DataStoreHandler commitRegisters types has been changed.")

        return S_OK()

    types_requestJob = [[six.string_types, dict]]

    def export_requestJob(self, resourceDescription):
        """Serve a job to the request of an agent which is the highest priority one
        matching the agent's site capacity."""
        result = MatcherClient(timeout=600).requestJob(resourceDescription)
        return result

    ###########################################################################
    types_setJobStatus = [(six.string_types, six.integer_types), six.string_types, six.string_types, six.string_types]

    def export_setJobStatus(self, jobID, status, minorStatus, source="Unknown", datetime=None):
        """Set the major and minor status for job specified by its JobId.

        Set optionally the status date and source component which sends the
        status information.
        """
        jobStatus = JobStateUpdateClient().setJobStatus(int(jobID), status, minorStatus, source, datetime)
        return jobStatus

    ###########################################################################
    types_setJobSite = [(six.string_types, six.integer_types), six.string_types]

    def export_setJobSite(self, jobID, site):
        """Allows the site attribute to be set for a job specified by its jobID."""
        jobSite = JobStateUpdateClient().setJobSite(jobID, site)
        return jobSite

    ###########################################################################
    types_setJobParameter = [(six.string_types, six.integer_types), six.string_types, six.string_types]

    def export_setJobParameter(self, jobID, name, value):
        """Set arbitrary parameter specified by name/value pair for job specified
        by its JobId."""
        jobParam = JobStateUpdateClient().setJobParameter(int(jobID), name, value)
        return jobParam

    ###########################################################################
    types_setJobStatusBulk = [(six.string_types, six.integer_types), dict]

    def export_setJobStatusBulk(self, jobID, statusDict):
        """Set various status fields for job specified by its JobId.

        Set only the last status in the JobDB, updating all the status
        logging information in the JobLoggingDB. The statusDict has datetime
        as a key and status information dictionary as values
        """
        jobStatus = JobStateUpdateClient().setJobStatusBulk(jobID, statusDict)
        return jobStatus

    ###########################################################################
    types_setJobParameters = [(six.string_types, six.integer_types), list]

    def export_setJobParameters(self, jobID, parameters):
        """Set arbitrary parameters specified by a list of name/value pairs for job
        specified by its JobId."""
        jobParams = JobStateUpdateClient().setJobParameters(jobID, parameters)
        return jobParams

    ###########################################################################
    types_sendHeartBeat = [(six.string_types, six.integer_types), dict, dict]

    def export_sendHeartBeat(self, jobID, dynamicData, staticData):
        """Send a heart beat sign of life for a job jobID."""
        result = JobStateUpdateClient(timeout=120).sendHeartBeat(jobID, dynamicData, staticData)
        return result

    ##########################################################################################
    types_rescheduleJob = []

    def export_rescheduleJob(self, jobIDs):
        """Reschedule a single job.

        If the optional proxy parameter is given it will be used to refresh
        the proxy in the Proxy Repository
        """
        result = JobManagerClient().rescheduleJob(jobIDs)
        return result

    ##########################################################################################
    types_setPilotStatus = [six.string_types, six.string_types]

    def export_setPilotStatus(self, pilotRef, status, destination=None, reason=None, gridSite=None, queue=None):
        """Set the pilot agent status."""
        result = PilotManagerClient().setPilotStatus(pilotRef, status, destination, reason, gridSite, queue)
        return result

    ##############################################################################
    types_setJobForPilot = [six.string_types + six.integer_types, six.string_types]

    def export_setJobForPilot(self, jobID, pilotRef, destination=None):
        """Report the DIRAC job ID which is executed by the given pilot job."""
        result = PilotManagerClient().setJobForPilot(jobID, pilotRef, destination)
        return result

    ##########################################################################################
    types_setPilotBenchmark = [six.string_types, float]

    def export_setPilotBenchmark(self, pilotRef, mark):
        """Set the pilot agent benchmark."""
        result = PilotManagerClient().setPilotBenchmark(pilotRef, mark)
        return result

    ##############################################################################
    types_getJobParameter = [(six.string_types, six.integer_types), six.string_types]

    @staticmethod
    def export_getJobParameter(jobID, parName):
        result = JobMonitoringClient(timeout=120).getJobParameter(jobID, parName)
        return result

    ##############################################################################
    types_getVOMSProxy = [six.string_types, six.string_types, six.string_types, six.integer_types]

    def export_getVOMSProxy(
        self, userDN, userGroup, requestPem, requiredLifetime, vomsAttribute=False
    ):  # pylint: disable=unused-argument
        """Always return the Boinc proxy."""
        userDN, userGroup, _ = self.__getOwnerGroupDN("BoincUser")
        rpcClient = RPCClient("Framework/BoincProxyManager", timeout=120)
        retVal = rpcClient.getProxy(userDN, userGroup, requestPem, requiredLifetime)
        return retVal

    ##############################################################################
    types_getProxy = [six.string_types, six.string_types, six.string_types, six.integer_types]

    def export_getProxy(self, userDN, userGroup, requestPem, requiredLifetime):  # pylint: disable=unused-argument
        """Get the Boinc User proxy."""
        userDN, userGroup, _ = self.__getOwnerGroupDN("BoincUser")
        rpcClient = RPCClient("Framework/BoincProxyManager", timeout=120)
        retVal = rpcClient.getProxy(userDN, userGroup, requestPem, requiredLifetime)
        return retVal

    ##############################################################################
    def __checkProperties(self, requestedUserDN, requestedUserGroup):
        """Check the properties and return if they can only download limited
        proxies if authorized."""
        credDict = self.getRemoteCredentials()
        gLogger.debug("in credDict %s" % credDict["properties"])
        if Properties.FULL_DELEGATION in credDict["properties"]:
            return S_OK(False)
        if Properties.LIMITED_DELEGATION in credDict["properties"]:
            return S_OK(True)
        if Properties.PRIVATE_LIMITED_DELEGATION in credDict["properties"]:
            if credDict["DN"] != requestedUserDN:
                return S_ERROR("You are not allowed to download any proxy")
            if Properties.PRIVATE_LIMITED_DELEGATION in Registry.getPropertiesForGroup(requestedUserGroup):
                return S_ERROR("You can't download proxies for that group")
            return S_OK(True)
        # Not authorized!
        return S_ERROR("You can't get proxies! Bad boy!")

    ########################################################################

    types_hasAccess = [[six.string_types, dict], [six.string_types, list, dict]]

    def export_hasAccess(self, paths, opType):  # pylint: disable=unused-argument
        """Access."""
        successful = {}
        for path in paths:
            successful[path] = True
        resDict = {"Successful": successful, "Failed": {}}
        return S_OK(resDict)

    types_exists = [[list, dict] + list(six.string_types)]

    def export_exists(self, lfns):
        """Check whether the supplied paths exists."""
        successful = {}
        for lfn in lfns:
            successful[lfn] = False
        resDict = {"Successful": successful, "Failed": {}}
        return S_OK(resDict)

    ########################################################################

    types_addFile = [[list, dict] + list(six.string_types)]

    def export_addFile(self, lfns):
        """Register supplied files."""
        failed = {}
        for lfn in lfns:
            failed[lfn] = True
        return S_OK({"Successful": {}, "Failed": failed})

    types_putRequest = [six.string_types]

    def export_putRequest(self, requestJSON):
        """put a new request into RequestDB."""

        requestDict = json.loads(requestJSON)
        request = Request(requestDict)
        operation = Operation()  # # create new operation
        operation.Type = "WMSSecureOutputData"
        request.insertBefore(operation, request[0])
        userDN, userGroup, _ = self.__getOwnerGroupDN("ProductionManager")
        request.OwnerDN = userDN
        request.OwnerGroup = userGroup
        return ReqClient().putRequest(request)

    def __getOwnerGroupDN(self, shifterType):
        opsHelper = Operations()
        userName = opsHelper.getValue(cfgPath("BoincShifter", shifterType, "User"), "")
        if not userName:
            return S_ERROR("No shifter User defined for %s" % shifterType)
        result = getDNForUsername(userName)
        if not result["OK"]:
            return result
        userDN = result["Value"][0]
        result = findDefaultGroupForDN(userDN)
        if not result["OK"]:
            return result
        defaultGroup = result["Value"]
        userGroup = opsHelper.getValue(cfgPath("BoincShifter", shifterType, "Group"), defaultGroup)
        return userDN, userGroup, userName

    ########################################################################

    types_commitRegisters = [list]

    def export_commitRegisters(self, entriesList):
        retVal = DataStoreClient().commitRegisters(entriesList)
        return retVal
