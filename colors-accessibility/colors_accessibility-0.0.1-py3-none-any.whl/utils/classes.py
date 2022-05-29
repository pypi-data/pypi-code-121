from dataclasses import dataclass


@dataclass
class ColorRepresentation:
    normalized: list = None
    extended: list = None
    dictionary: dict = None


@dataclass
class ColorRepresentations:
    rgb: ColorRepresentation = None
    hex: ColorRepresentation = None
    hsl: ColorRepresentation = None
