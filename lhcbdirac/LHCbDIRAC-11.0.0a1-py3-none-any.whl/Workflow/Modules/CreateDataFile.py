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
"""Prepare a file (data.py) which is consumed by Ganga, containing the input
files as resolved in the workflow."""

from DIRAC import S_OK, S_ERROR, gLogger

from LHCbDIRAC.Workflow.Modules.ModuleBase import ModuleBase
from LHCbDIRAC.Core.Utilities.GangaDataFile import GangaDataFile


class CreateDataFile(ModuleBase):
    """CreateDataFile class."""

    def __init__(self, bkClient=None, dm=None):
        """simple init."""

        self.log = gLogger.getSubLogger("CreateDataFile")

        super(CreateDataFile, self).__init__(self.log, bkClientIn=bkClient, dm=dm)

        self.gangaFileName = "data.py"
        self.poolXMLCatName = "pool_xml_catalog.xml"
        self.persistency = ""

    def _resolveInputVariables(self):
        """By convention the module parameters are resolved here."""

        super(CreateDataFile, self)._resolveInputVariables()
        super(CreateDataFile, self)._resolveInputStep()

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
        gdf=None,
    ):
        """Just calls GangaDataFile with some parameter."""

        try:

            super(CreateDataFile, self).execute(
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

            if not self._checkWFAndStepStatus():
                return S_OK()

            self._resolveInputVariables()

            if not gdf:
                gdf = GangaDataFile(fileName=self.gangaFileName, xmlcatalog_file=self.poolXMLCatName, log=self.log)

            if not self.inputDataList:
                return S_OK("No data file generated, because no inputs set")

            gdf.generateDataFile(self.inputDataList, persistency=self.persistency)

            return S_OK()

        except Exception as e:  # pylint:disable=broad-except
            self.log.exception("Failure in CreateDataFile execute module", lException=e)
            return S_ERROR(str(e))

        finally:
            super(CreateDataFile, self).finalize()
