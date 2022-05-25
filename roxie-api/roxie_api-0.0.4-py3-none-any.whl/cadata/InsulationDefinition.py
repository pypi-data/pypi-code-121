from pydantic.dataclasses import dataclass

from roxieapi.cadata.Definition import Definition


@dataclass
class InsulationDefinition(Definition):
    """Class for insulation definition.

    Attributes:
        thickness (float): The thickness (mm) on narrow side of cable.
        width (float): The width (mm) on broad side of cable.
    """

    thickness: float = 0.0
    width: float = 0.0

    @staticmethod
    def get_magnum_to_roxie_dct() -> dict:
        return {
            "name": "Name",
            "thickness": "Radial",
            "width": "Azimut",
            "comment": "Comment",
        }
