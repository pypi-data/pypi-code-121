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
"""Test_BKK_DB_OracleBookkeepingDB."""
import mock

import LHCbDIRAC.BookkeepingSystem.DB.OracleBookkeepingDB as moduleTested
from LHCbDIRAC.BookkeepingSystem.DB.OracleDB import OracleDB
from DIRAC.ConfigurationSystem.Client.Config import gConfig

# mock_OracleDB = mock.Mock(spec=OracleDB)
testClass = moduleTested.OracleBookkeepingDB
# self.moduleTested.OracleDB = mock_OracleDB

mock_getDatabaseSection = mock.Mock()
mock_getDatabaseSection.return_value = "/Systems/Bookkeeping/Development/Databases/BookkeepingDB"
mock_getDatabaseSection = mock_getDatabaseSection
mock_gConfig = mock.Mock(spec=gConfig)
mock_gConfig.getOption.return_value = {"OK": True, "Value": "exp1"}
mock_gConfig = mock_gConfig.getOption

moduleTested.getDatabaseSection = mock_getDatabaseSection
moduleTested.gConfig.getOption = mock_gConfig
moduleTested.OracleDB = mock.MagicMock()


def test_instantiate():
    """tests that we can instantiate one object of the tested class."""

    module = testClass()
    assert module.__class__.__name__ == "OracleBookkeepingDB"


def test_buildRunNumbers():
    """It test the method which used to build the conditions when runnumbers is
    a list/number, and end run and start run is a number."""
    client = testClass()
    runnumbers = [1, 3, 4]
    startRunID = None
    endRunID = None
    condition = ""
    tables = ""
    retVal = client._buildRunnumbers(runnumbers, startRunID, endRunID, condition, tables)
    assert retVal["OK"] is True
    outVal = " and prview.runnumber=j.runnumber  and  (  j.runnumber=1 or  j.runnumber=3 or  j.runnumber=4 ) "
    assert retVal["Value"] == (outVal, " ,prodrunview prview ,productionscontainer cont")

    startRunID = 1
    retVal = client._buildRunnumbers(runnumbers, startRunID, endRunID, condition, tables)
    assert retVal["OK"] is True
    assert retVal["Value"] == (outVal, " ,prodrunview prview ,productionscontainer cont")

    startRunID = None
    endRunID = 1
    retVal = client._buildRunnumbers(runnumbers, startRunID, endRunID, condition, tables)
    assert retVal["OK"] is True
    assert retVal["Value"] == (outVal, " ,prodrunview prview ,productionscontainer cont")

    startRunID = 1
    endRunID = 2
    runnumbers = [33, 44]
    retVal = client._buildRunnumbers(runnumbers, startRunID, endRunID, condition, tables)
    assert retVal["OK"] is True
    outVal = " and prview.runnumber=j.runnumber  "
    outVal += "and (j.runnumber>=1 and unnumber<=2 or  (  j.runnumber=33 or  j.runnumber=44 ))"
    assert retVal["Value"] == (outVal, " ,prodrunview prview ,productionscontainer cont")

    for i in [[], None]:
        runnumbers = i
        startRunID = 1
        endRunID = 2
        retVal = client._buildRunnumbers(runnumbers, startRunID, endRunID, condition, tables)
        assert retVal["OK"] is True
        assert retVal["Value"] == (" and j.runnumber>=1 and j.runnumber<=2", "")


def test_buildConditions():
    """it test the simulation/data taking condition string creation
    procedure."""
    client = testClass()
    condition = ""
    tables = ""
    for i in [[], None, "ALL"]:
        simdesc = i
        daqdesc = "BeamReal"
        mock_db = mock.Mock(spec=OracleDB)
        mock_db.query.return_value = {"OK": True, "Value": [(1,)]}
        client.dbR_ = mock_db
        retVal = client._buildConditions(simdesc, daqdesc, condition, tables)
        assert retVal["OK"] is True
        assert retVal["Value"] == (
            " and cont.DAQPERIODID=1 and cont.DAQPERIODID is not null ",
            " ,productionscontainer cont ",
        )


#   ################################################################################
#   def test_buildConfiguration(self):
#     """it test the configuration name and version condition string creation."""
#     client = self.testClass()
#     condition = ''
#     tables = ''
#     configName = ''
#     configVersion = ''
#     retVal = client.__buildConfiguration(configName, configVersion, condition, tables)
#     self.assertTrue(retVal['OK'])
#     self.assertTrue(retVal['Value'])
#     self.assertEqual(('', ''), retVal['Value'])

#     configName = 'MC'
#     configVersion = ''
#     retVal = client.__buildConfiguration(configName, configVersion, condition, tables)
#     self.assertTrue(retVal['OK'])
#     self.assertTrue(retVal['Value'])
#     self.assertEqual(('', ''), retVal['Value'])

#     configName = 'MC'
#     configVersion = 'MC11a'
#     retVal = client.__buildConfiguration(configName, configVersion, condition, tables)
#     self.assertTrue(retVal['OK'])
#     self.assertTrue(retVal['Value'])
#     self.assertEqual(("  and c.ConfigName='MC' and c.ConfigVersion='MC11a' \
# and       j.configurationid=c.configurationid ", " ,configurations c"), retVal['Value'])

