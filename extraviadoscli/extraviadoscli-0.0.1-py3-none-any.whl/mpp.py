import dataclasses
import datetime
import enum
import random
import string

import slugify

SLUG_LEN = 50

class StateChoices(enum.Enum):
    CIUDAD_DE_MEXICO = "MX-CMX"
    AGUASCALIENTES = "MX-AGU"
    BAJA_CALIFORNIA = "MX-BCN"
    BAJA_CALIFORNIA_SUR = "MX-BCS"
    CAMPECHE = "MX-CAM"
    COAHUILA_DE_ZARAGOZA = "MX-COA"
    COLIMA = "MX-COL"
    CHIAPAS = "MX-CHP"
    CHIHUAHUA = "MX-CHH"
    DURANGO = "MX-DUR"
    GUANAJUATO = "MX-GUA"
    GUERRERO = "MX-GRO"
    HIDALGO = "MX-HID"
    JALISCO = "MX-JAL"
    MEXICO = "MX-MEX"
    MICHOACAN_DE_OCAMPO = "MX-MIC"
    MORELOS = "MX-MOR"
    NAYARIT = "MX-NAY"
    NUEVO_LEON = "MX-NLE"
    OAXACA = "MX-OAX"
    PUEBLA = "MX-PUE"
    QUERETARO = "MX-QUE"
    QUINTANA_ROO = "MX-ROO"
    SAN_LUIS_POTOSI = "MX-SLP"
    SINALOA = "MX-SIN"
    SONORA = "MX-SON"
    TABASCO = "MX-TAB"
    TAMAULIPAS = "MX-TAM"
    TLAXCALA = "MX-TLA"
    VERACRUZ_DE_IGNACIO_DE_LA_LLAVE = "MX-VER"
    YUCATAN = "MX-YUC"
    ZACATECAS = "MX-ZAC"


class PhysicalBuildChoices(enum.Enum):
    SLIM = "S"
    REGULAR = "R"
    HEAVY = "H"


class ComplexionChoices(enum.Enum):
    BROWN = "BR"
    LIGHT_BROWN = "LB"
    DARK_BROWN = "DB"
    WHITE = "WH"
    BLACK = "BL"


class SexChoices(enum.Enum):
    MALE = "M"
    FEMALE = "F"
    OTHER = "O"


class AlertTypeChoices(enum.Enum):
    ALBA = "AL"
    AMBER = "AM"
    ODISEA = "OD"
    OTHER = "OT"


def randomnumber(length: int):
    return "".join(random.choice(string.digits) for _ in range(length))


@dataclasses.dataclass
class MissingPersonPoster:
    slug: str = dataclasses.field(init=False, compare=False)
    mp_name: str
    mp_height: int | None = None
    mp_weight: int | None = None
    mp_physical_build: str = ""
    mp_complexion: str = ""
    mp_sex: str = ""
    mp_dob: datetime.date | None = None
    mp_age_when_disappeared: int | None = None
    mp_eyes_description: str = ""
    mp_hair_description: str = ""
    mp_outfit_description: str = ""
    mp_identifying_characteristics: str = ""
    circumstances_behind_dissapearance: str = ""
    missing_from: str = ""
    missing_date: datetime.date | None = None
    found: bool = False
    alert_type: str = ""
    po_state: str = ""
    po_post_url: str = ""
    po_post_publication_date: datetime.date | None = None
    po_poster_url: str = ""
    is_multiple: bool = False

    def __post_init__(self):
        # We will add 2 dashes to the final slug between the slug contents, so we
        # substract 2 from the total character count
        words = SLUG_LEN - 2

        name_len = int(words * 0.7)
        md_len = int(words * 0.2)
        rn_len = int(words * 0.1)

        missing_date = self.missing_date or self.po_post_publication_date
        if missing_date is None:
            missing_date = ""
        else:
            missing_date = missing_date.strftime("%Y-%m-%d")

        rn = randomnumber(rn_len)

        self.slug = slugify.slugify(
            f"{self.mp_name[:name_len]}-{missing_date[:md_len]}-{rn}"
        )
