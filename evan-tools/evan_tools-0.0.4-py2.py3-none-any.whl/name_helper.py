class NameHelper:
    @staticmethod
    def camel_case_to_snake_case(text: str) -> str:
        """
        camel case to snake case
        e.g: abcAbc -> abc_abc
        :param text:
        :return: text -> str
        """
        words = []
        for index, char in enumerate(text):
            if char.isupper() and index != 0:
                words.append("_")
            words.append(char)

        return "".join(words).lower()

    @staticmethod
    def camel_cast_to_pascal_case(text: str) -> str:
        """
        camel case to pascal case
        e.g: abcAbc -> AbcAbc
        :param text:
        :return: text -> str
        """
        words = text[0].upper()
        return words + text[1:]

    @staticmethod
    def snake_case_to_camel_case(text: str) -> str:
        """
        snake case to camel case;
        e.g: abc_abc -> abcAbc
        :param text:
        :return: text -> str
        """
        words = text.split("_")
        if len(words) < 1: return text

        return words[0] + "".join([word[0].upper() + word[1:] for word in words[1:]])

    @staticmethod
    def snake_case_to_pascal_case(text: str) -> str:
        """
        snake case to pascal case
        e.g: abc_abc -> AbcAbc
        :param text:
        :return: text -> str
        """
        words = text.split("_")
        if len(words) < 1: return text

        return "".join([word[0].upper() + word[1:] for word in words])

    @staticmethod
    def pascal_case_to_snake_case(text: str) -> str:
        """
        pascal case to snake case
        e.g: AbcAbc -> abc_abc
        :param text:
        :return: text -> str
        """
        return NameHelper.camel_case_to_snake_case(text)

    @staticmethod
    def pascal_case_to_camel_case(text: str) -> str:
        """
        pascal case to camel case
        e.g: AbcAbc -> abcAbc
        :param text:
        :return: text -> str
        """
        words = text[0].lower()
        return words + text[1:]