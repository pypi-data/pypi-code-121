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
"""ProductionRequestHandler is the implementation of the Production Request
service."""
import importlib.resources
import os
import subprocess
import six
import tempfile

from DIRAC import gLogger, S_OK, S_ERROR
from DIRAC.Core.DISET.RequestHandler import RequestHandler
from DIRAC.FrameworkSystem.Client.ProxyManagerClient import gProxyManager
from DIRAC.Core.Utilities.Subprocess import shellCall

from LHCbDIRAC.ProductionManagementSystem.DB.ProductionRequestDB import ProductionRequestDB


class ProductionRequestHandler(RequestHandler):
    @classmethod
    def initializeHandler(cls, serviceInfoDict):
        cls.productionRequestDB = ProductionRequestDB()
        return S_OK()

    def __clientCredentials(self):
        creds = self.getRemoteCredentials()
        group = creds.get("group", "(unknown)")
        DN = creds.get("DN", "(unknown)")
        #    if 'DN' in creds:
        #      cn = re.search('/CN=([^/]+)',creds['DN'])
        #      if cn:
        #        return { 'User':cn.group(1), 'Group':group }
        return {"User": creds.get("username", "Anonymous"), "Group": group, "DN": DN}

    types_createProductionRequest = [dict]

    def export_createProductionRequest(self, requestDict):
        """Create production request."""
        creds = self.__clientCredentials()
        if "MasterID" not in requestDict:
            requestDict["RequestAuthor"] = creds["User"]
        return self.productionRequestDB.createProductionRequest(requestDict, creds)

    types_getProductionRequest = [list]

    def export_getProductionRequest(self, requestIDList):
        """Get production request(s) specified by the list of requestIDs
        AZ!!: not tested !!
        """
        if not requestIDList:
            return S_OK({})
        result = self.productionRequestDB.getProductionRequest(requestIDList)
        if not result["OK"]:
            return result
        rows = {}
        for row in result["Value"]["Rows"]:
            iD = row["RequestID"]
            rows[iD] = row
        return S_OK(rows)

    types_getProductionRequestList = [
        six.integer_types,
        six.string_types,
        six.string_types,
        six.integer_types,
        six.integer_types,
        dict,
    ]

    def export_getProductionRequestList(self, subrequestFor, sortBy, sortOrder, offset, limit, rFilter):
        """Get production requests in list format (for portal grid)"""
        return self.productionRequestDB.getProductionRequest(
            [], subrequestFor, sortBy, sortOrder, offset, limit, rFilter
        )

    types_updateProductionRequest = [six.integer_types, dict]

    def export_updateProductionRequest(self, requestID, requestDict):
        """Update production request specified by requestID."""
        creds = self.__clientCredentials()
        return self.productionRequestDB.updateProductionRequest(requestID, requestDict, creds)

    types_duplicateProductionRequest = [six.integer_types, bool]

    def export_duplicateProductionRequest(self, requestID, clearpp):
        """Duplicate production request with subrequests."""
        creds = self.__clientCredentials()
        return self.productionRequestDB.duplicateProductionRequest(requestID, creds, clearpp)

    types_deleteProductionRequest = [six.integer_types]

    def export_deleteProductionRequest(self, requestID):
        """Delete production request specified by requestID."""
        creds = self.__clientCredentials()
        return self.productionRequestDB.deleteProductionRequest(requestID, creds)

    types_splitProductionRequest = [six.integer_types, list]

    def export_splitProductionRequest(self, requestID, splitList):
        """split production request."""
        creds = self.__clientCredentials()
        return self.productionRequestDB.splitProductionRequest(requestID, splitList, creds)

    types_getProductionProgressList = [six.integer_types]

    def export_getProductionProgressList(self, requestID):
        """Return the list of associated with requestID productions."""
        return self.productionRequestDB.getProductionProgress(requestID)

    types_addProductionToRequest = [dict]

    def export_addProductionToRequest(self, pdict):
        """Associate production to request."""
        return self.productionRequestDB.addProductionToRequest(pdict)

    types_removeProductionFromRequest = [six.integer_types]

    def export_removeProductionFromRequest(self, productionID):
        """Deassociate production."""
        return self.productionRequestDB.removeProductionFromRequest(productionID)

    types_useProductionForRequest = [six.integer_types, bool]

    def export_useProductionForRequest(self, productionID, used):
        """Set Used flags for production."""
        return self.productionRequestDB.useProductionForRequest(productionID, used)

    types_getRequestHistory = [six.integer_types]

    def export_getRequestHistory(self, requestID):
        """Return the list of state changes for the request."""
        return self.productionRequestDB.getRequestHistory(requestID)

    types_getTrackedProductions = []

    def export_getTrackedProductions(self):
        """Return the list of productions in active requests."""
        return self.productionRequestDB.getTrackedProductions()

    types_updateTrackedProductions = [list]

    def export_updateTrackedProductions(self, update):
        """Update tracked productions (used by Agent)"""
        return self.productionRequestDB.updateTrackedProductions(update)

    types_getTrackedInput = []

    def export_getTrackedInput(self):
        """Return the list of requests with dynamic input data."""
        return self.productionRequestDB.getTrackedInput()

    types_updateTrackedInput = [list]

    def export_updateTrackedInput(self, update):
        """Update real number of input events (used by Agent)"""
        return self.productionRequestDB.updateTrackedInput(update)

    types_getAllSubRequestSummary = []

    def export_getAllSubRequestSummary(self, status="", rType=""):
        """Return a summary for each subrequest."""
        return self.productionRequestDB.getAllSubRequestSummary(status, rType)

    types_getAllProductionProgress = []

    def export_getAllProductionProgress(self):
        """Return all the production progress."""
        return self.productionRequestDB.getAllProductionProgress()

    def __productionTemplatePaths(self):
        """Return production template list (file based)"""
        tplFolder = importlib.resources.files("LHCbDIRAC.ProductionManagementSystem") / "Templates"
        for path in tplFolder.iterdir():
            if not path.is_file() or path.name[-1] in [".", "~"]:
                continue
            yield path

    types_getProductionTemplateList = []

    def export_getProductionTemplateList(self):
        """Return production template list (file based)"""
        templates = [
            {
                "AuthorGroup": "",
                "Author": "",
                "PublishingTime": "",
                "LongDescription": "",
                "WFName": path.name,
                "AuthorDN": "",
                "WFParent": "",
                "Description": "",
            }
            for path in self.__productionTemplatePaths()
        ]
        return S_OK(templates)

    types_getProductionTemplate = [six.string_types]

    def export_getProductionTemplate(self, name):
        for path in self.__productionTemplatePaths():
            if path.name == name:
                return S_OK(path.read_text())
        else:
            return S_ERROR(f"Template {name!r} doesn't exist")

    types_execProductionScript = [six.string_types, six.string_types]

    def export_execProductionScript(self, script, workflow):
        creds = self.__clientCredentials()
        if creds["Group"] != "lhcb_prmgr":
            return S_ERROR("You have to be production manager")
        result = gProxyManager.downloadProxyToFile(
            creds["DN"], creds["Group"], filePath=False, requiredTimeLeft=86400, cacheTime=86400
        )
        if not result["OK"]:
            return result
        proxyFile = result["Value"]
        filesToClean = [proxyFile]

        try:
            with tempfile.NamedTemporaryFile(mode="w+t", delete=False) as workflowFile:
                filesToClean += [workflowFile.name]
                workflowFile.write(workflow)
            with tempfile.NamedTemporaryFile(mode="w+t", delete=False) as scriptFile:
                filesToClean += [scriptFile.name]
                scriptFile.write(script)

            result = subprocess.run(
                ["python", scriptFile.name, workflowFile.name],
                check=False,
                capture_output=True,
                text=True,
                timeout=1800,
                env=os.environ | {"X509_USER_PROXY": proxyFile},
            )
            if result.returncode == 0:
                return S_OK(result.stdout + result.stderr)
        finally:
            for filename in filesToClean:
                os.remove(filename)

        message = f"Command exited with: {result.returncode}\nstdout: {result.stdout}\nstderr: {result.stderr}"
        gLogger.error("Failed to execProductionScript", message)
        return S_ERROR(message)

    types_execWizardScript = [six.string_types, dict]

    def export_execWizardScript(self, wizard, wizpar):
        """Execure wizard with parameters."""
        creds = self.__clientCredentials()
        if creds["Group"] != "lhcb_prmgr":
            # return S_ERROR("You have to be production manager")
            if "Generate" in wizpar:
                del wizpar["Generate"]
        result = gProxyManager.downloadProxyToFile(
            creds["DN"], creds["Group"], filePath=False, requiredTimeLeft=86400, cacheTime=86400
        )
        if not result["OK"]:
            return result
        proxyFile = result["Value"]["proxyFile"]
        try:
            f = tempfile.mkstemp()
            os.write(f[0], "wizardParameters = {\n")
            for name, value in wizpar.items():
                os.write(f[0], '  "' + str(name) + '": """' + str(value) + '""",\n')
            os.write(f[0], "}\n")
            os.write(f[0], wizard)
            os.close(f[0])
        except Exception as msg:
            gLogger.error("In temporary files createion: " + str(msg))
            os.remove(proxyFile)
            return S_ERROR(str(msg))
        setenv = "source /opt/dirac/bashrc"
        # #proxy = "X509_USER_PROXY=xxx"
        proxy = "X509_USER_PROXY=%s" % proxyFile
        cmd = "python %s" % (f[1])
        try:
            res = shellCall(1800, ["/bin/bash -c '%s;%s %s'" % (setenv, proxy, cmd)])
            if res["OK"]:
                result = S_OK(str(res["Value"][1]) + str(res["Value"][2]))
            else:
                gLogger.error(res["Message"])
                result = res
        except Exception as msg:
            gLogger.error("During execution: " + str(msg))
            result = S_ERROR("Failed to execute: %s" % str(msg))
        os.remove(f[1])
        os.remove(proxyFile)
        return result

    types_getProductionList = [six.integer_types]

    def export_getProductionList(self, requestID):
        """Return the list of productions associated with request and its
        subrequests."""
        return self.productionRequestDB.getProductionList(requestID)

    types_getProductionRequestSummary = [[six.string_types, list], [six.string_types, list]]

    def export_getProductionRequestSummary(self, status, requestType):
        """Method to retrieve the production / request relations for a given
        request status."""
        if isinstance(requestType, six.string_types):
            reqTypes = [requestType]
        elif isinstance(requestType, list):
            reqTypes = requestType

        if isinstance(status, six.string_types):
            selectStatus = [status]
        elif isinstance(status, list):
            selectStatus = status

        reqList = self.productionRequestDB.getProductionRequest([])
        if not reqList["OK"]:
            return reqList

        requests = reqList["Value"]
        resultDict = {}

        for req in requests["Rows"]:
            iD = int(req["RequestID"])
            if not req["RequestType"] in reqTypes:
                gLogger.verbose("Skipping %s request ID %s..." % (req["RequestType"], iD))
                continue
            if not req["RequestState"] in selectStatus:
                gLogger.verbose("Skipping request ID %s in state %s" % (iD, req["RequestState"]))
                continue
            if req["HasSubrequest"]:
                gLogger.verbose("Simulation request %s is a parent, getting subrequests..." % iD)
                subReq = self.productionRequestDB.getProductionRequest([], int(iD))
                if not subReq["OK"]:
                    gLogger.error("Could not get production request for %s" % iD)
                    return subReq
                for sreq in subReq["Value"]["Rows"]:
                    sid = int(sreq["RequestID"])
                    resultDict[sid] = {"reqTotal": sreq["rqTotal"], "bkTotal": sreq["bkTotal"], "master": iD}
            else:
                gLogger.verbose("Simulation request %s is a single request" % iD)
                resultDict[iD] = {"reqTotal": req["rqTotal"], "bkTotal": req["bkTotal"], "master": 0}

        return S_OK(resultDict)

    types_getFilterOptions = []

    def export_getFilterOptions(self):
        """Return the dictionary with possible values for filter."""
        return self.productionRequestDB.getFilterOptions()
