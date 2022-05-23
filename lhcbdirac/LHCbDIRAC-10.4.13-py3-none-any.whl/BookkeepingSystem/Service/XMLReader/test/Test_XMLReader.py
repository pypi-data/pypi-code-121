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

import datetime
import pytest
from xml.dom.minidom import parseString
from mock import MagicMock

mockBKDB = MagicMock()
mockBKDB.return_value = None

from DIRAC import gLogger

gLogger.setLevel("DEBUG")

# sut
from LHCbDIRAC.BookkeepingSystem.Service.XMLReader.JobReader import JobReader
from LHCbDIRAC.BookkeepingSystem.Service.XMLReader.XMLFilesReaderManager import XMLFilesReaderManager

xmlString = (
    """<?xml version="1.0" encoding="ISO-8859-1"?>
<!DOCTYPE Job SYSTEM "book.dtd">
<Job ConfigName="test" ConfigVersion="Jenkins" Date="%jDate%" Time="%jTime%">
  <TypedParameter Name="CPUTIME" Type="Info" Value="111222"/>
  <TypedParameter Name="ExecTime" Type="Info" Value="36571.0480781"/>
  <TypedParameter Name="WNMODEL" Type="Info" Value="Intel(R)Xeon(R)CPUE5-2650v2@2.60GHz"/>
  <TypedParameter Name="WNCPUPOWER" Type="Info" Value="1"/>
  <TypedParameter Name="WNCACHE" Type="Info" Value="2593.748"/>
  <TypedParameter Name="WorkerNode" Type="Info" Value="b6bd1ec9ae.cern.ch"/>
  <TypedParameter Name="WNMEMORY" Type="Info" Value="1667656.0"/>
  <TypedParameter Name="WNCPUHS06" Type="Info" Value="11.4"/>
  <TypedParameter Name="Production" Type="Info" Value="12345"/>
  <TypedParameter Name="DiracJobId" Type="Info" Value="147844677"/>
  <TypedParameter Name="Name" Type="Info" Value="00056438_00001025_test_1"/>
  <TypedParameter Name="JobStart" Type="Info" Value="%jStart%"/>
  <TypedParameter Name="JobEnd" Type="Info" Value="%jEnd%"/>
  <TypedParameter Name="Location" Type="Info" Value="LCG.CERN.ch"/>
  <TypedParameter Name="JobType" Type="Info" Value="MCSimulation"/>
  <TypedParameter Name="ProgramName" Type="Info" Value="Gauss"/>
  <TypedParameter Name="ProgramVersion" Type="Info" Value="v49r5"/>
  <TypedParameter Name="DiracVersion" Type="Info" Value="v6r15p9"/>
  <TypedParameter Name="FirstEventNumber" Type="Info" Value="1"/>
  <TypedParameter Name="StatisticsRequested" Type="Info" Value="-1"/>
  <TypedParameter Name="StepID" Type="Info" Value="123"/>
  <TypedParameter Name="NumberOfEvents" Type="Info" Value="411"/>
  <OutputFile Name="/lhcb/MC/2012/SIM/00056438/0000/00056438_00001025_test_1.sim" TypeName="SIM" TypeVersion="ROOT">
          <Parameter Name="EventTypeId" Value="11104131"/>
          <Parameter Name="EventStat" Value="411"/>
          <Parameter Name="FileSize" Value="862802861"/>
          <Parameter Name="MD5Sum" Value="ae647981ea419cc9f8e8fa0a2d6bfd3d"/>
          <Parameter Name="Guid" Value="546014C4-55C6-E611-8E94-02163E00F6B2"/>
  </OutputFile>
  <OutputFile Name="/lhcb/MC/2012/LOG/00056438/0000/00001025/Gauss_00056438_00001025_test_1.log" """
    + """TypeName="LOG" TypeVersion="1">
          <Parameter Name="FileSize" Value="319867"/>
          <Replica Location="Web" Name="http://lhcb-logs.cern.ch/"""
    + """storage/lhcb/MC/2012/LOG/00056438/0000/00001025/Gauss_00056438_00001025_test_1.log"/>
          <Parameter Name="MD5Sum" Value="e4574c9083d1163d43ba6ac033cbd769"/>
          <Parameter Name="Guid" Value="E4574C90-83D1-163D-43BA-6AC033CBD769"/>
  </OutputFile>
  <SimulationCondition>
          <Parameter Name="SimDescription" Value="Beam4000GeV-2012-MagUp-Nu2.5-Pythia8"/>
  </SimulationCondition>
</Job>
"""
)


