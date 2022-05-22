from enum import Enum
from typing import List, Optional

import pydantic

from classiq.interface.chemistry import molecule


class FermionMapping(str, Enum):
    JORDAN_WIGNER = "jordan_wigner"
    PARITY = "parity"
    BRAVYI_KITAEV = "bravyi_kitaev"
    FAST_BRAVYI_KITAEV = "fast_bravyi_kitaev"


class GroundStateProblem(pydantic.BaseModel):
    molecule: molecule.Molecule
    basis: str = pydantic.Field(default="sto3g", description="Molecular basis set")
    mapping: FermionMapping = pydantic.Field(
        default=FermionMapping.JORDAN_WIGNER, description="Fermionic mapping type"
    )
    freeze_core: Optional[bool] = pydantic.Field(default=False)
    remove_orbitals: Optional[List[int]] = pydantic.Field(
        default=None, description="list of orbitals to remove"
    )
    z2_symmetries: bool = pydantic.Field(
        default=False,
        description="whether to perform z2 symmetries reduction",
    )

    @pydantic.validator("z2_symmetries")
    def validate_z2_symmetries(cls, value, values):
        if value and values.get("mapping") == FermionMapping.FAST_BRAVYI_KITAEV:
            raise ValueError(
                "z2 symmetries reduction can not be used for fast_bravyi_kitaev mapping"
            )
        return value
