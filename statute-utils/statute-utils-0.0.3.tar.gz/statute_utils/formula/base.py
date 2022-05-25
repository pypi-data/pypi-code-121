import re
from typing import Pattern


class StatutePatternsMethods:

    optional_number_keyword = r"""
        (
            No # Number keyword
            .? # period possible
            s? # Number keyword can be plural
            .? # period possible
        )? # the Number keyword itself can be optional
    """

    optional_bilang_keyword = r"""
        (
            Bilang| # Bilang keyword
            Blg.? #
        )? # the Bilang keyword itself can be optional
    """

    digit_format = r"""
        [
            \d
            \s
            ,
        ]* # optional
        (and)? # some laws are referred to with multiple numbers, e.g. RA Nos. 965 and 2630
        \s*
        \d+-?A?B?
    """

    simple_commonwealth_digits = r"""
        \d{1,3} # limited number for early cases
        (?=(
            \s|
            \"|
            \”|
            \.|
            \,|
            \)|
            $
        )) # must not proceed to another digit
    """

    def statute_base_pattern(
        self,
        group_name: str,
        first_word: str,
        second_word: str,
        first_letter: str,
        second_letter: str,
        optional_number_keyword: str,
    ) -> str:
        """
        Create a regex base string for a specific statute

        :param group_name: e.g. republic_act, presidential_decree, etc.
        :type group_name: str
        :param first_word: regex possibilities for republic, presidential, etc
        :type first_word: str
        :param second_word: regex possibilities for act, decree, etc
        :type second_word: str
        :param first_letter: r, p
        :type first_letter: str
        :param second_letter: a, d
        :type second_letter: str
        :param optional_number_keyword: the number regex to use for this base pattern (e.g. no. or blg.)
        :type optional_number_keyword: str
        :return: formula for creating longform and shortform options in regex
        :rtype: str
        """
        # make the first letter and the second letter a bracketable option
        opt_acronym = self.bracketize(first_letter, second_letter)

        # combine the first word and the second word
        longform = rf"({first_word}\s+{second_word})"

        # make another option that will serve as a standalone option without brackets
        shortform = self.shorthand(first_letter, second_letter)

        # return the formula
        return rf"""
        (?P<{group_name}>
            (
                {longform} # Republic Act
                {opt_acronym}\s+ # (RA)
                {optional_number_keyword} # No.
            )|
            (
                {longform} # Republic Act
                \s+
                {optional_number_keyword} # No.
                {opt_acronym} # RA
            )|
            (
                {shortform} # RA
                \s+
                {optional_number_keyword} # No.
            )
        )"""

    def shorthand(self, first_letter: str, second_letter: str) -> str:
        """
        Most statutes are referred to in the following way:
        RA 8424, P.D. 1606, EO. 1008, etc. with spatial errors like
        B.  P.   22
        """
        return rf"""
        ( # shorthand option
            {first_letter}
            \.?
            \s* # possible whitespaces in typographical errors
            {second_letter}
            \.?
            \s* # possible whitespaces in typographical errors
        )
        """

    def bracketize(self, first_letter: str, second_letter: str) -> str:
        """
        Some statutes are referred to in the following way:
        "Republic Act (RA) No. 8424". RA therefore needs to be an optional
        bracketed pattern.
        """
        return rf"""
        (
            \s*
            \(
            {self.shorthand(first_letter, second_letter)}
            \)
        )? # optional bracketed option
        """


class NumberedMatcher:
    def get_list_of_digits(self, target_digits_string: str) -> list[str]:
        """
        Some statutes are referred to in the following way:
        Republic Act Nos. 1234, 1235, and 1421. This means there
        are three separate statutes that need to be identified.

        :param target_digits_string: the string consisting of numbers
        :type target_digits_string: str
        :return: the list consisting of numbers (each number is a str type)
        :rtype: List[str]
        """
        digits = re.compile(r"\b\d+-?A?B?\b")
        return digits.findall(target_digits_string)

    def get_items(
        self, raw_text: str, pattern: Pattern, label_name: str
    ) -> list[dict]:
        """
        Dissect string into component parts of the specific statute

        :param raw_text: the subject text to dissect
        :type raw_text: str
        :param pattern: custom pattern based of the statute category
        :type pattern: Pattern
        :param label_name: e.g. RA, PD, etc.
        :type label_name: str
        :param group_name: e.g. republic_act, presidential_decree, etc.
        :type group_name: str
        :return: list of patterns detected for a given label
        :rtype: Optional[List[Dict]]
        """
        if not (matches := pattern.finditer(raw_text)):
            return []

        items = []
        for match in matches:
            text = match.group(0)
            digit_label = label_name + "_digit"
            digit_string = match.group(digit_label)
            digits = self.get_list_of_digits(digit_string)
            for digit in digits:  # e.g. RA 123 and 5431
                item = {
                    "category": label_name,
                    "full_text": text,
                    "digit": digit,
                }
                items.append(item)

        return items