def test_JobReader():

    currentTime = datetime.datetime.now()
    jobStart = jobEnd = datetime.datetime.now()
    jobStart = jobEnd = jobStart.replace(second=0, microsecond=0)
    xml = xmlString.replace("%jDate%", currentTime.strftime("%Y-%m-%d"))
    xml = xml.replace("%jTime%", currentTime.strftime("%H:%M"))
    xml = xml.replace("%jStart%", jobStart.strftime("%Y-%m-%d %H:%M"))
    xml = xml.replace("%jEnd%", jobEnd.strftime("%Y-%m-%d %H:%M"))
    doc = parseString(xml)

    job = JobReader().readJob(doc, "IN Memory")
    assert job.configuration.configName == "test"
    assert job.configuration.configVersion == "Jenkins"
    assert len(job.outputFiles) == 2
    assert job.outputFiles[0].name == "/lhcb/MC/2012/SIM/00056438/0000/00056438_00001025_test_1.sim"
    assert job.outputFiles[0].type == "SIM"
    assert job.outputFiles[0].params[1].value == "411"
    assert len(job.parameters) == 22
    assert job.parameters[0].name == "CPUTIME"
    assert job.parameters[0].value == "111222"
    assert job.simulationCondition.parameters["SimDescription"] == "Beam4000GeV-2012-MagUp-Nu2.5-Pythia8"


@pytest.mark.parametrize(
    "inputfiles, getRunNbAndTckRV, expected",
    [
        ([], {"OK": True}, {"OK": True, "Value": (set(), set())}),
        (["aa"], {"OK": True, "Value": [(None, "None")]}, {"OK": True, "Value": (set(), set())}),
        (["aa"], {"OK": False, "Message": "bof"}, {"OK": False, "Message": "bof"}),
        (["aa", "bb"], {"OK": True, "Value": [(123, "None")]}, {"OK": True, "Value": ({123}, set())}),
        (["aa", "bb"], {"OK": True, "Value": [(123, "x123")]}, {"OK": True, "Value": ({123}, {"x123"})}),
    ],
)
def test__getRunNumbersAndTCKs(mocker, inputfiles, getRunNbAndTckRV, expected):
    mocker.patch(
        "LHCbDIRAC.BookkeepingSystem.Service.XMLReader.XMLFilesReaderManager.OracleBookkeepingDB.__init__",
        side_effect=mockBKDB,
    )
    xfrm = XMLFilesReaderManager()
    xfrm.bkClient_ = MagicMock()
    xfrm.bkClient_.getRunNbAndTck.return_value = getRunNbAndTckRV

    res = xfrm._getRunNumbersAndTCKs(inputfiles)
    assert res == expected


@pytest.mark.parametrize(
    "prod, runNumber, getProductionProcessingPassID_RV, getRunAndProcessingPassDataQuality_RV, expected",
    [
        (None, None, {"OK": True}, {"OK": True}, {"OK": True, "Value": None}),
        (None, 123, {"OK": True, "Value": None}, {"OK": True}, {"OK": True, "Value": None}),
        (None, 123, {"OK": True, "Value": 1}, {"OK": True, "Value": None}, {"OK": True, "Value": None}),
        (None, 123, {"OK": True, "Value": 1}, {"OK": True, "Value": "OK"}, {"OK": True, "Value": "OK"}),
        (None, 123, {"OK": False, "Message": "NOK"}, {"OK": True, "Value": "OK"}, {"OK": False, "Message": "NOK"}),
        (None, 123, {"OK": True, "Value": "OK"}, {"OK": False, "Message": "NOK"}, {"OK": False, "Message": "NOK"}),
        (321, 123, {"OK": True, "Value": 1}, {"OK": True, "Value": "UNCHECKED"}, {"OK": True, "Value": "UNCHECKED"}),
    ],
)
def test__getDataQuality(
    mocker, prod, runNumber, getProductionProcessingPassID_RV, getRunAndProcessingPassDataQuality_RV, expected
):
    mocker.patch(
        "LHCbDIRAC.BookkeepingSystem.Service.XMLReader.XMLFilesReaderManager.OracleBookkeepingDB.__init__",
        side_effect=mockBKDB,
    )
    xfrm = XMLFilesReaderManager()
    xfrm.bkClient_ = MagicMock()
    xfrm.bkClient_.getProductionProcessingPassID.return_value = getProductionProcessingPassID_RV
    xfrm.bkClient_.getRunAndProcessingPassDataQuality.return_value = getRunAndProcessingPassDataQuality_RV

    res = xfrm._getDataQuality(prod, runNumber)
    assert res == expected
