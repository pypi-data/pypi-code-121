from quickstats.utils.enums import GeneralEnum, DescriptiveEnum

class WSVariables(GeneralEnum):
    VARIABLES                         = 0
    OBSERVABLES                       = 1
    POIS                              = 2
    GLOBAL_OBSERVABLES                = 3
    NUISANCE_PARAMETERS               = 4
    CONSTRAINED_NUISANCE_PARAMETERS   = 5
    UNCONSTRAINED_NUISANCE_PARAMETERS = 6
    CONSTRAINTS                       = 7
    AUXILIARY                         = 8
    CORE                              = 9
    NON_CONSTRAINT_VARIABLES          = 10
    
class WSArgument(DescriptiveEnum):
    VARIABLES                         = (0, "All workspace variables")
    OBSERVABLES                       = (1, "Observables")
    POIS                              = (2, "Parameters of Interest")
    GLOBAL_OBSERVABLES                = (3, "Global Observables")
    NUISANCE_PARAMETERS               = (4, "All Nuisance Parameters")
    CONSTRAINED_NUISANCE_PARAMETERS   = (5, "Nuisance Parameters with an associated Constraint Pdfs")
    UNCONSTRAINED_NUISANCE_PARAMETERS = (6, "Nuisance Parameters without an associated Constraint Pdfs")
    CONSTRAINTS                       = (7, "Tuple of Constraint Pdf and the associated Nuisance Parameter and Global Observable")
    AUXILIARY                         = (8, "Auxiliary variables (All variables except POIs, Observables, Global Observables and "
                                            "Nuisance Parameters")
    
    
    
class SetValueMode(GeneralEnum):
    UNCHANGED = 0
    FIX       = 1
    FREE      = 2