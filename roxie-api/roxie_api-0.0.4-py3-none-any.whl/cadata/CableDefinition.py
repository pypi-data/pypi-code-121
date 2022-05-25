from pydantic.dataclasses import dataclass

from roxieapi.cadata.Definition import Definition


@dataclass
class CableDefinition(Definition):
    """Class for cable cadata definition.

    Attributes:
        width (float): The length (mm) of the long side of the cable cross-section.
        thickness_i (float): The inner narrow side thickness (mm).
        thickness_o (float): The outer narrow side thickness (mm).
        n_s (int): The number of strands (mm).
        l_tp (float): The length of the transposition pitch (mm) of the Rutherford-type cable.
        f_degrad (float): The degradation of the critical current density in %.
    """

    width: float = 0.0
    thickness_i: float = 0.0
    thickness_o: float = 0.0
    n_s: int = 0
    l_tp: float = 0.0
    f_degrad: float = 0.0

    @staticmethod
    def get_magnum_to_roxie_dct() -> dict:
        return {
            "name": "Name",
            "width": "height",
            "thickness_i": "width_i",
            "thickness_o": "width_o",
            "n_s": "ns",
            "l_tp": "transp.",
            "f_degrad": "degrd",
            "comment": "Comment",
        }
