from typing import List, Optional

import pydantic

from classiq.interface.chemistry.elements import ELEMENTS
from classiq.interface.helpers.custom_pydantic_types import AtomType


class Molecule(pydantic.BaseModel):
    atoms: List[AtomType] = pydantic.Field(
        description="A list of atoms each containing the string of the atom's symbol and a list of its (x,y,z) location; for example [('H', (0.0, 0.0, 0.0)), ('H', (0.0, 0.0, 0.735))]."
    )
    spin: Optional[pydantic.NonNegativeInt] = pydantic.Field(
        default=1, description="spin of the molecule"
    )
    charge: Optional[pydantic.NonNegativeInt] = pydantic.Field(
        default=0, description="charge of the molecule"
    )

    @pydantic.validator("atoms")
    def validate_atoms(cls, atoms):
        for atom in atoms:
            if len(atom) != 2:
                raise ValueError(
                    "each atom should be a list of two entries: 1) name pf the elemnt (str) 2) list of its (x,y,z) location"
                )
            if type(atom[0]) != str:
                raise ValueError(
                    "atom name should be a string. unknown element: {}.".format(atom[0])
                )
            if atom[0] not in ELEMENTS:
                raise ValueError("unknown element: {}.".format(atom[0]))
            if len(atom[1]) != 3:
                raise ValueError(
                    "location of the atom is of length three, representing the (x,y,z) coordinates of the atom, error value: {}".format(
                        atom[1]
                    )
                )
            for i in atom[1]:
                if type(i) != float and type(i) != int:
                    raise ValueError(
                        "coordinates of the atom should be of type float. error value: {}".format(
                            i
                        )
                    )
        return atoms
