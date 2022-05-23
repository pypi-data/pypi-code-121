"""
Label Module. A label is a string
box with custom format options.
"""

from typing import Dict


class Label:
    """
    Label Box for containing text.
    """


    # pylint: disable=invalid-name
    def __init__(self, x: float, y: float, text: str='', **kwargs) -> None:
        """
        Initializes an instace of 'Label'.
        """

        self.x: float = x
        self.y: float = y
        self.text: str = text

        self.properties: Dict = kwargs


    def change_properties(self, new_properties: Dict) -> None:
        """
        Updates the properties of the label.
        """

        self.properties.update(**new_properties)
