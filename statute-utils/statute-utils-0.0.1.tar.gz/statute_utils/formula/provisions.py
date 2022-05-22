import re
from typing import Match, Optional


class ProvisionLabel:
    paragraph = r"""
        \b
        (sub-?)?pars?
        (
            \.
            |agraphs?
        )?
        \b
    """

    article = r"""
        \b
        (A|a)rts?
        (
            \.
            |(icles?\b)
        )?
    """

    article_capped = r"""
        \b
        ARTS?\.?
        \b
    """

    section = r"""
        \b
        (S|s)
        ec
        (
            \.
            |(tions?)\b
        )?

    """

    section_capped = r"""
        \b
        SEC(TION)?S?\.?
        \b
    """

    chapter = r"""
        \b
        (C|c)h
        (
            \.
            |apters?
        )?
        \b
    """

    book = r"""
        \b
        (B|b)
        (
            (ook)
            |(k.?)
        )
        \b
    """

    title = r""" # excludes the following "Title" from being considered a provision
        (?<![Cc]ertificate\sof\s) # without s Original Certificate of Title
        (?<![Cc]ertificates\sof\s) # with s # Transfer Certificates of Title
        \b
        (T|t)it
        (
            \.
            |le
        )?
        \b
    """

    rule = r"""
        \bRule\b
    """

    canon = r"""
        \bCanon\b
    """

    section_symbol = r"""
        §§?\s*
    """

    options = [
        rule,
        canon,
        paragraph,
        article,
        article_capped,
        section,
        section_capped,
        title,
        chapter,
        book,
    ]
    link_options = (rf"{i}\s+" for i in options)
    formula = rf"({'|'.join(link_options)}|{section_symbol})"

    @classmethod
    def parse(cls, text) -> Optional[Match]:
        return re.compile(cls.formula, re.X).search(text)

    @classmethod
    def isolate_digit(cls, text) -> Optional[str]:
        """Removes label e.g. Art., Section from the query_text"""
        if match := cls.parse(text):
            return re.sub(match.group(), "", text).strip()
        return None


class ProvisionSubject:
    just_digits = r"""
        (
            \d+
        )
    """

    simple_roman = r"""
        (
            [IXV]+\b
        ) #\b ensures that in cases like "Section 6 of PD 902-A provides:"SECTION 6. In " SECTION 6. excludes an additional "I"
    """

    simple_letters = r"""
        (
            \- # ensures that -A, -B, -C is used; prevents matching of `B.P.`
            [ABC]
            \b
        )
    """

    bracketed_character = r"""
        (
            \(
            \w{1,3}
            \)
        )
    """

    connector = r"""
        (
            and|
            of|
            \,|
            \.|
            \s|
            \-
        )
    """

    formula = rf"""
        ( # must start with an initial object
            {just_digits}|
            {simple_roman}|
            {bracketed_character}
        ) # may end with multiple objects
        (
            {simple_letters}|
            {simple_roman}|
            {just_digits}|
            {bracketed_character}|
            {connector}
        )*
    """

    @classmethod
    def parse(cls, text) -> Optional[Match]:
        return re.compile(cls.formula, re.X).search(text)


class Provision:

    formula = rf"""
        (
            ({ProvisionLabel().formula})
            {ProvisionSubject().formula}
        )+
    """
