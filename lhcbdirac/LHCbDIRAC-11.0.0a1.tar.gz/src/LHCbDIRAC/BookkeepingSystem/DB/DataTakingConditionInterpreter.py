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
"""interpret the data taking conditions."""


SUBDETECTOR_SHORT_NAMES = {
    "ECAL": "EC",
    "HCAL": "HC",
    "MUON": "MU",
    "PLUME": "PL",
    "RICH1": "R1",
    "RICH2": "R2",
    "SCIFI": "SF",
    "SPD_PRS": "SP",
    "TDET": "TD",
    "VELO": "VE",
}


# For some reason, there are runs that were registered
# with this energy or greater, and where the beam should be
# considered off in the description...
MAX_BEAM_ENERGY = 7864


def generateConditionDescription(dataTakingDict: dict[str, str], configName: str) -> str:
    """Based on the sub detector status and the configuration name (partition),
    generate a condition description string.

    Rules:

    * If the partition is LHCb:
      <BeamEnergy>-<VeloPosition>-<MagPolarity>(-Excl-<list of excluded subdetectors>)

    * else:
      <BeamEnergy>-<MagPolarity>

    """

    beamEnergyDesc = "BeamOff"

    try:

        beamEnergyInt = int(float(dataTakingDict.get("BeamEnergy", "0").strip()))
        if 0 < beamEnergyInt < MAX_BEAM_ENERGY:
            beamEnergyDesc = f"Beam{beamEnergyInt}GeV"
    # Raised if it is not a number
    except ValueError:
        pass

    magPolarityDesc = f"Mag{dataTakingDict['MagneticField'].capitalize()}"

    if configName == "LHCb":
        veloPositionDesc = f"Velo{dataTakingDict['VeloPosition'].capitalize()}"

        excludedSubDetectors = []
        # Check all the excluded sub detectors
        for subDetector, subDetectorStatus in dataTakingDict.items():
            # The L0 trigger can be included or not, but it is not
            # a subdetector so skip it
            if subDetector == "L0":
                continue
            if subDetectorStatus == "NOT INCLUDED":
                excludedSubDetectors.append(SUBDETECTOR_SHORT_NAMES.get(subDetector, subDetector))

        descriptionParameters = [beamEnergyDesc, veloPositionDesc, magPolarityDesc]
        if excludedSubDetectors:
            excludedSubDetectorDesc = "Excl-" + "-".join(sorted(excludedSubDetectors))
            descriptionParameters.append(excludedSubDetectorDesc)

    else:
        descriptionParameters = [beamEnergyDesc, magPolarityDesc]

    return "-".join(descriptionParameters)
