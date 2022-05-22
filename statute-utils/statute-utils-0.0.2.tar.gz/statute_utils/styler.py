import re
from typing import Match, Optional

from statute_utils.formula import (
    AdministrativeMatter,
    BarMatter,
    BatasPambansa,
    CircularOCA,
    CommonwealthAct,
    ExecutiveOrder,
    LegacyAct,
    NamedStatute,
    NamedStatuteIndeterminate,
    PresidentialDecree,
    Provision,
    RepublicAct,
    ResolutionEnBanc,
    VetoMessage,
)

PROVISION_STYLE = re.compile(rf"({Provision().formula})", re.X)
"""
A `PROVISION` style refers to a pattern object based on the `UNIT` regex formula. Examples include:
1. Sec. 1
2. Art. 2350 (a)
3. Bk V
4. Title XV
"""

statutory_regexes = [
    NamedStatute.formula,  # special patterns
    RepublicAct().formula,
    CommonwealthAct().formula,
    LegacyAct().formula,
    PresidentialDecree().formula,
    BatasPambansa().formula,  # numbered, need to construct formula
    ExecutiveOrder().formula,
    AdministrativeMatter().formula,
    BarMatter().formula,
    ResolutionEnBanc().formula,
    VetoMessage().formula,
    CircularOCA().formula,
    NamedStatuteIndeterminate.formula,  # must be last
]
STATUTE_STYLE = re.compile(rf"({'|'.join(statutory_regexes)})", re.X)
"""
A `STATUTE` style refers to a pattern object based on various regex options. Examples include:
1. CONST,
2. RA 354
3. Republic Act No. (RA) 354
"""


def match_statute(text: str) -> Optional[Match]:
    """
    >>> sample = "prior to its amendment by Republic Act (RA) No. 8424, otherwise known as the Tax Reform Act of 1997; Section 533 of Rep. Act 7160 reads in part:"
    >>> match_statute(sample)
    <re.Match object; span=(26, 52), match='Republic Act (RA) No. 8424'>
    """
    return STATUTE_STYLE.search(text)


def match_statutes(text: str) -> list[Match]:
    """
    >>> sample = "prior to its amendment by Republic Act (RA) No. 8424, otherwise known as the Tax Reform Act of 1997; Section 533 of Rep. Act 7160 reads in part:"
    >>> match_statutes(sample)
    [<re.Match object; span=(26, 52), match='Republic Act (RA) No. 8424'>, <re.Match object; span=(116, 129), match='Rep. Act 7160'>]
    """
    return list(STATUTE_STYLE.finditer(text))


def match_provision(text: str) -> Optional[Match]:
    """
    >>> sample = "prior to its amendment by Republic Act (RA) No. 8424, otherwise known as the Tax Reform Act of 1997; Section 533 of Rep. Act 7160 reads in part:"
    >>> match_provision(sample)
    <re.Match object; span=(101, 116), match='Section 533 of '>
    """
    return PROVISION_STYLE.search(text)


def match_provisions(text: str) -> list[Match]:
    """
    >>> sample = "prior to its amendment by Republic Act (RA) No. 8424, otherwise known as the Tax Reform Act of 1997; Section 533 of Rep. Act 7160 reads in part:"
    >>> match_provisions(sample)
    [<re.Match object; span=(101, 116), match='Section 533 of '>]
    """
    return list(PROVISION_STYLE.finditer(text))
