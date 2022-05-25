#!/usr/bin/env python
# -*- coding: UTF-8 -*-
""" Text Utility Methods: Common Functions without Special Libraries """

from statistics import mean

STOPWORDS = [
    'a',
    'all',

    'for',
    'from',

    'of',

    'i',
    'in',
    'into',
    'is',

    'to',
    'the',
]


class TextUtils(object):
    """ Text Utility Methods: Common Functions without Special Libraries """

    def choose_random_line(input_text: str) -> str:
        """ Choose Random Line from Long Input String

        The function will segment the input text and if only one line exists, this will be returned
        if multiple lines exist, the function will randomly choose a single line, assuming the length 
            of that line is near the mean 

        Use Case:

            Assume the input text is:
                "Hi!  How are you doing?  I'm here to help you"

            This segments into three sentences:
                [
                    "Hi!",
                    "How are you doing?",
                    "I'm here to help you",
                ]

            Either of the last two sentences will be chosen

        Args:
            input_text (str): the incoming text string

        Returns:
            str: a random segment from the incoming text string
        """

        def random_line(lines: list) -> str or None:
            try:
                d = {len(x): x for x in lines}
                _mean = mean(d)
                lines = list(reversed(d.values()))
                for i in len(lines):
                    if len(lines[i]) >= _mean - 2:
                        return lines[i]

                return lines[0]
            except Exception:
                print(lines)
                raise ValueError

        lines = TextUtils.split_on_punctuation(input_text)
        if len(lines) == 1:
            return lines[0]
        return random_line(lines)

    @staticmethod
    def jaccard_similarity(x: str, y: str) -> float:
        """ returns the jaccard similarity between two lists

        Args:
            x (str): the first string to compare
            y (str): the second string to compare

        Returns:
            float: the Jaccard similarity score (0 <= x <= 100)
        """
        intersection_cardinality = len(set.intersection(*[set(x), set(y)]))
        union_cardinality = len(set.union(*[set(x), set(y)]))
        sim = intersection_cardinality/float(union_cardinality)
        return round(sim, 3)

    @staticmethod
    def split_on_len(input_text: str,
                     threshold: int = 7) -> str:
        """Insert New Lines into Label Text
        This constrains the text to fit into a small box on a diagram

        Args:
            input_text (str): The text that will be displayed
            threshold (int, optional): The relative position to set a line break. Defaults to 7.

        Returns:
            str: the input text with zero-or-more line breaks inserted
        """

        if len(input_text) <= threshold:
            return input_text

        tokens = [x.strip() for x in input_text.split(' ')]

        master = []
        buffer = []
        for i in range(len(tokens)):
            buffer.append(tokens[i])

            temp = ' '.join(buffer).strip()
            if len(temp) >= threshold:
                master.append(temp)
                buffer = []

        if len(buffer):
            master.append(' '.join(buffer).strip())

        return "\\n".join(master).strip()

    @staticmethod
    def ends_with_punctuation(input_text: str) -> bool:
        """ Determine if Input Text ends with punctuation

        Args:
            input_text (str): any input text of any length

        Returns:
            bool: True if punctuation ends the input text
        """
        if input_text is None or not len(input_text):
            return False

        return input_text[-1] in ['.', '?', '!']  # common ending punctuation

    @staticmethod
    def remove_ending_punctuation(input_text: str) -> str:
        """ Remove Ending (terminating sequence) Punctuation

        Args:
            input_text (str): the input text of any length
            Sample Input:
                How are you doing?

        Returns:
            str: the input text with ending punctuation (if any) removed
            Sample Output:
                How are you doing
        """
        if TextUtils.ends_with_punctuation(input_text):
            return input_text[:-1]
        return input_text

    @staticmethod
    def split_on_punctuation(input_text: str,
                             punkt: list = ['!', '?']) -> list:
        """ Split (segment) a line on common punctuation

        Args:
            input_text (str): the input text of any length
            punkt (list, optional): the punctuation to split on. Defaults to ['!', '?'].

        Returns:
            list: the split (segmented) input text
        """

        for p in punkt:
            input_text = input_text.replace(p, '.')

        lines = input_text.split('.')
        lines = [x.strip() for x in lines]
        lines = [x for x in lines if x and len(x)]

        return lines

    @staticmethod
    def update_spacing(input_text: str) -> str:
        """ Correct Syntactical Spacing Inconsistencies

        Args:
            input_text (str): the input text of any length

        Returns:
            str: the corrected input string
        """
        input_text = input_text.replace(' !', '!')
        input_text = input_text.replace('.?', '?')
        input_text = input_text.replace('.!', '!')
        input_text = input_text.replace('. .', '. ').strip()

        while '  ' in input_text:
            input_text = input_text.replace('  ', ' ')

        return input_text

    @staticmethod
    def update_csvs(input_text: str) -> str:
        """ Synatically correct Comma Separated values in Natural Language

        Samples:
            1.  Input:      meetings, presentations and speeches
                Output:     meetings, presentations, and speeches
            2.  Input:      the telephone, and electronic mail
                Output:     the telephone and electronic mail

        Args:
            input_text (str): the input text of any length

        Returns:
            str: the corrected input string
        """
        return input_text

    @staticmethod
    def update_determiners(input_text: str) -> str:
        """ Update Determiners in a text string

        Args:
            input_text (str): the input text of any length
            Sample Input:
                "I see a elephant!"

        Returns:
            str: the corrected input string
            Sample Output:
                "I see an elephant!"
        """
        if ' ' not in input_text:
            return input_text

        results = []
        tokens = input_text.split(' ')

        for i in range(len(tokens)):

            def use_an() -> bool:
                if tokens[i].lower() != 'a':
                    return False

                if i + 1 >= len(tokens):
                    return False

                return TextUtils.startswith_vowel(tokens[i + 1])

            def an() -> str:
                if tokens[i].isupper():
                    return "An"
                return "an"

            if use_an():
                results.append(an())
            else:
                results.append(tokens[i])

        return ' '.join(results).strip()

    @staticmethod
    def startswith_vowel(input_text: str) -> str:
        """ Determine if Input Text starts with a vowel

        Args:
            input_text (str): the input text of any length

        Returns:
            str: True if the input text does start with a vowel
        """
        vowels = ['a', 'e', 'i', 'o', 'u']

        if input_text[0] in ["'", '"'] and len(input_text) > 1:
            return input_text[1].lower() in vowels

        return input_text[0].lower() in vowels

    @staticmethod
    def lower_case(input_text: str) -> str:
        """ Perform Lower Casing on Input

        Args:
            input_text (str): the input text of any length
            Sample Input:
                'The Quick Brown Fox Jumped OVER the Lazy Dog'

        Returns:
            str: the corrected input string
            Sample Output:
                'the quick brown fox jumped over the lazy dog'
        """
        if ' ' not in input_text:
            return input_text.lower()

        tokens = [x.lower() for x in input_text.split(' ')]

        return ' '.join(tokens).strip()

    @staticmethod
    def sentence_case(input_text: str) -> str:
        """ Perform Sentence Casing on Input

        Args:
            input_text (str): the input text of any length
            Sample Input:
                'the quick brown fox jumped over the lazy dog'

        Returns:
            str: the corrected input string
            Sample Output:
                'The quick brown fox jumped over the lazy dog'
        """
        def case(value: str) -> str:
            return f"{value[:1].upper()}{value[1:]}"

        if ' ' not in input_text:
            return case(input_text)

        def conditional_case(value: str) -> str:

            # careful not to lowercase an acronym ...
            if len(value) > 1 and not value.isupper():
                return value.lower()

            return value

        tokens = input_text.split(' ')
        results = \
            [case(tokens[0])] + \
            [conditional_case(x) for x in tokens[1:]]

        return ' '.join(results).strip()

    @staticmethod
    def title_case(input_text: str) -> str:
        """ Perform Title Casing on Input

        Args:
            input_text (str): the input text of any length
            Sample Input:
                'the quick brown fox jumped over the lazy dog'

        Returns:
            str: the corrected input string
            Sample Output:
                'The Quick Brown Fox Jumped Over the Lazy Dog'
        """
        def case(value: str) -> str:
            return f"{value[:1].upper()}{value[1:]}"

        def conditional_case(value: str) -> str:
            if value.lower().strip() in STOPWORDS:

                # careful not to lowercase an acronym ...
                if len(value) > 1 and not value.isupper():
                    return value.lower()

            return case(value)

        if ' ' not in input_text:
            return case(input_text)

        tokens = input_text.split(' ')
        results = \
            [case(tokens[0])] + \
            [conditional_case(x) for x in tokens[1:]]

        return ' '.join(results).strip()
