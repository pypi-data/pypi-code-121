from enum import Enum, unique

_NUMBER = "No."
_BILANG = "Blg."
_DATED = "dated"
_DASHED = "-"


@unique
class StatuteID(Enum):
    RA = ("Republic Act", _NUMBER)
    CA = ("Commonwealth Act", _NUMBER)
    ACT = ("Act", _NUMBER)
    CONST = ("Constitution", None)
    SPAIN = ("Spanish", None)
    BP = ("Batas Pambansa", _BILANG)
    PD = ("Presidential Decree", _NUMBER)
    EO = ("Executive Order", _NUMBER)
    VETO = ("Veto Message", _DASHED)
    RULE_ROC = ("Rules of Court", None)
    RULE_BM = ("Bar Matter", _NUMBER)
    RULE_AM = ("Administrative Matter", _NUMBER)
    RULE_RESO = ("Resolution of the Court En Banc", _DATED)
    OCA_CIR = ("OCA Circular", _NUMBER)
    SC_CIR = ("SC Circular", _NUMBER)

    @property
    def parts(self) -> str:
        """Remove `None` values when joining the tuple value"""
        return " ".join(elem for elem in self.value if elem)

    def get_spanish_id_code(self, text: str):
        """Legacy docs don't have serialized identifiers"""
        remainder = text.removeprefix("Spanish ").lower()
        if "civil" in remainder:
            return "civil"
        elif "commerce" in remainder:
            return "commerce"
        elif "penal" in remainder:
            return "penal"

    def get_idx(self, txt: str) -> str:
        """Given text e.g. `Spanish Civil Code` or `Executive Order No. 111`, get the serial number"""
        if self.name == "SPAIN" and (code := self.get_spanish_id_code(txt)):
            return code  # special case
        return txt.replace(self.parts, "").strip()  # regular

    def search_pair(self, txt: str) -> tuple[str, str] | None:
        """Return shortcut tuple of member name and identifier, if found."""
        return (self.name, self.get_idx(txt)) if self.value[0] in txt else None

    def make_title(self, idx: str) -> str:
        """Return full title; notice inverted order for Rules of Court, Constitution"""

        # invert
        if self.name in ["RULE_ROC", "CONST"]:
            return f"{idx} {self.parts}"  # e.g. 1987 Constitution

        # special
        elif self.name == "SPAIN":
            if code := self.get_spanish_id_code(f"Spanish {idx}"):
                if code == "civil" or code == "penal":
                    return f"Spanish {code.title()} Code"
                elif code == "commerce":
                    return "Spanish Code of Commerce"

        # default
        return f"{self.parts} {idx}"  # e.g. Republic Act No. 1231


def get_statute_choices() -> list[tuple[str, str]]:
    return [
        (name, member.value[0])
        for name, member in StatuteID.__members__.items()
    ]


def get_member(query: str) -> StatuteID | None:
    """Get the StatuteID object representing the the name, e.g. 'ra', 'oca_cir', etc."""
    for name, member in StatuteID.__members__.items():
        if name == query.upper():
            return member
    return None


def extract_category_and_identifier_from_text(
    text: str,
) -> tuple[str, str] | None:
    """Given statutory text, e.g. "Republic Act No. 386", get a matching category ("RA") and identifier ("386") by going through each member of the `StatuteID` enumeration"""
    for member in StatuteID:
        if pair := member.search_pair(text):
            return pair
    return None
