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
""" Analyse XMLSummary module and PoolCatalog in order to monitor the files access
    We send data to the accounting (Site -> SE : fail/success)
"""

from collections import defaultdict

from DIRAC import S_OK, S_ERROR, gLogger
from DIRAC.AccountingSystem.Client.Types.DataOperation import DataOperation
from DIRAC.Resources.Catalog.PoolXMLCatalog import PoolXMLCatalog
from LHCbDIRAC.Core.Utilities.XMLSummaries import XMLSummary, XMLSummaryError
from LHCbDIRAC.Workflow.Modules.ModuleBase import ModuleBase


class AnalyseFileAccess(ModuleBase):
    """Analyzing the access with xroot"""

    def __init__(self, bkClient=None, dm=None):
        """Module initialization."""

        self.log = gLogger.getSubLogger("AnalyseFileAccess")
        super(AnalyseFileAccess, self).__init__(self.log, bkClientIn=bkClient, dm=dm)

        self.XMLSummary = ""
        self.XMLSummary_o = None
        self.poolXMLCatName = ""
        self.poolXMLCatName_o = None
        self.dsc = None

    def _resolveInputVariables(self):
        """By convention any workflow parameters are resolved here."""

        super(AnalyseFileAccess, self)._resolveInputVariables()
        super(AnalyseFileAccess, self)._resolveInputStep()

        self.XMLSummary_o = XMLSummary(self.XMLSummary, log=self.log)
        self.dsc = self.workflow_commons["AccountingReport"]
        self.poolXMLCatName_o = PoolXMLCatalog(xmlfile=self.poolXMLCatName)

    def execute(
        self,
        production_id=None,
        prod_job_id=None,
        wms_job_id=None,
        workflowStatus=None,
        stepStatus=None,
        wf_commons=None,
        step_commons=None,
        step_number=None,
        step_id=None,
    ):
        """Main execution method.

        Here we analyse what is written in the XML summary and the pool XML, and send accounting
        """

        try:
            super(AnalyseFileAccess, self).execute(
                production_id,
                prod_job_id,
                wms_job_id,
                workflowStatus,
                stepStatus,
                wf_commons,
                step_commons,
                step_number,
                step_id,
            )

            try:
                self._resolveInputVariables()
            except XMLSummaryError as e:
                if e.message == "XML Summary Not Available":
                    self.log.warn("XML summary not created, skipping this module")
                    return S_OK()
                else:
                    raise e

            self.log.info("Analyzing root access from %s and %s" % (self.XMLSummary, self.poolXMLCatName))

            accessAttempts = self._checkFileAccess(self.poolXMLCatName_o, self.XMLSummary_o)

            if not self._enableModule():
                self.log.info("Not enabled")
                return S_OK()

            for remoteSE, success in accessAttempts:
                oDataOperation = self.__initialiseAccountingObject(remoteSE, success)
                self.dsc.addRegister(oDataOperation)

            return S_OK()

        except Exception as e:  # pylint:disable=broad-except
            self.log.exception("Failure in AnalyseFileAccess execute module", lException=e)
            self.setApplicationStatus(e)
            return S_ERROR(str(e))

        finally:
            super(AnalyseFileAccess, self).finalize()

    @staticmethod
    def _checkFileAccess(xmlCatalog, xmlSummary):
        """Given an xmlCatalog and an xmlSummary, check which were the successful and failed attempts
        to open remote root files

        For each attempts, we return a tuple (srcSE, flag) with the flag being true if the read was successful.

        :param xmlCatalog: instance of :py:class:`~LHCbDIRAC.Resources.Catalog.PoolXMLCatalog.PoolXMLCatalog`
        :param xmlSummary: instance of :py:class:`~LHCbDIRAC.LHCbDIRAC.Core.Utilities.XMLSummaries.XMLSummary`

        :returns: list of tuples (srcSE, successful flag)
        """

        # This will contain the list of tuples with the accesses and their status
        accessAttempts = []

        # Used to cache the information PFN -> SE from the catalog
        pfn_se = {}
        # Used to cache the information LFN -> PFN from the catalog
        lfn_pfn = defaultdict(list)

        # Matching between a PFN and the LFN
        pfn_lfn = {}

        # {LFN: failed PFN}
        lfn_pfn_fail = defaultdict(list)

        # Build all the caches
        for guid in xmlCatalog.files:
            pFile = xmlCatalog.files[guid]
            lfn = pFile.lfns[0]  # there can be only one
            for pfn, _ftype, se in pFile.pfns:
                pfn_lfn[pfn] = lfn
                pfn_se[pfn] = se
                lfn_pfn[lfn].append(pfn)

        # Check the URLs that failed, and associate them with their LFNs
        for pfn, _status in xmlSummary.failedInputURL:
            # The name starts with 'PFN:'
            pfn = pfn[4:]
            # Find the matching LFN
            lfn = pfn_lfn[pfn]
            lfn_pfn_fail[lfn].append(pfn)

        # For each PFN in the lfn_pfn_fail dictionnary, we will count a failure.
        for lfn, failedPfns in lfn_pfn_fail.items():
            # We add the accounting for the failure
            for pfn in failedPfns:
                remoteSE = pfn_se[pfn]
                accessAttempts.append((remoteSE, False))

        # To find the successful access, we take the next available replicas if any.
        # If the LFN is not in the lfn_pfn_fail dict, that means the first attempt was successful
        # If there are no more replicas to be tried, then the LFN was never read.

        for lfn, replicaList in lfn_pfn.items():
            # get the index of the successful replicas
            succRepIndex = len(lfn_pfn_fail.get(lfn, []))
            try:
                succRep = replicaList[succRepIndex]
                remoteSE = pfn_se[succRep]
                accessAttempts.append((remoteSE, True))
            # This happens if all the replicas failed
            except IndexError:
                pass

        return accessAttempts

    def __initialiseAccountingObject(self, srcSE, successful):
        """create accouting record"""
        accountingDict = {}

        accountingDict["OperationType"] = "fileAccess"
        accountingDict["User"] = self._getCurrentOwner()
        accountingDict["Protocol"] = "xroot"
        accountingDict["RegistrationTime"] = 0.0
        accountingDict["RegistrationOK"] = 0
        accountingDict["RegistrationTotal"] = 0
        accountingDict["Source"] = srcSE
        accountingDict["TransferTotal"] = 1
        accountingDict["TransferOK"] = 1 if successful else 0
        accountingDict["TransferSize"] = 0
        accountingDict["TransferTime"] = 0.0
        accountingDict["FinalStatus"] = "Successful" if successful else "Failed"
        accountingDict["Destination"] = self.siteName
        oDataOperation = DataOperation()
        oDataOperation.setValuesFromDict(accountingDict)

        if "StartTime" in self.step_commons:
            oDataOperation.setStartTime(self.step_commons["StartTime"])
            oDataOperation.setEndTime()

        return oDataOperation
