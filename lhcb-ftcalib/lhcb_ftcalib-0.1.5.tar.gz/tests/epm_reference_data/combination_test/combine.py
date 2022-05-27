datafile  = "../reference.root"
TupleName = "BD_POLY1_MISTAG"
Nmax      = -1

BranchID = "FLAV_DECAY"

OS_Muon_Use            = 1
OS_Muon_BranchDec      = "TOY0_DEC"
OS_Muon_BranchProb     = "TOY0_ETA"
OS_Electron_Use        = 1
OS_Electron_BranchDec  = "TOY1_DEC"
OS_Electron_BranchProb = "TOY1_ETA"
SS_Pion_Use            = 1
SS_Pion_BranchDec      = "TOY2_DEC"
SS_Pion_BranchProb     = "TOY2_ETA"

PerformOfflineCombination_OSplusSS = 1
OS_Muon_InComb                     = 1
OS_Electron_InComb                 = 1
SS_Pion_InComb                     = 1
Combination_Write                  = 1
WriteCalibratedMistagBranches      = 0
CalibratedOutputFile = "combined.root"
