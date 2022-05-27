OS_Muon_CalibrationArchive     = "OS_Muon_Calibration.xml"
OS_Electron_CalibrationArchive = "OS_Electron_Calibration.xml"
SS_Pion_CalibrationArchive     = "SS_Pion_Calibration.xml"
datafile  = "../reference.root"
TupleName = "BD_POLY1_MISTAG"
DoCalibrations = 0

CalibrationMode   = "Bd"
CalibrationLink   = "LOGIT"
CalibrationDegree = 4
CalibrationModel  = "NSPLINE"
UseNewtonRaphson  = 0

TauUnits  = "ps"
UseTau    = 1
BranchTau = "TAU"

BranchID = "FLAV_DECAY"

OS_Muon_Use            = 1
OS_Muon_Write          = 1
OS_Muon_BranchDec      = "TOY0_DEC"
OS_Muon_BranchProb     = "TOY0_ETA"
OS_Electron_Use        = 1
OS_Electron_Write      = 1
OS_Electron_BranchDec  = "TOY1_DEC"
OS_Electron_BranchProb = "TOY1_ETA"
SS_Pion_Use            = 1
SS_Pion_Write          = 1
SS_Pion_BranchDec      = "TOY2_DEC"
SS_Pion_BranchProb     = "TOY2_ETA"
WriteCalibratedMistagBranches = 1
CalibratedOutputFile = "output.root"
