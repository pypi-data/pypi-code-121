
from typing import List, Type

from .base import Command
from .mchgc import MCHGC
from .mnchgc import MNCHGC_Parallel, MNCHGC_Single
from .muchgc import MUCHGC_Single, MUCHGC_Parallel
from .pbatmaxdisc import PBATMAXDISC
from .pbcv import PBCV
from .pbdv import PBDV
from .pbft import PBFT
from .pbt import PBT
from .pcp import PCP
from .pcvv import PCVV
from .pop import POP
from .psdv import PSDV
from .qmchgcr import QMCHGCR
from .qmuchgcr import QMUCHGCR
from .qmod import QMOD
from .qpigs import QPIGS, QPIGS_LV, QPIGS_GKMK, QPIGS_MAX
from .qpigs2 import QPIGS2, QPIGS2_MAX
from .qpiri import QPIRI, QPIRI_GK, QPIRI_MAX, QPIRI_MK


COMMANDS_BY_MODEL = {
    'GK': [
        MNCHGC_Single,
        MUCHGC_Single,
        PBCV,
        PBDV,
        PBFT,
        PBT,
        PCP,
        PCVV,
        POP,
        PSDV,
        QMCHGCR,
        QMUCHGCR,
        QMOD,
        QPIGS_GKMK,
        QPIRI_GK,
    ],
    'LV': [
        MNCHGC_Single,
        PBCV,
        PBDV,
        PBFT,
        PBT,
        PCP,
        PCVV,
        POP,
        PSDV,
        QMCHGCR,
        QMOD,
        QPIGS_LV,
    ],
    'MAX': [
        MCHGC,
        MNCHGC_Parallel,
        MUCHGC_Parallel,
        PBATMAXDISC,
        PBCV,
        PBDV,
        PBFT,
        PBT,
        PCP,
        PCVV,
        POP,
        PSDV,
        QMCHGCR,
        QMOD,
        QMUCHGCR,
        QPIGS_MAX,
        QPIGS2_MAX,
        QPIRI_MAX,
    ],
    'MK': [
        MNCHGC_Parallel,
        MUCHGC_Parallel,
        PBCV,
        PBDV,
        PBFT,
        PBT,
        PCP,
        PCVV,
        POP,
        PSDV,
        QMCHGCR,
        QMOD,
        QPIGS_GKMK,
        QPIRI_MK,
    ],
}


def get_command_classes(model: str) -> List[Type[Command]]:
    return COMMANDS_BY_MODEL.get(model, [])
