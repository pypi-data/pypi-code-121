"""Parses a string representation of a FileTree
"""
import os.path as op
from .template import Template
from .file_tree import FileTree
from contextlib import contextmanager
from typing import Tuple, List, Optional, Union, Dict, Union
import re
import pkg_resources
from glob import glob
from pathlib import Path


# searching for a file-tree

"""List of directories to look for FileTrees
"""
tree_directories = ['.']

available_subtrees: Dict[str, Union[FileTree, str, Path]] = {}

scanned_plugins = set()


@contextmanager
def extra_tree_dirs(extra_dirs):
    """Temporarily insert ``extra_dirs`` to the beginning of :attr:`tree_directories`.

    :arg extra_dirs: Sequence of additional tree file directories to search.
    """

    global tree_directories

    old_tree_directories = list(tree_directories)

    tree_directories = list(extra_dirs) + list(tree_directories)

    try:
        yield
    finally:
        tree_directories = old_tree_directories


def scan_plugins():
    """Scan plugins for filetrees
    """
    for ep in pkg_resources.iter_entry_points("file_tree.trees"):
        if ep.module_name in scanned_plugins:
            continue
        plugin = ep.load()
        plugin()
        scanned_plugins.add(ep.module_name)


def search_tree(name: str) -> Union[Path, str, FileTree]:
    """
    Searches for the file defining the specific tree

    Iteratively searches through the directories in ``tree_directories`` till a file named ${name}.tree is found.
    If not found in ``tree_directories`` the filetrees in installed python packages will be searched.

    :param name: Name of the tree
    :return: string containing the filetree definition
    """
    for directory in tree_directories:
        filename = op.join(directory, name)
        if not filename.endswith('.tree'):
            filename = filename + '.tree'
        if op.exists(filename):
            return Path(filename)

    scan_plugins()

    for ext in ('.tree', ''):
        if name + ext in available_subtrees:
            return available_subtrees[name + ext]

    raise ValueError("No file tree found for %s" % name)


def list_all_trees() -> List[str]:
    """Generates a list of available sub-trees

    Lists trees available in ``tree_directories`` (default just the current directory) and in installed file-tree plugins (e.g., `file-tree-fsl`).
    """
    scan_plugins()
    trees = list(available_subtrees.keys())
    for directory in tree_directories:
        trees.extend(op.basename(fn) for fn in glob(op.join(directory, "*.tree")))
    return trees


# reading the file-tree

def read_file_tree_text(lines: List[str], top_level: Union[str, Template]) -> FileTree:
    """Parses the provided lines to read a FileTree

    See :func:`add_line_to_tree` for how individual lines are parsed

    Args:
        lines (List[str]): Individual lines read from a file-tree file
        top_level (Template): top-level template

    Returns:
        FileTree: tree read from the file
    """
    tree = FileTree.empty(top_level)
    current: List[Tuple[int, str]] = []
    to_link: List[List[str]] = []
    for line in lines:
        current = add_line_to_tree(tree, line, current, to_link)
    for keys in to_link:
        tree.placeholders.link(*keys)
    return tree


def add_line_to_tree(tree: FileTree, line: str, current: List[Tuple[int, str]], to_link: List[List[str]]) -> List[Tuple[int, Optional[str]]]:
    """Adds template or sub-tree defined on this file

    There are 5 options for the line:

        1. Empty lines or those containing only comments (start with #) do nothing.
        2. Templates have the form "  <unique part> (<short name>)" and are added as a new template (note that the <short name> is optional).
        3. Placeholder values have the form "<key> = <value>" and are stored as placeholder values in the tree.
        4. Sub-trees have the form "  -><tree name> [<placeholder>=<value>,...] (<short name>)" and are added as a new sub-tree
        5. Linkages between placeholder values are indicated by "&LINK <placeholder>,..."

    The parent directory of the new template or sub-tree is determined by the amount of white space.

    Args:
        tree (FileTree): tree containing all templates/sub-trees read so far (will be updated in place with new template or sub-tree)
        line (str): current line from the file-tree definition
        current (List[Tuple[int, Optional[str]]]): sequence of the possible parent directories and their indentation

    Returns:
        List[Tuple[int, Optional[str]]]: new sequence of the possible parent directories after reading the line
    """
    stripped = line.split('#')[0].strip()
    if len(stripped) == 0:
        return current
    nspaces = line.index(stripped)
    parent = get_parent(nspaces, current)
    new_current = [(n, name) for n, name in current if n < nspaces]

    if stripped[:2] == '->': 
        new_dirs = []
        try:
            new_dirs.append(tree.get(parent))
        except KeyError:
            pass
        with extra_tree_dirs(new_dirs):
            sub_tree, short_names = read_subtree_line(stripped)
        tree.add_subtree(sub_tree, short_names, parent)
        new_current.append((nspaces, None))
    elif '=' in stripped:
        key, value = [s.strip() for s in stripped.split('=')]
        if value.strip() == "None":
            value = None
        if ',' in value:
            value = [None if v.strip() == "None" else v.strip() for v in value.split(',')]
        tree.update(inplace=True, **{key: value})
    elif stripped.startswith("&LINK"):
        keys = [k.strip() for k in stripped[5:].split(",")]
        to_link.append(keys)
    else:
        if stripped[0] == '!':
            if nspaces != 0:
                raise ValueError(f"Defining a new top-level with '!' is only available at the top-level, but the line '{stripped}' is indented")
            stripped = stripped[1:]
            real_parent = None
        else:
            real_parent = parent
        unique_part, short_names = read_line(stripped)
        if short_names is not None and len(short_names) == 0:
            raise ValueError("Empty short names are not allowed (they are used internally for the top-level directory")
        short_name = tree.add_template(unique_part, short_names, real_parent)
        new_current.append((nspaces, short_name))
    return new_current


