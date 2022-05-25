# Copyright (C) 2021- 2022 Cosmo Tech
# This document and all information contained herein is the exclusive property -
# including all intellectual property rights pertaining thereto - of Cosmo Tech.
# Any use, reproduction, translation, broadcasting, transmission, distribution,
# etc., to any person is prohibited unless it has been previously and
# specifically authorized by written means by Cosmo Tech.

from .functionalmodelinterface import FunctionalModelInterface
from .commandlineinterface import CommandLineModelInterface

from ..utilities import get_logger

__all__ = ["FunctionalModelInterface", "CommandLineModelInterface"]

try:
    from .cosmointerface import CosmoInterface, CosmoStepInterface

    __all__.append("CosmoInterface")  # pragma: no cover
    __all__.append("CosmoStepInterface")  # pragma: no cover
except ImportError:  # pragma: no cover
    logger = get_logger(__name__)
    logger.info("Import csm failed, CosmoInterface will not be available")
