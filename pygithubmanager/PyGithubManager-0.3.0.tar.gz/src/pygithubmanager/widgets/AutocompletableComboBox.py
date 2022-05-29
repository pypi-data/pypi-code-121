from PySide6.QtCore import Qt
from PySide6.QtWidgets import QCompleter, QComboBox


def completion(word_list, widget, i=True):
    """
    Autocompletion of sender and subject

    Parameters
    ----------
    word_list : list
        List of words to be autocompleted
    widget : QComboBox
        Widget to be autocompleted
    i : bool
        If True, the autocompletion is case insensitive
    """
    word_set = set(word_list)
    completer = QCompleter(word_set)
    if i:
        completer.setCaseSensitivity(Qt.CaseInsensitive)
    else:
        completer.setCaseSensitivity(Qt.CaseSensitive)
    widget.setCompleter(completer)


class Autocomplete(QComboBox):
    def __init__(self, i=False, allow_duplicates=True):
        """
        Autocomplete ComboBox

        Parameters
        ----------
        i : bool
            If True, the autocompletion is case-insensitive
        allow_duplicates : bool
            If True, duplicates are allowed
        """
        super(Autocomplete, self).__init__()
        self.insensitivity = i
        self.allowDuplicates = allow_duplicates
        self.init()

    def init(self):
        """
        Configure the ComboBox
        """
        self.setEditable(True)
        self.setDuplicatesEnabled(self.allowDuplicates)

    def set_autocompletion(self, items, i):
        """
        Set autocompletion for the ComboBox
        Parameters
        ----------
        items : list
            List of items to be autocompleted
        i : bool
            If True, the autocompletion is case-insensitive
        """
        completion(items, self, i)

    def remove_item(self, item):
        """
        Remove an item from the ComboBox

        Parameters
        ----------
        item : int
            Index of the item to be removed
        """
        self.removeItem(item)

    def clear_items(self):
        """
        Clear all items from the ComboBox
        """
        self.clear()

    def add_items(self, items):
        """
        Add items to the ComboBox

        Parameters
        ----------
        items
            List of items to be added
        """
        self.addItems(items)
        self.set_autocompletion(items, i=self.insensitivity)
