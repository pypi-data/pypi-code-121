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

    def print(self):
        """Print the directory listing in a nice tree format."""
        topname, children = self._name_and_children(self._data[0])
        print(topname)
        self._print_children(children)

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

    def _print_children(self, children, prefix=""):
        """Recursive function to print the children of a directory.

        The prefix is added to with each level of the tree. Each child gets the TEE
        marker before outputing its name except for the last child that gets the ELBOW
        marker.

        Args:
            children (list): A list of the dir's children; may be empty.
            prefix (str): The prefix to output for each child.

        Returns:
            None

        """
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
                self._print_children(next_children, prefix + add_prefix)
            else:
                print(f"{prefix}{connector} {child}")
