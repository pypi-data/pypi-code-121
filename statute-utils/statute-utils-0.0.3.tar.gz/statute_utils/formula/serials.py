from typing import Match, Optional

from text_gists import cull_suffix

from statute_utils.statute_formula import StatuteID
from statute_utils.statute_regex import StatuteLabel

from .base import StatutePatternsMethods


class RepublicAct(StatutePatternsMethods):
    statute_id = StatuteID.RA.name
    group_name = "republic_act"
    digit_group_name = "RA_digit"

    def __init__(self) -> None:
        base_text = self.statute_base_pattern(
            group_name=self.group_name,
            first_word=r"Rep(.|ublic)?",
            second_word=r"Act?\s?",
            first_letter="R",
            second_letter="A",
            optional_number_keyword=self.optional_number_keyword,
        )

        digit = rf"(?P<{self.digit_group_name}>{self.digit_format})"

        self.formula = rf"""
        ( # e.g. Republic Act (RA) No. 242
            \b{base_text}
            \s*{digit}
        )
        """

    @classmethod
    def matcher(cls, m: Match) -> Optional[StatuteLabel]:
        if m.group(cls.group_name):
            return StatuteLabel(
                category=cls.statute_id,
                identifier=cull_suffix(m.group(cls.digit_group_name)),
            )
        return None


class ExecutiveOrder(StatutePatternsMethods):
    statute_id = StatuteID.EO.name
    group_name = "executive_order"
    digit_group_name = "EO_digit"

    def __init__(self) -> None:
        base_text = self.statute_base_pattern(
            group_name=self.group_name,
            first_word=r"Exec(.|utive)?",
            second_word=r"Order?\s?",
            first_letter="E",
            second_letter="O",
            optional_number_keyword=self.optional_number_keyword,
        )

        digit = rf"(?P<{self.digit_group_name}>{self.digit_format})"

        self.formula = rf"""
        (
            \b{base_text}
            \s*{digit}
        )
        """

    @classmethod
    def matcher(cls, m: Match) -> Optional[StatuteLabel]:
        if m.group(cls.group_name):
            return StatuteLabel(
                category=cls.statute_id,
                identifier=cull_suffix(m.group(cls.digit_group_name)),
            )
        return None


class PresidentialDecree(StatutePatternsMethods):
    statute_id = StatuteID.PD.name
    group_name = "presidential_decree"
    digit_group_name = "PD_digit"

    def __init__(self) -> None:
        base_text = self.statute_base_pattern(
            group_name=self.group_name,
            first_word=r"Pres(.|idential)?",
            second_word=r"Dec(.|ree)?\s?",
            first_letter="P",
            second_letter="D",
            optional_number_keyword=self.optional_number_keyword,
        )

        digit = rf"(?P<{self.digit_group_name}>{self.digit_format})"

        self.formula = rf"""
        (
            \b{base_text}
            \s*{digit}
        )
        """

    @classmethod
    def matcher(cls, m: Match) -> Optional[StatuteLabel]:
        if m.group(cls.group_name):
            return StatuteLabel(
                category=cls.statute_id,
                identifier=cull_suffix(m.group(cls.digit_group_name)),
            )
        return None


class BatasPambansa(StatutePatternsMethods):
    statute_id = StatuteID.BP.name
    group_name = "batas_pambansa"
    digit_group_name = "BP_digit"

    def __init__(self) -> None:
        base_text = self.statute_base_pattern(
            group_name=self.group_name,
            first_word=r"Batas",
            second_word=r"Pambansa",
            first_letter="B",
            second_letter="P",
            optional_number_keyword=self.optional_bilang_keyword,
        )  # * number keyword replaced with bilang

        digit = rf"(?P<{self.digit_group_name}>{self.digit_format})"

        self.formula = rf"""
        (
            \b{base_text}
            \s*{digit}
        )
        """

    @classmethod
    def matcher(cls, m: Match) -> Optional[StatuteLabel]:
        if m.group(cls.group_name):
            return StatuteLabel(
                category=cls.statute_id,
                identifier=cull_suffix(m.group(cls.digit_group_name)),
            )
        return None


class CommonwealthAct(StatutePatternsMethods):
    statute_id = StatuteID.CA.name
    group_name = "commonwealth_act"
    digit_group_name = "CA_digit"

    def __init__(self) -> None:
        base_text = self.statute_base_pattern(
            group_name="commonwealth_act",
            first_word=r"Com(.|monwealth)?",
            second_word=r"Act\s?",
            first_letter="C",
            second_letter="A",
            optional_number_keyword=self.optional_number_keyword,
        )

        # * digits are limited to 3
        digit = (
            rf"(?P<{self.digit_group_name}>{self.simple_commonwealth_digits})"
        )

        self.formula = rf"""
        (
            \b{base_text}
            \s*{digit}
        )
        """

    @classmethod
    def matcher(cls, m: Match) -> Optional[StatuteLabel]:
        if m.group(cls.group_name):
            return StatuteLabel(
                category=cls.statute_id,
                identifier=cull_suffix(m.group(cls.digit_group_name)),
            )
        return None


class LegacyAct(StatutePatternsMethods):
    statute_id = StatuteID.ACT.name
    group_name = "legacy_act"
    digit_group_name = "ACT_digit"

    def __init__(self) -> None:

        # join a list of negative lookbehinds
        non_match = "".join(
            rf"(?<!{i}\s)"
            for i in [
                r"An",
                r"AN",
                r"Republic",
                r"Rep",
                r"Rep\.",
                r"REPUBLIC",
                r"Commonwealth",
                r"COMMONWEALTH",
            ]
        )

        # * negative lookbehinds with words: "Act/Acts"
        base_text = rf"(?P<legacy_act>{non_match}Acts?)"

        digit = rf"(?P<{self.digit_group_name}>{self.digit_format})"

        self.formula = rf"""
        (
            \b{base_text}
            \s+{self.optional_number_keyword}
            \s*{digit}
        )
        """

    @classmethod
    def matcher(cls, m: Match) -> Optional[StatuteLabel]:
        if m.group(cls.group_name):
            return StatuteLabel(
                category=cls.statute_id,
                identifier=cull_suffix(m.group(cls.digit_group_name)),
            )
        return None


