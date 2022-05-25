import re
from enum import Enum
from typing import Iterator, Match, NamedTuple, Optional, Pattern

from text_gists import (
    combine_regexes_as_options,
    construct_acronyms,
    construct_negative_lookbehinds,
    construct_prefix_options,
)

from statute_utils.statute_formula import StatuteID
from statute_utils.statute_regex import IndeterminateStatute, StatuteLabel


def add_suffix_year(regex: str, year: str) -> str:
    return rf"{regex}\s+of\s+{year}"


def add_suffix_PH(regex: str) -> str:
    return rf"{regex}\s+of\s+the\s+Philippines"


class NamedLaw(NamedTuple):
    name: str
    year: int
    serial: StatuteLabel
    aliases: list[str] = []
    max_year: int | None = None  # TODO possible to limit application dates?
    base: str | None = None

    @property
    def aliased(self) -> Optional[str]:
        """The order of aliases matter hence the need to start with the longer matching sequence, e.g. `add_suffix_PH()`"""
        if self.aliases:
            return rf"({combine_regexes_as_options(self.aliases)})"
        return None

    @property
    def options(self):
        result = re.escape(self.name)  # *  with re.X, no issues arise
        if self.aliases:
            result = combine_regexes_as_options(self.aliases + [result])
        return rf"({result})"

    @property
    def pattern(self) -> Pattern:
        return re.compile(rf"{self.options}")


class Base(Enum):
    const = r"((PHIL\.\s+)?CONST(ITUTION|\.?)|(Phil\.\s+)?Const(itution|\.?))"  # can refer to 3
    admin = r"Administrative\s+Code"  # can refer to 3
    elect = r"Election\s+Code"  # can refer to 2
    corp = r"Corporation\s+Code"  # can refer to 2
    agrarian = r"Agrarian\s+Reform\s+Code"  # can refer to 2
    civil = r"Civil\s+Code"  # can refer to 2
    tax = r"(N\.?I\.?R\.?C\.?|National\s+Internal\s+Revenue\s+Code)"  # can refer to 3
    penal = r"Penal\s+Code"  # can refer to 2
    coop = r"Cooperative\s+Code"  # can refer to 2
    insure = r"Insurance\s+Code"  # can refer to 2
    rules = r"Rules\s+of\s+Court"  # can refer to 3

    @property
    def pattern(self) -> Pattern:
        return re.compile(self.value)

    def find(self, raw: str) -> Optional[Match]:
        return self.pattern.search(raw)


