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
"""UploadMC module is used to upload to ES the json files for MC statistics."""
import os
import io
import json

import six
from DIRAC import S_OK, S_ERROR, gLogger

import LHCbDIRAC
from LHCbDIRAC.Workflow.Modules.ModuleBase import ModuleBase
from LHCbDIRAC.ProductionManagementSystem.Client.MCStatsClient import MCStatsClient
from LHCbDIRAC.Core.Utilities.XMLSummaries import XMLSummary
from LHCbDIRAC.Core.Utilities.GeneratorLog import GeneratorLog


class UploadMC(ModuleBase):
    """Upload to LogSE."""

    def __init__(self):
        """Module initialization."""

        self.log = gLogger.getSubLogger("UploadMC")
        super(UploadMC, self).__init__(self.log)

        self.version = LHCbDIRAC.version

    def _resolveInputVariables(self):
        """standard method for resolving the input variables."""

        super(UploadMC, self)._resolveInputVariables()

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
        """Main executon method.

        Takes care of indexing JSON files on ElasticSearch databases
        All these uploads are controlled by flags that can be found in
        'Operations/<setup>/Productions/'

        1) Gauss errors => /Operations/<setup>/Productions/UploadES_GaussErrors (default: True)
        2) Boole errors => /Operations/<setup>/Productions/UploadES_BooleErrors (default: True)
        3) Summary.xml -> JSON => /Operations/<setup>/Productions/UploadES_XMLSummary (default: False)
        4) GeneratorLog.xml -> JSON => /Operations/<setup>/Productions/UploadES_GeneratorLog (default: False)
        5) PRMon => /Operations/<setup>/Productions/UploadES_PrMon (default: False)

        """
        try:

            super(UploadMC, self).execute(
                self.version,
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

            self._resolveInputVariables()

            mcStatsClient = MCStatsClient()

            # DBs list
            # db = {
            #     'XMLSummary': elasticApplicationSummaryDB,
            #     'booleErrors': elasticMCBooleLogErrorsDB,
            #     'gaussErrors': elasticMCGaussLogErrorsDB,
            #     'generatorLog': elasticMCGeneratorLogDB,
            #     'prMon': elasticMCGeneratorLogDB,
            # }

            # 1) MC Gauss errors
            # looking for json files that are 'self.jobID_Errors_Gauss.json'
            fn = "%s_Errors_Gauss.json" % (self.jobID)
            if os.path.exists(fn):
                with io.open(fn) as fd:
                    try:
                        jsonData = json.load(fd)
                        self.log.verbose("Content of JSON file", "%s: %s" % (fn, jsonData))
                        if self._enableModule() and self.opsH.getValue("Productions/UploadES_GaussErrors", True):
                            res = mcStatsClient.set("gaussErrors", jsonData)
                            if not res["OK"]:
                                self.log.error(
                                    "MC Error data not set, exiting without affecting workflow status",
                                    "%s: %s" % (str(jsonData), res["Message"]),
                                )
                        else:
                            # At this point we can see exactly what the module would have uploaded
                            self.log.info(
                                "Module disabled", "would have attempted to upload the following file %s" % fn
                            )
                    except Exception as ve:
                        self.log.error(repr(ve))
                        self.log.verbose("Exception loading the JSON file: content of %s follows" % fn)
                        self.log.verbose(fd.read)
                        # do not fail the job for this
                        # raise
            else:
                self.log.info("Gauss errors JSON file not found", fn)

            # 2) MC Boole errors
            # looking for json files that are 'self.jobID_Errors_Boole.json'
            fn = "%s_Errors_Boole.json" % (self.jobID)
            if os.path.exists(fn):
                with io.open(fn) as fd:
                    try:
                        jsonData = json.load(fd)
                        self.log.verbose("Content of JSON file", "%s: %s" % (fn, jsonData))
                        if self._enableModule() and self.opsH.getValue("Productions/UploadES_BooleErrors", True):
                            res = mcStatsClient.set("booleErrors", jsonData)
                            if not res["OK"]:
                                self.log.error(
                                    "MC Error data not set, exiting without affecting workflow status",
                                    "%s: %s" % (str(jsonData), res["Message"]),
                                )
                        else:
                            # At this point we can see exactly what the module would have uploaded
                            self.log.info(
                                "Module disabled", "would have attempted to upload the following file %s" % fn
                            )
                    except Exception as ve:
                        self.log.error(repr(ve))
                        self.log.verbose("Exception loading the JSON file: content of %s follows" % fn)
                        self.log.verbose(fd.read)
                        # do not fail the job for this
                        # raise
            else:
                self.log.info("Boole errors JSON file not found", fn)

            # 3) summary JSON files
            # looking for xml files that are 'summaryGauss_self.production_id_self.prod_job_id_1.xml'
            xmlfl = "summaryGauss_%s_%s_1.xml" % (self.production_id, self.prod_job_id)
            if os.path.exists(xmlfl):

                try:
                    xmlData = XMLSummary(xmlfl)
                    xmlData.xmltojson()
                    # At this point 'summaryGauss_self.production_id_self.prod_job_id_1.json' should have been created
                    jsonfl = "summaryGauss_%s_%s_1.json" % (self.production_id, self.prod_job_id)
                    with io.open(jsonfl) as JS:
                        jsonData = json.load(JS)
                        ids = dict()
                        ids["JobID"] = self.jobID
                        ids["ProductionID"] = self.production_id
                        ids["prod_job_id"] = self.prod_job_id
                        jsonData["Counters"]["ID"] = ids
                        with io.open(jsonfl, "w", encoding="utf-8") as output:
                            output.write(six.text_type(json.dumps(jsonData, indent=2)))

                        self.log.verbose("Content of JSON file", "%s: %s" % (jsonfl, jsonData))
                        if self._enableModule() and self.opsH.getValue("Productions/UploadES_XMLSummary", False):
                            res = mcStatsClient.set("XMLSummary", jsonData)
                            if not res["OK"]:
                                self.log.error(
                                    "Gauss Summaries data not set, exiting without affecting workflow status",
                                    "%s: %s" % (str(jsonData), res["Message"]),
                                )
                        else:
                            # At this point we can see exactly what the module would have uploaded
                            self.log.info(
                                "Module disabled", "would have attempted to upload the following file %s" % jsonfl
                            )

                except Exception:
                    self.log.exception("Exception creating/loading the XMLSummary JSON file")
                    # do not fail the job for this

            else:
                self.log.info("XML Gauss summary file not found", xmlfl)

            # 4) Generator logs
            # looking for xml files that are 'GeneratorLog.xml'
            xmlfile = "GeneratorLog.xml"
            if os.path.exists(xmlfile):

                try:
                    jsonfile = "GeneratorLog_%s_%s.json" % (self.production_id, self.prod_job_id)
                    xmlData = GeneratorLog()
                    xmlData.generatorLogJson(jsonfile)
                    # At this point 'GeneratorLog_self.production_id_self.prod_job_id.json' should have been created
                    with io.open(jsonfile) as JS:
                        jsonData = json.load(JS)
                        ids = dict()
                        ids["JobID"] = self.jobID
                        ids["ProductionID"] = self.production_id
                        ids["prod_job_id"] = self.prod_job_id
                        jsonData["generatorCounters"]["ID"] = ids
                        with io.open(jsonfile, "w", encoding="utf-8") as output:
                            output.write(six.text_type(json.dumps(jsonData)))

                        self.log.verbose("Content of JSON file", "%s: %s" % (jsonfile, jsonData))
                        if self._enableModule() and self.opsH.getValue("Productions/UploadES_GeneratorLog", False):
                            res = mcStatsClient.set("generatorLog", jsonData)
                            if not res["OK"]:
                                self.log.error(
                                    "Generator Log data not set, exiting without affecting workflow status",
                                    "%s: %s" % (str(jsonData), res["Message"]),
                                )
                        else:
                            # At this point we can see exactly what the module would have uploaded
                            self.log.info(
                                "Module disabled", "would have attempted to upload the following file %s" % jsonfile
                            )

                except Exception:
                    self.log.exception("Exception creating/loading the GeneratorLog JSON file")
                    # do not fail the job for this

            else:
                self.log.info("XML GeneratorLog file not found", xmlfile)

            # 5) PRmon JSON files (only for Gauss)
            # looking for prmon files that are 'prmon_Gauss.json'
            prmonFile = "prmon_Gauss.json"
            if os.path.exists(prmonFile):
                with io.open(prmonFile) as JS:
                    try:
                        jsonData = json.load(JS)
                        jsonData["JobID"] = self.jobID
                        jsonData["ProductionID"] = self.production_id
                        jsonData["prod_job_id"] = self.prod_job_id
                        self.log.verbose("Content of JSON file", "%s: %s" % (prmonFile, jsonData))
                        if self._enableModule() and self.opsH.getValue("Productions/UploadES_PrMon", False):
                            res = mcStatsClient.set("prMon", jsonData)
                            if not res["OK"]:
                                self.log.error(
                                    "prmon Metrics data not set, exiting without affecting workflow status",
                                    "%s: %s" % (str(jsonData), res["Message"]),
                                )
                        else:
                            # At this point we can see exactly what the module would have uploaded
                            self.log.info(
                                "Module disabled", "would have attempted to upload the following file %s" % prmonFile
                            )
                    except Exception as ve:
                        self.log.error(repr(ve))
                        self.log.verbose("Exception loading the JSON file: content of %s follows" % prmonFile)
                        self.log.verbose(JS.read())
                        # do not fail the job for this
                        # raise
            else:
                self.log.info("prmon JSON file not found", prmonFile)

            return S_OK()

        except Exception as e:
            self.log.exception("Failure in UploadMC execute module", lException=e)
            return S_ERROR(repr(e))

        finally:
            super(UploadMC, self).finalize(self.version)