#   ################################################################################
#   def test_buildDataquality(self):
#     """it test the data quality condition string creation."""
#     client = self.testClass()
#     condition = ''
#     tables = ''
#     mock_db = mock.Mock(spec=OracleDB)
#     mock_db.query.return_value = {'OK': True, 'Value': [(1,)]}
#     client.dbR_ = mock_db
#     for i in ['ALL', None]:
#       dqFlag = i
#       retVal = client.__buildDataquality(dqFlag, condition, tables)
#       self.assertTrue(retVal['OK'])
#       self.assertTrue(retVal['Value'])
#       self.assertEqual(('', ''), retVal['Value'])

#     dqFlag = 'OK'
#     retVal = client.__buildDataquality(dqFlag, condition, tables)
#     self.assertTrue(retVal['OK'])
#     self.assertTrue(retVal['Value'])
#     self.assertEqual((' and f.qualityid=1', ''), retVal['Value'])

#     dqFlag = ['OK', 'UNCHECKED', 'BAD']
#     retVal = client.__buildDataquality(dqFlag, condition, tables)
#     self.assertTrue(retVal['OK'])
#     self.assertTrue(retVal['Value'])
#     self.assertEqual((' and ( f.qualityid=1 or f.qualityid=1 or f.qualityid=1)', ''), retVal['Value'])

#   ################################################################################
#   def test_buildEventType(self):
#     """it test the event type condition string creation."""
#     client = self.testClass()
#     condition = ''
#     tables = ''

#     for i in [0, None, 'ALL']:
#       evt = i
#       retVal = client.__buildEventType(evt, condition, tables)
#       self.assertTrue(retVal['OK'])
#       self.assertTrue(retVal['Value'])
#       self.assertEqual(('', ''), retVal['Value'])

#     evt = 1
#     retVal = client.__buildEventType(evt, condition, tables)
#     self.assertTrue(retVal['OK'])
#     self.assertTrue(retVal['Value'])
#     self.assertEqual((' and f.eventtypeid=1', ''), retVal['Value'])

#     retVal = client.__buildEventType([], condition, tables)
#     self.assertTrue(retVal['OK'])
#     self.assertTrue(retVal['Value'])
#     self.assertEqual(('', ''), retVal['Value'])

#   ################################################################################
#   def test_buildFileTypes(self):
#     """it test the file type condition string creation."""
#     client = self.testClass()
#     condition = ''
#     tables = ''
#     for i in [None, 'ALL']:
#       ft = i
#       retVal = client.__buildFileTypes(ft, condition, tables)
#       self.assertTrue(retVal['OK'])
#       self.assertTrue(retVal['Value'])
#       self.assertEqual(('', ''), retVal['Value'])

#     retVal = client.__buildFileTypes([], condition, tables)
#     self.assertTrue(retVal['Message'])

#   ################################################################################
#   def test_buildProcessingPass(self):
#     """it test the processing pass condition string creation."""
#     client = self.testClass()
#     condition = ''
#     tables = ''
#     mock_db = mock.Mock(spec=OracleDB)
#     mock_db.query.return_value = {'OK': True, 'Value': [(1,)]}
#     client.dbR_ = mock_db

#     for i in [None, 'ALL']:
#       procpass = i
#       retVal = client.__buildProcessingPass(procpass, condition, tables)
#       self.assertTrue(retVal['OK'])
#       self.assertTrue(retVal['Value'])
#       self.assertEqual(('', ''), retVal['Value'])

#     procpass = '/Sim08/Reco01'
#     retVal = client.__buildProcessingPass(procpass, condition, tables)
#     self.assertTrue(retVal['OK'])
#     self.assertTrue(retVal['Value'])
#     self.assertEqual((' and j.production=prod.production\
#                       and prod.processingid in (1)', ',productionscontainer prod'), retVal['Value'])

#     procpass = '/Sim08/Reco01'
#     tables = ',productionscontainer prod'
#     retVal = client.__buildProcessingPass(procpass, condition, tables)
#     self.assertTrue(retVal['OK'])
#     self.assertTrue(retVal['Value'])
#     self.assertEqual((' and j.production=prod.production\
#                       and prod.processingid in (1)', ',productionscontainer prod'), retVal['Value'])

#     mock_db.query.return_value = {'OK': True, 'Value': [(1,), (2,)]}
#     retVal = client.__buildProcessingPass(procpass, condition, tables)
#     self.assertTrue(retVal['OK'])
#     self.assertTrue(retVal['Value'])
#     self.assertEqual((' and j.production=prod.production\
#                       and prod.processingid in (1,2)', ',productionscontainer prod'), retVal['Value'])

#   ################################################################################

#   def test_buildProduction(self):
#     """it test the production condition string creation."""
#     client = self.testClass()
#     condition = ''
#     tables = ''

#     for i in [None, 'ALL', []]:
#       prod = i
#       retVal = client.__buildProduction(prod, condition, tables)
#       self.assertTrue(retVal['OK'])
#       self.assertTrue(retVal['Value'])
#       self.assertEqual(('', ''), retVal['Value'])

