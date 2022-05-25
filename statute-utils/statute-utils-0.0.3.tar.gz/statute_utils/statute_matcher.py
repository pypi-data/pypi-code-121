from dataclasses import dataclass, field
from typing import Iterator, NamedTuple, Optional

from text_gists import cull_suffix

from statute_utils.assigner import assign
from statute_utils.compiler import match_provision, match_statute
from statute_utils.formula import ProvisionLabel
from statute_utils.spanner import get_statutory_provision_spans
from statute_utils.statute_formula import get_member
from statute_utils.statute_regex import IndeterminateStatute, StatuteLabel


class StatuteDesignation(NamedTuple):
    """
    Based on `text`, e.g. 'RA 386, art. 2', the following fields are detected:
    1. a `category` (the coded category of the statute), e.g. 'RA';
    2. an `identifier` (a serial number of the category), e.g. '386',
    3. a `provision` of the statute, e.g.'art. 2'"

    Requires `StatuteMatcher` which determines matches before designating components of the match.
    """

    text: str
    category: Optional[str]
    identifier: Optional[str]
    provision: Optional[str]
    indeterminate: Optional[str] = None

    @property
    def statutory_title(self) -> Optional[str]:
        """Convert 'RA' `category` and '386' `identifier` to Republic Act No. 386'"""
        if self.category and self.identifier:
            if member := get_member(self.category):
                return member.make_title(self.identifier)
        return None

    @property
    def title_and_provision(
        self,
    ) -> Optional[tuple[Optional[str], Optional[str]]]:
        """Return formatted statutory title, if existing, with associated provision, if existing."""
        return self.statutory_title, self.provision

    @property
    def isolated_provision(self) -> Optional[str]:
        """Remove the label 'Art. ' from the provision string 'Art. 2', if the provision string exists."""
        return (
            ProvisionLabel.isolate_digit(self.provision)
            if self.provision
            else None
        )


@dataclass
class StatuteMatcher:
    """
    Compile list of `StatuteDesignations` from `raw`
    >>> sample = "There is no question that Section 2 of Presidential Decree No. 1474-B is inconsistent with Section 62 of Republic Act No. 3844.; Petitioner’s case was decided under P.D. No. 971, as amended by P.D. No. 1707."
    >>> StatuteMatcher(sample).matches
    [StatuteDesignation(text='Section 2 of Presidential Decree No. 1474-B', category='PD', identifier='1474-B', provision='Section 2', indeterminate=None), StatuteDesignation(text='Section 62 of Republic Act No. 3844', category='RA', identifier='3844', provision='Section 62', indeterminate=None), StatuteDesignation(text='P.D. No. 971', category='PD', identifier='971', provision=None, indeterminate=None), StatuteDesignation(text='P.D. No. 1707', category='PD', identifier='1707', provision=None, indeterminate=None)]
    """

    raw: str
    matches: list[StatuteDesignation] = field(default_factory=list)

    def __post_init__(self):
        self.matches = list(self.get_designations(self.raw))

    @property
    def iter_dicts(self) -> Iterator[dict]:
        """Get statutes as dict in given `text`"""
        if self.matches:
            for match in self.matches:
                yield match._asdict()

    @classmethod
    def designate(cls, raw: str) -> Optional[StatuteDesignation]:
        """
        Use `assign()` to map out statutory patterns and get the proper `category` and `identifier` fields.
        >>> sample = "Republic Act (RA) No. 8424"
        >>> StatuteMatcher.designate(sample)
        StatuteDesignation(text='Republic Act (RA) No. 8424', category='RA', identifier='8424', provision=None, indeterminate=None)
        """

        provision_portion = (
            cull_suffix(match.group())
            if (match := match_provision(raw))
            else None
        )

        # statute pattern can be assigned
        if statute_portion := match_statute(raw):
            result = assign(statute_portion)
            if isinstance(result, StatuteLabel):
                return StatuteDesignation(
                    text=raw,
                    category=result.category,
                    identifier=result.identifier,
                    provision=provision_portion,
                )
            elif isinstance(result, IndeterminateStatute):
                return StatuteDesignation(
                    text=raw,
                    category=None,
                    identifier=None,
                    provision=provision_portion,
                    indeterminate=result.text,
                )

        # no statute pattern means no category and no identifier
        elif provision_portion:
            return StatuteDesignation(
                text=raw,
                category=None,
                identifier=None,
                provision=provision_portion,
            )

        return None

    @classmethod
    def get_designations(cls, input: str) -> Iterator[StatuteDesignation]:
        """Provision style and statutory style matches are first matched from the text; for each match found, create a StatuteDesignation."""
        for result in get_statutory_provision_spans(input):
            if statute_designated := cls.designate(result):
                yield statute_designated

    @classmethod
    def get_statute_category_idxes(
        cls, input: str
    ) -> Iterator[tuple[str, str]]:
        """Similar to `get_designations()` but produces tuples of raw category and identifier, e.g. `RA`, `386`, when they exist (it's possible that a StatuteDesignation only matches a provision, e.g. `Art. 2`)"""
        for result in get_statutory_provision_spans(input):
            if s := cls.designate(result):
                if s.category and s.identifier:
                    yield s.category, s.identifier

    @classmethod
    def single_match(cls, text: str) -> Optional[StatuteDesignation]:
        """Assuming only one attempted statutory designation found in the text, format the resulting match."""
        if results := list(cls.get_designations(text)):
            if len(results) == 1:
                return results[0]
        return None

    @classmethod
    def websearch(cls, text: str):
        """
        1. When a user searches for a statute, the likely input is not capitalized, e.g. "ra 386"
        2. The regex patterns utilized are case sensitive.
        3. To overcome this, try matching converted variants of the raw text.
        4. The variants include: UPPER CASE, lower case, Title Case, and the raw text.
        5. Assumes only one attempted match found in the text.
        """
        return (
            cls.single_match(text.upper())
            or cls.single_match(text.lower())
            or cls.single_match(text.title())
            or cls.single_match(text)
        )

    @classmethod
    def get_single_formal_title(
        cls, text: str
    ) -> Optional[tuple[Optional[str], Optional[str]]]:
        """Get tuple consisting of the formal statutory title and provision `Republic Act No. 386`, `art. 2` from a StatuteDesignation with 'RA' `category`, '386' `identifier`, 'art. 2', `provision`."""
        return x.title_and_provision if (x := cls.single_match(text)) else None

    @classmethod
    def get_single_category_idx(
        cls, text: str
    ) -> Optional[tuple[Optional[str], Optional[str]]]:
        """Get tuple consisting of the raw category and identifier `RA`, `386` from a StatuteDesignation with 'RA' `category`, '386' `identifier`"""
        if s := cls.single_match(text):
            if s.category and s.identifier:
                return s.category, s.identifier
        return None
