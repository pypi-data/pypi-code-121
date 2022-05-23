from typing import NoReturn


class Reporter:
    """Class represening a place in your streamlit app that can be updated with text to show the user.

    """

    def __init__(self, place):
        """The constructor of the InfoCell class.

        Args:
            place: the streamlit asset to write the text to.
        """

        self.info = ''
        self.place = place

    def empty(self) -> NoReturn:
        """Flush all content from the info cell.

        """

        self.info = ''
        self.place.empty()

    def update(self, delta: str) -> NoReturn:
        """Update the info cell content by appending a string.

        Args:
            delta (str): the string to add to the existing content.

        """

        self.info += delta
        self.place.text(self.info)