NAMED_LAWS = [
    NamedLaw(
        base=Base.const.value,
        name="1987 Constitution",
        year=1987,
        serial=StatuteLabel(StatuteID.CONST.name, "1987"),
        aliases=[
            add_suffix_PH(rf"1987\s+{Base.const.value}"),
            rf"1987\s+{Base.const.value}",
        ],
    ),
    NamedLaw(
        base=Base.const.value,
        name="1973 Constitution",
        year=1973,
        serial=StatuteLabel(StatuteID.CONST.name, "1973"),
        aliases=[
            add_suffix_PH(rf"1973\s+{Base.const.value}"),
            rf"1973\s+{Base.const.value}",
        ],
    ),
    NamedLaw(
        base=Base.const.value,
        name="1935 Constitution",
        year=1935,
        serial=StatuteLabel(StatuteID.CONST.name, "1935"),
        aliases=[
            add_suffix_PH(rf"1935\s+{Base.const.value}"),
            rf"1935\s+{Base.const.value}",
        ],
    ),
    NamedLaw(
        name="Maceda Law",
        year=1972,
        serial=StatuteLabel(StatuteID.RA.name, "6552"),
    ),
    NamedLaw(
        name="Recto Law",
        year=1933,
        serial=StatuteLabel(StatuteID.ACT.name, "4122"),
    ),
    NamedLaw(
        name="Code of Civil Procedure",
        year=1901,
        serial=StatuteLabel(StatuteID.ACT.name, "190"),
    ),
    NamedLaw(
        name="Canons of Professional Ethics",
        year=1901,
        serial=StatuteLabel(StatuteID.RULE_ROC.name, "ethics_1901"),
    ),
    NamedLaw(
        name="Code of Professional Responsibility",
        year=1988,
        serial=StatuteLabel(StatuteID.RULE_ROC.name, "responsibility_1988"),
        aliases=[construct_acronyms("cpr")],
    ),
    NamedLaw(
        name="Canons of Judicial Ethics",
        year=1946,
        serial=StatuteLabel(StatuteID.RULE_ROC.name, "judicial_ethics_1946"),
    ),
    NamedLaw(
        name="Code of Judicial Conduct",
        year=1989,
        serial=StatuteLabel(StatuteID.RULE_ROC.name, "judicial_conduct_1989"),
    ),
    NamedLaw(
        base=Base.rules.value,
        name="1940 Rules of Court",
        year=1940,
        serial=StatuteLabel(StatuteID.RULE_ROC.name, "1940"),
    ),
    NamedLaw(
        base=Base.rules.value,
        name="1964 Rules of Court",
        year=1940,
        serial=StatuteLabel(StatuteID.RULE_ROC.name, "1964"),
    ),
    NamedLaw(
        base=Base.admin.value,
        name="Administrative Code of 1916",
        year=1916,
        max_year=1917,
        serial=StatuteLabel(StatuteID.ACT.name, "2657"),
    ),
    NamedLaw(
        base=Base.admin.value,
        name="Administrative Code of 1917",
        year=1917,
        max_year=1986,
        serial=StatuteLabel(StatuteID.ACT.name, "2711"),
        aliases=[
            construct_prefix_options(
                Base.admin.value, [r"[Rr]evised", r"1917"]
            ),
            add_suffix_year(Base.admin.value, "1917"),
        ],
    ),
    NamedLaw(
        base=Base.admin.value,
        name="Administrative Code of 1987",
        year=1987,
        serial=StatuteLabel(StatuteID.EO.name, "292"),
        aliases=[
            construct_prefix_options(Base.admin.value, [r"1987"]),
            add_suffix_year(Base.admin.value, "1987"),
        ],
    ),
    NamedLaw(
        base=Base.civil.value,
        name="Old Civil Code",
        year=1889,
        max_year=1950,
        serial=StatuteLabel(StatuteID.SPAIN.name, "civil"),
        aliases=[
            construct_prefix_options(
                Base.civil.value, [r"[Ss]panish", r"[Oo]ld"]
            ),
            add_suffix_year(Base.civil.value, "1889"),
        ],
    ),
    NamedLaw(
        base=Base.civil.value,
        name="Civil Code of the Philippines",
        year=1950,
        serial=StatuteLabel(StatuteID.RA.name, "386"),
        aliases=[
            add_suffix_PH(Base.civil.value),
            add_suffix_year(Base.civil.value, "1950"),
            construct_negative_lookbehinds(
                Base.civil.value, [r"[Ss]panish", r"[Oo]ld"]
            ),
        ],
    ),
    NamedLaw(
        name="Child and Youth Welfare Code",
        year=1974,
        serial=StatuteLabel(StatuteID.PD.name, "603"),
        aliases=[
            r"Child[\s&]+Youth\s+Welfare\s+Code",
        ],
    ),
    NamedLaw(
        base=Base.coop.value,
        name="Cooperative Code",
        year=1990,
        max_year=2008,
        serial=StatuteLabel(StatuteID.RA.name, "6938"),
        aliases=[
            construct_negative_lookbehinds(
                Base.coop.value,
                [r"Philippine"],
            )
        ],
    ),
    NamedLaw(
        base=Base.coop.value,
        name="Philippine Cooperative Code",
        year=2008,
        serial=StatuteLabel(StatuteID.RA.name, "9520"),
        aliases=[
            construct_prefix_options(
                Base.coop.value,
                [r"Philippine"],
            ),
        ],
    ),
    NamedLaw(
        base=Base.penal.value,
        name="Old Penal Code",
        year=1889,
        max_year=1930,
        serial=StatuteLabel(StatuteID.SPAIN.name, "penal"),
        aliases=[
            construct_prefix_options(
                Base.penal.value,
                [r"[Ss]panish", r"[Oo]ld"],
            ),
        ],
    ),
    NamedLaw(
        base=Base.penal.value,
        name="Revised Penal Code",
        year=1930,
        serial=StatuteLabel(StatuteID.ACT.name, "3815"),
        aliases=[
            construct_prefix_options(
                Base.penal.value,
                [r"[Rr]evised"],
            ),
            construct_acronyms("rpc"),
        ],
    ),
    NamedLaw(
        name="Code of Commerce",
        year=1889,
        serial=StatuteLabel(StatuteID.SPAIN.name, "commerce"),
    ),
    NamedLaw(
        base=Base.corp.value,
        name="Corporation Code of 1980",
        year=1980,
        max_year=2020,
        serial=StatuteLabel(StatuteID.BP.name, "68"),
        aliases=[
            add_suffix_year(Base.corp.value, "1980"),
        ],
    ),
    NamedLaw(
        base=Base.corp.value,
        name="Revised Corporation Code",
        year=2021,
        serial=StatuteLabel(StatuteID.RA.name, "11232"),
        aliases=[
            construct_prefix_options(
                Base.corp.value,
                [r"[Rr]evised"],
            ),
            add_suffix_year(Base.corp.value, "2021"),
        ],
    ),
    NamedLaw(
        base=Base.tax.value,
        name="National Internal Revenue Code of 1939",
        year=1939,
        max_year=1977,
        serial=StatuteLabel(StatuteID.CA.name, "466"),
        aliases=[
            construct_prefix_options(Base.tax.value, [r"1939"]),
            construct_prefix_options(r"Tax\s+Code", [r"1939"]),
            add_suffix_year(Base.tax.value, "1939"),
            add_suffix_year(r"Tax\s+Code", "1939"),
            construct_acronyms("nirc", 1939),
        ],
    ),
    NamedLaw(
        base=Base.tax.value,
        name="National Internal Revenue Code of 1977",
        year=1977,
        max_year=1997,
        serial=StatuteLabel(StatuteID.PD.name, "1158"),
        aliases=[
            construct_prefix_options(Base.tax.value, [r"1977"]),
            construct_prefix_options(r"Tax\s+Code", [r"1977"]),
            add_suffix_year(Base.tax.value, "1977"),
            add_suffix_year(r"Tax\s+Code", "1977"),
            construct_acronyms("nirc", 1977),
        ],
    ),
    NamedLaw(
        base=Base.tax.value,
        name="National Internal Revenue Code",
        year=1997,
        serial=StatuteLabel(StatuteID.RA.name, "8424"),
        aliases=[
            construct_prefix_options(Base.tax.value, [r"1997"]),
            construct_prefix_options(r"Tax\s+Code", [r"1997"]),
            add_suffix_year(Base.tax.value, "1997"),
            add_suffix_year(r"Tax\s+Code", "1997"),
            construct_acronyms("nirc", 1997),
        ],
    ),
    NamedLaw(
        name="Real Property Tax Code",
        year=1974,
        serial=StatuteLabel(StatuteID.PD.name, "464"),
    ),
    NamedLaw(
        base=Base.elect.value,
        name="Revised Election Code",
        year=1947,
        serial=StatuteLabel(StatuteID.RA.name, "180"),
    ),
    NamedLaw(
        base=Base.elect.value,
        name="Omnibus Election Code",
        year=1985,
        serial=StatuteLabel(StatuteID.BP.name, "881"),
        aliases=[construct_acronyms("oec", 1997)],
    ),
    NamedLaw(
        name="Family Code",
        year=1987,
        serial=StatuteLabel(StatuteID.EO.name, "209"),
        aliases=[add_suffix_PH(r"Family\s+Code")],
    ),
    NamedLaw(
        name="Fire Code",
        year=2008,
        serial=StatuteLabel(StatuteID.RA.name, "9514"),
        aliases=[add_suffix_PH(r"Fire\s+Code")],
    ),
    NamedLaw(
        name="Water Code",
        year=1976,
        serial=StatuteLabel(StatuteID.PD.name, "1067"),
        aliases=[add_suffix_PH(r"Water\s+Code")],
    ),
    NamedLaw(
        base=Base.agrarian.value,
        name="Agricultural Land Reform Code",
        year=1963,
        serial=StatuteLabel(StatuteID.RA.name, "3844"),
    ),
    NamedLaw(
        base=Base.agrarian.value,
        name="Comprehensive Agrarian Reform Code",
        year=1988,
        serial=StatuteLabel(StatuteID.RA.name, "6657"),
        aliases=[
            add_suffix_year(
                r"Comprehensive\s+Agrarian\s+Reform\s+(Code|Law)",
                "1988",
            ),
            construct_prefix_options(
                r"Agrarian\s+Reform\s+(Code|Law)",
                [r"Comprehensive"],
            ),
        ],
    ),
    NamedLaw(
        name="Coconut Industry Code",
        year=1978,
        serial=StatuteLabel(StatuteID.PD.name, "961"),
        aliases=[add_suffix_PH(r"Coconut\s+Industry\s+Code")],
    ),
    NamedLaw(
        name="Sanitation Code",
        year=1975,
        serial=StatuteLabel(StatuteID.PD.name, "856"),
        aliases=[add_suffix_PH(r"Sanitation\s+Code")],
    ),
    NamedLaw(
        name="State Auditing Code",
        year=1978,
        serial=StatuteLabel(StatuteID.PD.name, "1445"),
    ),
    NamedLaw(
        base=Base.insure.value,
        name="Insurance Code",
        year=1974,
        serial=StatuteLabel(StatuteID.PD.name, "612"),
        aliases=[add_suffix_year(Base.insure.value, "1974")],
    ),
    NamedLaw(
        base=Base.insure.value,
        name="Insurance Code",
        year=2013,
        serial=StatuteLabel(StatuteID.RA.name, "10607"),
        aliases=[add_suffix_year(Base.insure.value, "2013")],
    ),
    NamedLaw(
        name="Intellectual Property Code",
        year=1997,
        serial=StatuteLabel(StatuteID.RA.name, "8293"),
        aliases=[
            add_suffix_PH(r"Intellectual\s+Property\s+Code"),
            add_suffix_year(r"Intellectual\s+Property\s+Code", "1997"),
        ],
    ),
    NamedLaw(
        name="Labor Code",
        year=1974,
        serial=StatuteLabel(StatuteID.PD.name, "442"),
        aliases=[
            add_suffix_PH(r"Labor\s+Code"),
            add_suffix_year(r"Labor\s+Code", "1974"),
        ],
    ),
    NamedLaw(
        name="Local Government Code",
        year=1991,
        serial=StatuteLabel(StatuteID.RA.name, "7160"),
        aliases=[
            add_suffix_PH(r"Local\s+Government\s+Code"),
            add_suffix_year(r"Local\s+Government\s+Code", "1991"),
            construct_acronyms("lgc"),
        ],
    ),
    NamedLaw(
        name="Flag and Heraldic Code",
        year=1998,
        serial=StatuteLabel(StatuteID.RA.name, "8491"),
    ),
    NamedLaw(
        name="Philippine Fisheries Code of 1998",
        year=1998,
        serial=StatuteLabel(StatuteID.RA.name, "8550"),
    ),
    NamedLaw(
        name="Forest Reform Code",
        year=1998,
        serial=StatuteLabel(StatuteID.PD.name, "389"),
    ),
    NamedLaw(
        name="Land Transportation and Traffic Code",
        year=1964,
        serial=StatuteLabel(StatuteID.RA.name, "4136"),
    ),
    NamedLaw(
        name="Meat Inspection Code",
        year=2004,
        serial=StatuteLabel(StatuteID.RA.name, "9296"),
    ),
    NamedLaw(
        name="Muslim Code of Personal Laws",
        year=1977,
        serial=StatuteLabel(StatuteID.PD.name, "1083"),
    ),
    NamedLaw(
        name="National Building Code",
        year=1977,
        serial=StatuteLabel(StatuteID.PD.name, "1096"),
        aliases=[add_suffix_PH(r"National\s+Building\s+Code")],
    ),
    NamedLaw(
        name="Philippine Environment Code",
        year=1977,
        serial=StatuteLabel(StatuteID.PD.name, "1152"),
    ),
    NamedLaw(
        name="National Code of Marketing of Breast-milk Substitutes and Supplements",
        year=1986,
        serial=StatuteLabel(StatuteID.EO.name, "51"),
    ),
    NamedLaw(
        name="Tariff and Customs Code",
        year=1957,
        serial=StatuteLabel(StatuteID.RA.name, "1937"),
        aliases=[
            add_suffix_PH(r"Tariff\s+and\s+Customs\s+Code"),
            construct_acronyms("tccp"),
        ],
    ),
]