#     prod = 1
#     retVal = client.__buildProduction(prod, condition, tables)
#     self.assertTrue(retVal['OK'])
#     self.assertTrue(retVal['Value'])
#     self.assertEqual((' and j.production=1', ''), retVal['Value'])

#     prod = [1, 2]
#     retVal = client.__buildProduction(prod, condition, tables)
#     self.assertTrue(retVal['OK'])
#     self.assertTrue(retVal['Value'])
#     self.assertEqual((' and  (  j.production=1 or  j.production=2 )', ''), retVal['Value'])

#   ################################################################################
#   def test_buildReplicaflag(self):
#     """it test the replica flag condition string creation."""
#     client = self.testClass()
#     condition = ''
#     tables = ',production prod'

#     for i in [None, 'ALL', []]:
#       flag = i
#       retVal = client.__buildReplicaflag(flag, condition, tables)
#       self.assertTrue(retVal['OK'])
#       self.assertTrue(retVal['Value'])
#       self.assertEqual(('', tables), retVal['Value'])

#     flag = 'Yes'
#     retVal = client.__buildReplicaflag(flag, condition, tables)
#     self.assertTrue(retVal['OK'])
#     self.assertTrue(retVal['Value'])
#     self.assertEqual((" and f.gotreplica='Yes' ", tables), retVal['Value'])

#     flag = 'No'
#     retVal = client.__buildReplicaflag(flag, condition, tables)
#     self.assertTrue(retVal['OK'])
#     self.assertTrue(retVal['Value'])
#     self.assertEqual((" and f.gotreplica='No' ", tables), retVal['Value'])

#   ################################################################################
#   def test_buildStartenddate(self):
#     """it test the start and end date condition string creation."""
#     client = self.testClass()
#     condition = ''
#     tables = ',production prod'

#     for i in [None, 'ALL', []]:
#       sDate = i
#       eDate = i
#       retVal = client.__buildStartenddate(sDate, eDate, condition, tables)
#       self.assertTrue(retVal['OK'])
#       self.assertTrue(retVal['Value'])
#       self.assertEqual(('', tables), retVal['Value'])

#     sDate = 1
#     eDate = 2
#     retVal = client.__buildStartenddate(sDate, eDate, condition, tables)
#     self.assertTrue(retVal['OK'])
#     self.assertTrue(retVal['Value'])
#     self.assertEqual((" and f.inserttimestamp >= TO_TIMESTAMP ('1','YYYY-MM-DD HH24:MI:SS') \
# and f.inserttimestamp <= TO_TIMESTAMP ('2','YYYY-MM-DD HH24:MI:SS')", tables), retVal['Value'])

#     sDate = None
#     eDate = 2
#     retVal = client.__buildStartenddate(sDate, eDate, condition, tables)
#     self.assertTrue(retVal['OK'])
#     self.assertTrue(retVal['Value'])
#     self.assertEqual((" and f.inserttimestamp <= TO_TIMESTAMP ('2','YYYY-MM-DD HH24:MI:SS')", tables),
#                      retVal['Value'])

#     sDate = 1
#     eDate = None
#     retVal = client.__buildStartenddate(sDate, eDate, condition, tables)
#     self.assertTrue(retVal['OK'])
#     self.assertTrue(retVal['Value'])
#     condition, tables2 = retVal['Value']
#     self.assertEqual(154, len(condition))  # the current time is returned and can not compared
#     self.assertEqual(tables, tables2)

#   ################################################################################
#   def test_buildTCKS(self):
#     """it test the TCK condition string creation."""
#     client = self.testClass()
#     condition = ''
#     tables = ',production prod'

#     for i in [None, 'ALL']:
#       tcks = i
#       retVal = client.__buildTCKS(tcks, condition, tables)
#       self.assertTrue(retVal['OK'])
#       self.assertTrue(retVal['Value'])
#       self.assertEqual(('', tables), retVal['Value'])

#     tcks = [1]
#     retVal = client.__buildTCKS(tcks, condition, tables)
#     self.assertTrue(retVal['OK'])
#     self.assertTrue(retVal['Value'])
#     self.assertEqual((" and (j.tck='1' ) ", tables), retVal['Value'])

#     tcks = "1"
#     retVal = client.__buildTCKS(tcks, condition, tables)
#     self.assertTrue(retVal['OK'])
#     self.assertTrue(retVal['Value'])
#     self.assertEqual((" and j.tck='1'", tables), retVal['Value'])

#     tcks = [1, 2]
#     retVal = client.__buildTCKS(tcks, condition, tables)
#     self.assertTrue(retVal['OK'])
#     self.assertTrue(retVal['Value'])
#     self.assertEqual((" and (j.tck='1' or j.tck='2' ) ", tables), retVal['Value'])

#     tcks = []
#     retVal = client.__buildTCKS(tcks, condition, tables)
#     self.assertTrue(retVal['OK'])
#     self.assertTrue(retVal['Value'])
#     self.assertEqual(('', tables), retVal['Value'])
