from typing import Match, Optional, Union

from statute_utils.formula import (
    AdministrativeMatter,
    BarMatter,
    BatasPambansa,
    CommonwealthAct,
    ExecutiveOrder,
    LegacyAct,
    NamedStatute,
    NamedStatuteIndeterminate,
    PresidentialDecree,
    RepublicAct,
    ResolutionEnBanc,
    VetoMessage,
)
from statute_utils.statute_regex import IndeterminateStatute, StatuteLabel


def assign(
    match: Match,
) -> Optional[Union[StatuteLabel, IndeterminateStatute]]:
    """
    >>> from statute_utils import match_statute
    >>> sample = match_statute('Section 2 of Presidential Decree No. 1474-B')
    >>> sample
    <re.Match object; span=(13, 43), match='Presidential Decree No. 1474-B'>
    >>> assign(sample)
    StatuteLabel(category='PD', identifier='1474-B')
    """
    return (
        NamedStatute.matcher(match)
        or AdministrativeMatter.matcher(match)
        or BarMatter.matcher(match)
        or ResolutionEnBanc.matcher(match)
        or PresidentialDecree.matcher(match)
        or BatasPambansa.matcher(match)
        or ExecutiveOrder.matcher(match)
        or RepublicAct.matcher(match)
        or CommonwealthAct.matcher(match)
        or LegacyAct.matcher(match)
        or VetoMessage.matcher(match)
        or NamedStatuteIndeterminate.matcher(match)
    )
