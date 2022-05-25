# Copyright (C) 2021- 2022 Cosmo Tech
# This document and all information contained herein is the exclusive property -
# including all intellectual property rights pertaining thereto - of Cosmo Tech.
# Any use, reproduction, translation, broadcasting, transmission, distribution,
# etc., to any person is prohibited unless it has been previously and
# specifically authorized by written means by Cosmo Tech.

from .core import (
    Task,
    FunctionalTask,
    ParallelManager,
    ModelInterface,
    StepModelInterface,
    ModelTask,
    Experiment,
    ParameterSet,
    StopCriteria,
    Space,
    Variable,
)

from .modelinterfaces import (
    FunctionalModelInterface,
    CommandLineModelInterface,
)


from .utilities import set_logging_level, get_logger, Registry

from .experiments import (
    CompositeSampling,
    CustomSampling,
    Distribution,
    DistributionRegistry,
    DistributionSampling,
    GeneratorRegistry,
    Optimization,
    CMAES,
    OpenES,
    OptimizationAlgorithmRegistry,
    UncertaintyAnalysis,
    SensitivityAnalysis,
    SequenceRegistry,
    StatisticsRegistry,
    SurrogateModeling,
    SurrogateRegistry,
    ParameterSweep,
    ReinforcementLearningEnvironment,
)


__all__ = [
    "Task",
    "FunctionalTask",
    "ParallelManager",
    "ModelInterface",
    "StepModelInterface",
    "FunctionalModelInterface",
    "CommandLineModelInterface",
    "ModelTask",
    "Experiment",
    "StopCriteria",
    "ParameterSet",
    "Space",
    "Variable",
    "set_logging_level",
    "get_logger",
    "CompositeSampling",
    "CustomSampling",
    "Distribution",
    "DistributionRegistry",
    "DistributionSampling",
    "GeneratorRegistry",
    "Optimization",
    "OptimizationAlgorithmRegistry",
    "UncertaintyAnalysis",
    "SensitivityAnalysis",
    "SequenceRegistry",
    "StatisticsRegistry",
    "SurrogateModeling",
    "SurrogateRegistry",
    "ParameterSweep",
    "ReinforcementLearningEnvironment",
]

try:  # pragma: no cover
    from .modelinterfaces import CosmoInterface, CosmoStepInterface

    __all__.append("CosmoInterface")
    __all__.append("CosmoStepInterface")
except ImportError:  # pragma: no cover
    pass
