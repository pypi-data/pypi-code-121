###############################################################################
# (c) Copyright 2022 CERN for the benefit of the LHCb Collaboration           #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################
import json
import os
import pytest

from LHCbDIRAC.BookkeepingSystem.DB.DataTakingConditionInterpreter import generateConditionDescription


with open(os.path.join(os.path.dirname(__file__), "dtc.json"), "r") as f:
    allExistingConditions = json.load(f)


KNOWN_TO_DIFFER = {
    "1019-LHCb": "VeloOpen-MagOff-Excl-EC-HC-IT-MU-OT-R1-SP-TT-VE",
    "1019-RICH2": "MagOff",
    "1019-RICH": "MagOff",
    "1024-RICH1": "MagOff",
    "1024-RICH2": "MagOff",
    "1024-RICH": "MagOff",
    "1378-LHCb": "VeloOpen-MagOff-Excl-IT-MU-OT-R1-R2-TT-VE",
    "1516-LHCb": "VeloOpen-MagOff-Excl-EC-HC-IT-MU-OT-R1-R2-SP-TT-VE",
    "1516-MUON": "MagOff",
    "1516-RICH2": "MagOff",
    "1516-TDET": "MagOff",
    "1516-VELOA": "MagOff",
    "1516-VELOC": "MagOff",
    "1516-VELO": "VeloOpen-MagOff",
    "1583-LHCb": "VeloOpen-MagOff-Excl-IT-OT-R1-R2-TT-VE",
    "182-CALO": "MagOff",
    "182-ECAL": "MagOff",
    "182-HCAL": "MagOff",
    "182-HRC": "MagOff",
    "182-IT": "MagOff",
    "182-LHCb": "VeloOpen-MagOff-Excl-EC-HC-MU-OT-R1-R2-SP-TT-VE",
    "182-MUON": "MagOff",
    "182-OT": "MagOff",
    "182-PRS": "MagOff",
    "182-RICH1": "MagOff",
    "182-RICH": "MagOff",
    "182-TDET": "MagOff",
    "182-TT": "MagOff",
    "182-VELOC": "MagOff",
    "200-LHCb": "BeamOff-VeloOpen-MagOff-Excl-EC-HC-IT-MU-OT-R1-R2-SP-TT-VE",
    "200-VELO": "BeamOff-VeloOpen-MagOff",
    "267-LHCb": "VeloOpen-MagOff-Excl-OT-R1-R2-VE",
    "366-RICH1": "BeamOff-MagOff",
    "366-RICH": "BeamOff-MagOff",
    "428095-OT": "BeamOff-MagOff",
    "429155-certification": "Beam3500GeV-MagDown",
    "429155-MC": "Beam3500GeV-MagDown",
    "429155-test": "Beam3500GeV-MagDown",
    "429155-validation": "Beam3500GeV-MagDown",
    "429215-test": "Beam3500GeV-MagUp",
    "429215-validation": "Beam3500GeV-MagUp",
    "429695-FEST": "Beam4000GeV-MagDown",
    "429695-validation": "Beam4000GeV-MagDown",
    "430455-validation": "Beam1380GeV-MagDown",
    "431576-validation": "Beam4000GeV-MagUp",
    "432178-validation": "Beam1380GeV-MagDown",
    "432900-validation": "Beam6500GeV-MagUp",
    "432943-validation": "Beam6500GeV-MagDown",
    "433198-validation": "Beam2510GeV-MagDown",
    "433204-validation": "Beam6370GeV-MagDown",
    "4937-IT": "BeamOff-MagOff",
    "5432-RICH2": "BeamOff-MagOff",
    "5432-RICH": "BeamOff-MagOff",
    "5476-LHCb": "VeloOpen-MagOff-Excl-HC-IT-MU-OT-R1-R2-TT-VE",
    "5687-RICH2": "MagOff",
    "5811-LHCb": "VeloOpen-MagOff-Excl-EC-HC-IT-OT-R1-R2-SP-TT-VE",
    "6136-Fest": "BeamOff-MagOff",
    "6136-FEST": "BeamOff-MagOff",
    "6138-LHCb": "BeamOff-VeloOpen-MagOff-Excl-EC-HC-IT-MU-OT-R1-R2-SP-TT-VE",
    "849-LHCb": "VeloOpen-MagOff-Excl-EC-HC-IT-MU-OT-R1-R2-SP-VE",
    "849-TT": "MagOff",
    "880-RICH2": "MagOff",
    "880-RICH": "MagOff",
    # There was a very special case for when the config name was VELO
    # in which case the Velo position was in the description, as opposed
    # to any other string. Forget about that use case.
    "428095-VELO": "BeamOff-VeloOpen-MagOff",
    "428116-VELO": "BeamOff-VeloOpen-MagOff",
    "6136-VELO": "BeamOff-VeloOpen-MagOff",
}


@pytest.mark.parametrize("dataTakingDict", allExistingConditions)
def test_existingConditions(dataTakingDict):
    """This checks whether the condition descriptions stored
    in the DB can still be generated from the list of sub-detector.
    We know that it is not the case for some of them, even before changing code
    """

    # The json file was obtained by dumping the production DB:
    #
    # select distinct ConfigName, dc.* \
    # from data_taking_conditions dc\
    # JOIN PRODUCTIONSCONTAINER pc on dc.DAQPERIODID = pc.DAQPERIODID \
    # JOIN CONFIGURATIONS c on c.CONFIGURATIONID=pc.CONFIGURATIONID;
    #
    # and then edit it
    #
    # sed -e 's/"it"/"IT"/g' -e 's/"tt"/"TT"/g' -e 's/"ot"/"OT"/g' \
    #     -e 's/"rich1"/"RICH1"/g' -e 's/"rich2"/"RICH2"/g' \
    #     -e 's/spd_prs/SPD_PRS/g' -e 's/"ecal"/"ECAL"/g' \
    #     -e 's/"hcal"/"HCAL"/g' -e 's/"muon"/"MUON"/g' -e 's/"l0"/"L0"/g' \
    #     -e 's/"hlt"/"HLT"/g' -e 's/"veloposition"/"VeloPosition"/g' \
    #     -e 's/configname/ConfigName/g' -e 's/configversion/ConfigVersion/g' \
    #     -e 's/description/Description/g' -e 's/beamcond/BeamCond/g' \
    #     -e 's/beamenergy/BeamEnergy/g' -e 's/magneticfield/MagneticField/g' \
    #     -e 's/"velo"/"VELO"/g' -e 's/configname/ConfigName/g' \
    #     -e 's/configversion/ConfigVersion/g' -e 's/description/Description/g' \
    #     -e 's/beamcond/BeamCond/g' -e 's/beamenergy/BeamEnergy/g' \
    #     -e 's/magneticfield/MagneticField/g' -e 's/"velo"/"VELO"/g'

    configName = dataTakingDict.pop("ConfigName")

    descriptionHash = f"{dataTakingDict['daqperiodid']}-{configName}"

    if descriptionHash in KNOWN_TO_DIFFER:
        pytest.xfail("Known to differ, even in the old system")
    else:
        description = generateConditionDescription(dataTakingDict, configName)
        assert (
            description == dataTakingDict["Description"]
        ), f"{description}, {dataTakingDict['Description']}, {descriptionHash}"