NAMES_REGEX: str = combine_regexes_as_options([n.options for n in NAMED_LAWS])
"""
Collects all regex strings that can be constructed from each NAME and constructs a combined regex string.
"""


def get_indeterminates():
    for named in NAMED_LAWS:
        if named.base:
            yield named.base


INDETERMINATES_REGEX: set[str] = combine_regexes_as_options(
    set(get_indeterminates())
)
"""
Collects all regex strings that form the base of indeterminate statutes;
When used in `Named Laws`, each base results in complete `StatuteLabel`s;
When used alone in legal documents (with a human providing context), each base is indeterminate and thus not machine-readable.
"""


class NamedStatute:
    group_name = "named_statute"
    formula = rf"""
            (?P<{group_name}>
                {NAMES_REGEX}
            )
        """

    @classmethod
    def matcher(cls, m: Match) -> Optional[StatuteLabel]:
        return cls.fetch(text) if (text := m.group(cls.group_name)) else None

    @classmethod
    def fetch(cls, raw: str) -> Optional[StatuteLabel]:
        for named in NAMED_LAWS:
            if re.compile(named.options).search(raw):
                return named.serial
        return None

    @classmethod
    def get_match(cls, raw: str) -> Optional[Match]:
        return m if (m := re.compile(cls.formula, re.X).search(raw)) else None

    @classmethod
    def get_named_law(cls, raw: str) -> Iterator[NamedLaw]:
        for named in NAMED_LAWS:
            if raw.casefold() in named.name.casefold():
                yield named
        return None


class NamedStatuteIndeterminate:
    group_name = "indeterminate_statute"
    formula = rf"""
            (?P<{group_name}>
                {INDETERMINATES_REGEX}
            )
        """

    @classmethod
    def matcher(cls, m: Match) -> Optional[IndeterminateStatute]:
        return (
            IndeterminateStatute(text)
            if (text := m.group(cls.group_name))
            else None
        )

    @classmethod
    def get_match(cls, raw: str) -> Optional[Match]:
        return m if (m := re.compile(cls.formula, re.X).search(raw)) else None
