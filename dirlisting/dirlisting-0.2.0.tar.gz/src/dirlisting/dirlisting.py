import yaml


ELBOW = "└──"
TEE = "├──"
PIPE_PREFIX = "│   "
SPACE_PREFIX = "    "


class Dirlisting:
    """This class represents the directory tree listing.

    `Dirlisting` currently assumes a single top level directory. This may be changed in
    a later release.
    """

    def __init__(self, stream):
        """Initializes an instance of Dirlisting.

        Both a file stream or a string can be used to initialize an instance of the
        class.

        Args:
            stream (str or file stream): The input YAML stream.

        """
        self._data = yaml.load(stream, yaml.SafeLoader)

    def print(self, is_sort=False, is_dirsfirst=False):
        """Print the directory listing in a nice tree format.

        Args:
            is_sort (bool): Whether or not to sort the child entries.
            is_dirsfirst (bool): Whether or not to list directories first.

        """
        topname, children = self._name_and_children(self._data[0])
        print(topname)
        self._print_children(children, is_sort, is_dirsfirst)

    def _is_dir(self, entry):
        """Whether or not an entry is a directory.

        Args:
            entry (dict or str): The entry to test.

        Returns:
            True if a directory entry; False otherwise

        """
        return isinstance(entry, dict)

    def _name_and_children(self, entry):
        """Helper function to retrieve the dir name and its children.

        If the directory has no children an empty list is returned with the name.

        Args:
            entry (dict): The single entry dict for a directory entry.

        Returns:
            A tuple with the directory name and a list of its children

        """
        name, children = next(iter(entry.items()))
        if children is None:
            children = []
        return name, children

    def _entry_name(self, entry):
        """Return the name of the directory or file.

        Args:
            entry (str or dict): The entry to check.

        Returns:
            The str with the name of the entry
        """
        name = entry
        if self._is_dir(entry):
            name, _ = self._name_and_children(entry)
        return name

    def _print_children(self, children, is_sort, is_dirsfirst, prefix=""):
        """Recursive function to print the children of a directory.

        The prefix is added to with each level of the tree. Each child gets the TEE
        marker before outputing its name except for the last child that gets the ELBOW
        marker.

        Args:
            children (list): A list of the dir's children; may be empty.
            is_sort (bool): Whether or not to sort the child entries.
            is_dirsfirst (bool): Whether or not to list directories first.
            prefix (str): The prefix to output for each child.

        Returns:
            None

        """
        if is_sort:
            children = sorted(children, key=self._entry_name)
        if is_dirsfirst:
            children = sorted(children, key=lambda e: not self._is_dir(e))
        num_children = len(children)
        for index, child in enumerate(children):
            if index == num_children - 1:
                connector = ELBOW
                add_prefix = SPACE_PREFIX
            else:
                connector = TEE
                add_prefix = PIPE_PREFIX
            if self._is_dir(child):
                name, next_children = self._name_and_children(child)
                print(f"{prefix}{connector} {name}")
                self._print_children(
                    next_children, is_sort, is_dirsfirst, prefix + add_prefix
                )
            else:
                print(f"{prefix}{connector} {child}")
