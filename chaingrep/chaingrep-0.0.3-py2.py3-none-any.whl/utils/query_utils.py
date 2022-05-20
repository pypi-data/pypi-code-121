from decimal import Decimal


# pylint: disable=invalid-name
class operator:
    @classmethod
    def _normalize(cls, element):
        # Adjust float precision
        if type(element) in [float, Decimal]:
            # pylint: disable=consider-using-f-string
            element = "{:.5f}".format(element)

        # Lowercase addresses
        if isinstance(element, str):
            if len(element) in [42, 43, 44] and "0x" in element:
                element = element.lower()

        return element

    @classmethod
    def lower_than(cls, element):
        element = cls._normalize(element)
        element = f"<{element}"

        return element

    @classmethod
    def greater_than(cls, element):
        element = cls._normalize(element)
        element = f">{element}"

        return element

    @classmethod
    def lower_or_equal(cls, element):
        element = cls._normalize(element)
        element = f"<={element}"

        return element

    @classmethod
    def greater_or_equal(cls, element):
        element = cls._normalize(element)
        element = f">={element}"

        return element

    @classmethod
    def not_equal(cls, element):
        element = cls._normalize(element)
        element = f"!{element}"

        return element