class AdministrativeMatter(StatutePatternsMethods):
    statute_id = StatuteID.RULE_AM.name
    group_name = "rule_am"
    digit_group_name = "AM_digit"

    def __init__(self) -> None:
        base_text = self.statute_base_pattern(
            group_name=self.group_name,
            first_word=r"""Adm(
                \.|
                in\.|
                inistrative
            )""",
            second_word=r"Matter",
            first_letter="A",
            second_letter="M",
            optional_number_keyword=self.optional_number_keyword,
        )

        digit = rf"(?P<{self.digit_group_name}>[\w-]+)"

        self.formula = rf"""
        ( # e.g. Administrative Matter (AM) No. 242
            \b{base_text}
            \s*{digit}
        )
        """

    @classmethod
    def matcher(cls, m: Match) -> Optional[StatuteLabel]:
        if m.group(cls.group_name):
            return StatuteLabel(
                category=cls.statute_id,
                identifier=cull_suffix(m.group(cls.digit_group_name)),
            )
        return None


class BarMatter(StatutePatternsMethods):
    statute_id = StatuteID.RULE_BM.name
    group_name = "rule_bm"
    digit_group_name = "BM_digit"

    def __init__(self) -> None:
        base_text = self.statute_base_pattern(
            group_name=self.group_name,
            first_word=r"Bar",
            second_word=r"Matter",
            first_letter="B",
            second_letter="M",
            optional_number_keyword=self.optional_number_keyword,
        )

        digit = rf"(?P<{self.digit_group_name}>{self.digit_format})"

        self.formula = rf"""
        ( # e.g. Bar Matter (AM) No. 242
            \b{base_text}
            \s*{digit}
        )
        """

    @classmethod
    def matcher(cls, m: Match) -> Optional[StatuteLabel]:
        if m.group(cls.group_name):
            return StatuteLabel(
                category=cls.statute_id,
                identifier=cull_suffix(m.group(cls.digit_group_name)),
            )
        return None


class ResolutionEnBanc(StatutePatternsMethods):
    statute_id = StatuteID.RULE_RESO.name
    group_name = "rule_reso"
    digit_group_name = "RESO_digit"

    def __init__(self) -> None:
        version_one = rf"""
        (
            Court
            \s+
            En
            \s+
            Banc
            \s+
            Resolution
        )
        """

        version_two = rf"""
        (
            Resolution
            \s+
            [o|O]f
            \s+
            [t|T]he
            \s+
            Court
            \s+
            En
            \s+
            Banc
        )
        """

        digit = rf"(?P<{self.digit_group_name}>[\w-]+)"

        self.formula = rf"""
        ( # e.g. Court En Banc Resolution dated 10-15-1991
            \b
            (?P<{self.group_name}>{version_one}|{version_two}
            )
            \s+
            [D|d]ated
            \s*{digit}
        )
        """

    @classmethod
    def matcher(cls, m: Match) -> Optional[StatuteLabel]:
        if m.group(cls.group_name):
            return StatuteLabel(
                category=cls.statute_id,
                identifier=cull_suffix(m.group(cls.digit_group_name)),
            )
        return None


class VetoMessage(StatutePatternsMethods):
    statute_id = StatuteID.VETO.name
    group_name = "veto_msg"
    digit_group_name = "veto_digit"

    def __init__(self) -> None:
        veto = rf"""
        (
            Veto
            \s+
            Message
        )
        """

        digit = rf"(?P<{self.digit_group_name}>[\w]+)"

        self.formula = rf"""
        ( # e.g. Veto Message - 11534
            \b
            (?P<{self.group_name}>{veto})
            [\s\-\–]+
            \s*{digit}
        )
        """

    @classmethod
    def matcher(cls, m: Match) -> Optional[StatuteLabel]:
        if m.group(cls.group_name):
            return StatuteLabel(
                category=cls.statute_id,
                identifier=m.group(cls.digit_group_name),
            )
        return None


class CircularOCA(StatutePatternsMethods):
    statute_id = StatuteID.OCA_CIR.name
    group_name = "rule_oca_cir"
    digit_group_name = "OCA_CIR_digit"

    def __init__(self) -> None:
        base = rf"""
        (
            OCA
            \s+
            Cir(\.|cular)
        )
        """

        digit = rf"(?P<{self.digit_group_name}>[\w-]+)"

        self.formula = rf"""
        ( # OCA Cir. No. 39-02
            \b
            (?P<{self.group_name}>{base})
            \s+
            (No\.\s*)?
            {digit}
        )
        """


class CircularSC(StatutePatternsMethods):
    statute_id = StatuteID.SC_CIR.name
    group_name = "rule_sc_cir"
    digit_group_name = "SC_CIR_digit"

    def __init__(self) -> None:
        base = rf"""
        (
            SC
            \s+
            Cir(\.|cular)
        )
        """

        digit = rf"(?P<{self.digit_group_name}>[\w-]+)"

        self.formula = rf"""
        ( # SC Cir. No. 19
            \b
            (?P<{self.group_name}>{base})
            \s+
            (No\.\s*)?
            {digit}
        )
        """