def get_parent(nspaces: int, current: List[Tuple[int, str]]) -> str:
    """Determines the parent template based on the amount of whitespace

    Args:
        nspaces (int): amount of whitespace before the new line
        current (List[Tuple[int, str]]): sequence of possible parent directories and their indentation

    Raises:
        ValueError: raised of parent is a sub-tree rather than a template
        ValueError: raise if number of spaces does not match any existing directory

    Returns:
        str: empty string if the parent is the top-level directory; template short name otherwise
    """
    if len(current) == 0:
        return ""
    nspaces_max = current[-1][0]
    if nspaces > nspaces_max:
        if current[-1][1] is None:
            raise ValueError("Current line seems to be the child of a sub-tree, which is not supported.")
        return current[-1][1]

    for idx, (nspaces_template, _) in enumerate(current):
        if nspaces_template == nspaces:
            if idx == 0:
                return ""
            else:
                return current[idx - 1][1]
    raise ValueError("Number of spaces of current line does not match any previous lines.")


def check_forbidden_characters(text, characters, text_type):
    """
    Checks the text for forbidden characters

    raises ValueError if one is found

    :param text: string with the text
    :param characters: sequence of forbidden characters
    :param text_type: type of the text to raise in error message
    """
    bad = [character for character in characters if character in text]
    if len(bad) > 0:
        raise ValueError('Invalid character(s) "{}" in {}: {}'.format("".join(bad), text_type, text))


def read_line(line: str) -> Tuple[Union[FileTree, str], List[Optional[str]]]:
    """
    Parses line from the tree file

    :param line: input line from a ``*.tree`` file
    :return: Tuple with:

        - unique part of the filename
        - short name of the file (None if not provided)
    """
    if line.strip()[:1] == '->':
        return read_subtree_line(line)
    match = re.match(r'^(\s*)(\S*)\s*\((\S*)\)\s*$', line)
    if match is not None:
        gr = match.groups()
        check_forbidden_characters(gr[1], r'<>"|?*', 'file or directory name')
        if ',' in gr[2]:
            short_names = [name.strip() for name in gr[2].split(',') if len(name.strip()) > 0]
        else:
            short_names = [gr[2].strip()]
        return gr[1], short_names
    match = re.match(r'^(\s*)(\S*)\s*$', line)
    if match is not None:
        gr = match.groups()
        check_forbidden_characters(gr[1], r'<>"|?*', 'file or directory name')
        return gr[1], None
    raise ValueError('Unrecognized line %s' % line)


def read_subtree_line(line: str) -> Tuple[FileTree, List[Optional[str]]]:
    """
    Parses the line defining a sub_tree

    :param line: input line from a ``*.tree`` file
    :param template: containing template
    :return: Tuple with

        - sub_tree
        - short name of the sub_tree (None if not provided)
    """
    match = re.match(r'^(\s*)->\s*(\S*)(.*)\((\S*)\)', line)
    short_names: List[Optional[str]]
    if match is None:
        match = re.match(r'^(\s*)->\s*(\S*)(.*)', line)
        if match is None:
            raise ValueError("Sub-tree line could not be parsed: {}".format(line.strip()))
        _, type_name, variables_str = match.groups()
        short_names = [None]
    else:
        _, type_name, variables_str, full_short_name = match.groups()
        check_forbidden_characters(full_short_name, r'(){}/', 'sub-tree name')
        if ',' in full_short_name:
            short_names = [name.strip() for name in full_short_name.split(',') if len(name.strip()) > 0]
        else:
            short_names = [full_short_name]

    check_forbidden_characters(type_name, r'<>:"/\|?*', 'filename of sub-tree')

    variables = {}
    if len(variables_str.strip()) != 0:
        for single_variable in variables_str.split(','):
            key, value = single_variable.split('=')
            variables[key.strip()] = value.strip()

    sub_tree = FileTree.read(type_name, **variables)
    return sub_tree, short_names
