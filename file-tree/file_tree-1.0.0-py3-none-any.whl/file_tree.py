"""Defines the main FileTree object, which will be the main point of interaction
"""
from collections import defaultdict
import warnings
import xarray
from .template import Template, Placeholders, is_singular
from typing import Generator, Optional, Dict, Any, Sequence, Union, Set, Collection
from pathlib import Path
import numpy as np
from functools import cmp_to_key
import string
from shutil import copyfile
import os
from warnings import warn
import rich


class FileTree:
    """Represents a structured directory

    The many methods can be split into 4 categories

        1. The template interface. Each path (file or directory) is represented by a :class:`Template <file_tree.template.Template>`, 
           which defines the filename with any unknown parts (e.g., subject ID) marked by placeholders. 
           Templates are accessed based on their key.

            - :meth:`get_template`: used to access a template based on its key.
            - :meth:`template_keys`: used to list all the template keys.
            - :meth:`add_template`: used to add a new template or overwrite an existing one.
            - :meth:`add_subtree`: can be used to add all the templates from a different tree to this one.
            - :meth:`filter_templates`: reduce the filetree to a user-provided list of templates and its parents
        
        2. The placeholder interface. Placeholders represent values to be filled into the placeholders.
           Each placeholder can be either undefined, have a singular value, or have a sequence of possible values.

            - You can access the :class:`placeholders dictionary-like object <file_tree.template.Placeholders>` directly through `FileTree.placeholders`
            - :meth:`update`: returns a new FileTree with updated placeholders or updates the placeholders in the current one.
            - :meth:`update_glob`: sets the placeholder values based on which files/directories exist on disk.
            - :meth:`iter_vars`: iterate over all possible values for the selected placeholders.
            - :meth:`iter`: iterate over all possible values for the placeholders that are part of a given template.
        
        3. Getting the actual filenames based on filling the placeholder values into the templates.

            - :meth:`get`: Returns a valid path by filling in all the placeholders in a template. 
              For this to work all placeholder values should be defined and singular.
            - :meth:`get_mult`: Returns array of all possible valid paths by filling in the placeholders in a template.
              Placeholder values can be singular or a sequence of possible values.
            - :meth:`get_mult_glob`: Returns array with existing paths on disk. 
              Placeholder values can be singular, a sequence of possible values, or undefined.
              In the latter case possible values for that placeholder are determined by checking the disk.
            - :meth:`fill`: Returns new FileTree with any singular values filled into the templates and removed from the placeholder dict.

        4. Input/output

            - :meth:`report`: create a pretty overview of the filetree
            - :meth:`run_app`: opens a terminal-based App to explore the filetree interactively
            - :meth:`empty`: creates empty FileTree with no templates or placeholder values.
            - :meth:`read`: reads a new FileTree from a file.
            - :meth:`from_string`: reads a new FileTree from a string.
            - :meth:`write`: writes a FileTree to a file.
            - :meth:`to_string`: writes a FileTree to a string.
    """

    def __init__(self, templates: Dict[str, Template], placeholders: Union[Dict[str, Any], Placeholders], return_path=False):
        self._templates = templates
        self.placeholders = Placeholders(placeholders)
        self.return_path = return_path

    # create new FileTree objects
    @classmethod
    def empty(cls, top_level: Union[str, Template]='.', return_path=False) -> "FileTree":
        """Creates a new empty FileTree containing only a top-level directory

        Args:
            top_level (str, Template, optional): Top-level directory that other templates will use as a reference. Defaults to current directory.

        Returns:
            FileTree: empty FileTree
        """
        if not isinstance(top_level, Template):
            top_level = Template(None, top_level)
        return cls({"": top_level}, {}, return_path=return_path)

    @classmethod
    def read(cls, name: str, top_level: Union[str, Template]='.', return_path=False, **placeholders) -> "FileTree":
        """Reads a filetree based on the given name

        Args:
            name (str): name of the filetree. Interpreted as:

                - a filename containing the tree definition if "name" or "name.tree" exist on disk
                - one of the trees in `tree_directories` if one of those contains "name" or "name.tree"
                - one of the tree in the plugin FileTree modules

            top_level (str): top-level directory name. Defaults to current directory. Set to parent template for sub-trees.
            placeholders (str->Any): maps placeholder names to their values

        Returns:
            FileTree: tree matching the definition in the file
        """
        from . import parse_tree
        if 'directory' in placeholders:
            warnings.warn(
                f"Setting the 'directory' placeholder to {placeholders['directory']}. " +
                "This differs from the behaviour of the old filetree in fslpy, which used the `directory` keyword to set the top-level directory. " +
                "If you want to do that, please use the new `top_level` keyword instead of `directory`."
                )
        found_tree = parse_tree.search_tree(name)
        if isinstance(found_tree, Path):
            with open(found_tree, 'r') as f:
                text = f.read()
            with parse_tree.extra_tree_dirs([found_tree.parent]):
                return cls.from_string(text, top_level, return_path=return_path, **placeholders)
        elif isinstance(found_tree, str):
            return cls.from_string(found_tree, top_level, return_path=return_path, **placeholders)
        elif isinstance(found_tree, FileTree):
            new_tree = cls.empty(top_level, return_path)
            new_tree.add_subtree(found_tree, fill=False)
            return new_tree.update(**placeholders)
        raise ValueError(f"Type of object ({type(found_tree)}) returned when searching for FileTree named '{name}' was not recognised")

    @classmethod
    def from_string(cls, definition: str, top_level: Union[str, Template]='.', return_path=False, **placeholders) -> "FileTree":
        """Creates a FileTree based on the given definition

        Args:
            definition (str): A FileTree definition describing a structured directory
            top_level (str): top-level directory name. Defaults to current directory. Set to parent template for sub-trees.

        Returns:
            FileTree: tree matching the definition in the file
        """
        from . import parse_tree
        res = parse_tree.read_file_tree_text(definition.splitlines(), top_level).update(inplace=True, **placeholders)
        res.return_path = return_path
        return res

    def copy(self, ) -> "FileTree":
        """Creates a copy of the tree

        The dictionaries (templates, placeholders) are copied, but the values within them are not.

        Returns:
            FileTree: new tree object with identical templates, sub-trees and placeholders
        """
        new_tree = type(self)(dict(self._templates), Placeholders(self.placeholders), self.return_path)
        return new_tree

    # template interface
    def get_template(self, key: str) -> Template:
        """Returns the template corresponding to `key`.

        Raises:
            KeyError: if no template with that identifier is available

        Args:
            key (str): key identifying the template.

        Returns:
            Template: description of pathname with placeholders not filled in
        """
        return self._templates[key]

    @property
    def top_level(self, ):
        as_string = self.get_template("").unique_part
        if self.return_path:
            return Path(as_string)
        return str(as_string)

    @top_level.setter
    def top_level(self, value: str):
        self.get_template("").unique_part = str(value)

    def add_template(self, template_path: str, key: Optional[Union[str, Sequence[str]]]=None, parent: Optional[str]="", overwrite=False) -> str:
        """Updates the FileTree with the new template

        Args:
            template_path: path name with respect to the parent (or top-level if no parent provided)
            key: key(s) to access this template in the future. Defaults to result from :meth:`Template.guess_key <file_tree.template.Template.guess_key>` 
                (i.e., the path basename without the extension).
            parent: if defined, `template_path` will be interpreted as relative to this template. 
                By default the top-level template is used as reference.
                To create a template unaffiliated with the rest of the tree, set `parent` to None. 
                Such a template should be an absolute path or relative to the current directory and can be used as parent for other templates
            overwrite: if True, overwrites any existing template rather than raising a ValueError. Defaults to False.

        Returns:
            str: one of the short names under which the template has been stored
        """
        parent_template = None if parent is None else self.get_template(parent)
        new_template = Template(parent_template, template_path)
        if parent_template is not None and new_template.as_path == parent_template.as_path:
            new_template = parent_template
        return self._add_actual_template(new_template, key, overwrite=overwrite)

    def _add_actual_template(self, template: Template, keys: Optional[Union[str, Sequence[str]]]=None, overwrite=False):
        if keys is None:
            keys = template.guess_key()
        if isinstance(keys, Path):
            keys = str(keys)
        if isinstance(keys, str):
            keys = [keys]
        for key in keys:
            if key in self._templates:
                if not overwrite:
                    raise ValueError(f"{self._templates[key]} already exists with short name '{key}', so cannot add {template}")
                old_template = self.get_template(key)
                for potential_child in self._templates.values():
                    if potential_child.parent is old_template:
                        potential_child.parent = template
            self._templates[key] = template
        return keys[0]

    def template_keys(self, only_leaves=False):
        """Returns the keys of all the templates in the FileTree

        Each key will be returned for templates with multiple keys.

        Args
            only_leaves (bool, optional): set to True to only return templates that do not have any children
        """
        if not only_leaves:
            return self._templates.keys()
        parents = {t.parent for t in self._templates.values() if t.parent is not None}
        return {key for key, template in self._templates.items() if template not in parents}

    def add_subtree(self, sub_tree: "FileTree", precursor: Union[Optional[str], Sequence[Optional[str]]]=(None, ), parent: Optional[str]="", fill=None) -> None:
        """Updates the templates and the placeholders in place with those in sub_tree

        The top-level directory of the sub-tree will be replaced by the `parent` (unless set to None).
        The sub-tree templates will be available with the key "<precursor>/<original_key>",
        unless the precursor is None in which case they will be unchanged (which can easily lead to errors due to naming conflicts).

        What happens with the placeholder values of the sub-tree depends on whether the precursor is None or not:

            - if the precursor is None, any singular values are directly filled into the sub-tree templates. 
              Any placeholders with multiple values will be added to the top-level variable list (error is raised in case of conflicts).
            - if the precursor is a string, the templates are updated to look for "<precursor>/<original_placeholder>" and 
              all sub-tree placeholder values are also prepended with this precursor.
              Any template values with "<precursor>/<key>" will first look for that full key, but if that is undefined 
              they will fall back to "<key>" (see :class:`Placeholders <file_tree.template.Placeholders>`).
        
        The net effect of either of these procedures is that the sub-tree placeholder values will be used in that sub-tree,
        but will not affect templates defined elsewhere in the parent tree.
        If a placeholder is undefined in a sub-tree, it will be taken from the parent placeholder values (if available).

        Args:
            sub_tree (FileTree): tree to be added to the current one
            precursor (list(str or None)): name(s) of the sub-tree. Defaults to just adding the sub-tree to the main tree without precursor
            parent (str): key of the template used as top-level directory for the sub tree. 
                Defaults to top-level directory of the main tree. 
                Can be set to None for an independent tree.
            fill (Optional[bool]): whether any defined placeholders should be filled in before adding the sub-tree. By default this is True if there is no precursor and false otherwise
        """
        if isinstance(precursor, str) or precursor is None:
            precursor = [precursor]
        for name in precursor:
            sub_tree_fill = sub_tree
            if name is None:
                add_string = ""
                if (fill is None) or fill:
                    sub_tree_fill = sub_tree.fill()
            else:
                add_string = name + "/"
                if fill:
                    sub_tree_fill = sub_tree.fill()

            to_assign = dict(sub_tree_fill._templates)
            assigned = {"": (
                Template(None, to_assign[""].unique_part) 
                if parent is None else 
                self.get_template(parent)
            )}
            been_assigned = {to_assign[""]: ""}
            del to_assign[""]
            while len(to_assign) > 0:
                for key, old_template in list(to_assign.items()):
                    if old_template.parent is None:
                        parent_template = None
                    elif old_template.parent in been_assigned:
                        parent_key = been_assigned[old_template.parent]
                        parent_template = assigned[parent_key]
                    else:
                        continue
                    assigned[key] = Template(parent_template, old_template.unique_part).add_precursor(add_string)
                    been_assigned[old_template] = key
                    del to_assign[key]

            for key, template in assigned.items():
                if key == '' and name is None:
                    if parent is None:
                        for letter in string.ascii_letters:
                            label = f"tree_top_{letter}"
                            if (
                                label not in sub_tree_fill.template_keys() and
                                label not in self.template_keys()
                            ):
                                self._add_actual_template(template, label)
                                break
                    continue
                self._add_actual_template(template, add_string + key)

            if name is None:
                conflict = {key for key in sub_tree_fill.placeholders.keys() if key in self.placeholders}
                if len(conflict) > 0:
                    raise ValueError(f"Sub-tree placeholder values for {conflict} conflict with those set in the parent tree.")
            for old_key, old_value in sub_tree_fill.placeholders.items():
                if isinstance(old_key, str):
                    self.placeholders[add_string + old_key] = old_value
                else:
                    self.placeholders[frozenset(add_string + k for k in old_key)] = {add_string + k: v for k, v in old_value.items()}

    def filter_templates(self, template_names: Collection[str], check=True):
        """New FileTree containing just the templates in `template_names` and their parents.

        A KeyError will be raised if any of the template names are not in the FileTree (unless `check` is set to False)

        Args:
            template_names: names of the templates to keep.
            check: if True, check whether all template names are actually part of the FileTree
        """
        all_keys = self.template_keys()
        if check:
            undefined = {name for name in template_names if name not in all_keys}
            if len(undefined) > 0:
                raise KeyError("Undefined template names found in filter: ", undefined)

        new_templates = {}

        def add_template(template: Template):
            for key, value in self._templates.items():
                if value is template:
                    new_templates[key] = value
            if template.parent is not None:
                add_template(template.parent)

        for name in template_names:
            if name not in all_keys:
                continue
            add_template(self.get_template(name))

        return FileTree(new_templates, self.placeholders.copy(), return_path=self.return_path)

    # placeholders interface
    def update(self, inplace=False, **placeholders) -> "FileTree":
        """Updates the placeholder values to be filled into the templates

        Args:
            inplace (bool): if True change the placeholders in-place (and return the FileTree itself); 
                by default a new FileTree is returned with the updated values without altering this one.
            **placeholders (Dict[str, Any]): maps placeholder names to their new values (None to mark placeholder as undefined)

        Returns:
            FileTree: Tree with updated placeholders (same tree as the current one if inplace is True)
        """ 
        new_tree = self if inplace else self.copy()
        new_tree.placeholders.update(placeholders)
        return new_tree

    def update_glob(self, template_key: Union[str, Sequence[str]], inplace=False) -> "FileTree":
        """Updates any undefined placeholders based on which files exist on disk for template

        Args:
            template_key (str or sequence of str): key(s) of the template(s) to use
            inplace (bool): if True change the placeholders in-place (and return the FileTree itself); 
                by default a new FileTree is returned with the updated values without altering this one.

        Returns:
            FileTree: Tree with updated placeholders (same tree as the current one if inplace is True)
        """
        if isinstance(template_key, str):
            template_key = [template_key]
        new_placeholders: Dict[str, Set[str]] = defaultdict(set)
        for key in template_key:
            template = self.get_template(key)
            from_template = template.get_all_placeholders(self.placeholders)
            for name, values in from_template.items():
                new_placeholders[name] = new_placeholders[name].union(values)

        def cmp(item1, item2):
            if item1 is None:
                return -1
            if item2 is None:
                return 1
            if item1 < item2:
                return -1
            if item1 > item2:
                return 1
            return 0
        return self.update(inplace, **{k: sorted(v, key=cmp_to_key(cmp)) for k, v in new_placeholders.items()})

    # Extract paths
    def get(self, key: str, make_dir=False) -> Union[str, Path]:
        """Returns template with placeholder values filled in

        Args:
            key (str): identifier for the template
            make_dir (bool, optional): If set to True, create the parent directory of the returned path.

        Returns:
            Path: Filled in template as Path object. 
                Returned as a `pathlib.Path` object if `FileTree.return_path` is True. 
                Otherwise a string is returned.
        """
        path = self.get_template(key).format_single(self.placeholders)
        if make_dir:
            Path(path).parent.mkdir(parents=True, exist_ok=True)
        if self.return_path:
            return Path(path)
        return path

    def get_mult(self, key: Union[str, Sequence[str]], filter=False, make_dir=False) -> Union[xarray.DataArray, xarray.Dataset]:
        """Returns array of paths with all possible values filled in for the placeholders 

        Singular placeholder values are filled into the template directly. 
        For each placeholder with multiple values a dimension is added to the output array.
        This dimension will have the name of the placeholder and labels corresponding to the possible values (see http://xarray.pydata.org/en/stable/).
        The precense of required, undefined placeholders will lead to an error 
        (see :meth:`get_mult_glob` or :meth:`update_glob` to set these placeholders based on which files exist on disk).

        Args:
            key (str, Sequence[str]): identifier(s) for the template.
            filter (bool, optional): If Set to True, will filter out any non-existent files.
                If the return type is strings, non-existent entries will be empty strings.
                If the return type is Path objects, non-existent entries will be None.
                Note that the default behaviour is opposite from :meth:`get_mult_glob`.
            make_dir (bool, optional): If set to True, create the parent directory for each returned path.

        Returns:
            xarray.DataArray, xarray.Dataset: For a single key returns all possible paths in an xarray DataArray. 
                For multiple keys it returns the combination of them in an xarray Dataset.
                Each element of in the xarray is a `pathlib.Path` object if `FileTree.return_path` is True.
                Otherwise the xarray will contain the paths as strings.
        """
        if isinstance(key, str):
            paths = self.get_template(key).format_mult(self.placeholders, filter=filter)
            paths.name = key
            if make_dir:
                for path in paths.data.flat:
                    if path is not None:
                        Path(path).parent.mkdir(parents=True, exist_ok=True)
            if self.return_path:
                return xarray.apply_ufunc(lambda p: None if p == "" else Path(p), paths, vectorize=True)
            return paths
        else:
            return xarray.merge([self.get_mult(k, filter=filter, make_dir=make_dir) for k in key], join='exact')

    def get_mult_glob(self, key: Union[str, Sequence[str]]) -> Union[xarray.DataArray, xarray.Dataset]:
        """Returns array of paths with all possible values filled in for the placeholders 

        Singular placeholder values are filled into the template directly. 
        For each placeholder with multiple values a dimension is added to the output array.
        This dimension will have the name of the placeholder and labels corresponding to the possible values (see http://xarray.pydata.org/en/stable/).
        The possible values for undefined placeholders will be determined by which files actually exist on disk.

        The same result can be obtained by calling `self.update_glob(key).get_mult(key, filter=True)`.
        However calling this method is more efficient, because it only has to check the disk for which files exist once.

        Args:
            key (str, Sequence[str]): identifier(s) for the template.

        Returns:
            xarray.DataArray, xarray.Dataset: For a single key returns all possible paths in an xarray DataArray. 
                For multiple keys it returns the combination of them in an xarray Dataset.
                Each element of in the xarray is a `pathlib.Path` object if `FileTree.return_path` is True.
                Otherwise the xarray will contain the paths as strings.
        """
        if isinstance(key, str):
            template = self.get_template(key)
            matches = template.all_matches(self.placeholders)

            new_placeholders = Placeholders(self.placeholders)
            new_placeholders.update(template.get_all_placeholders(self.placeholders, matches=matches))

            paths = template.format_mult(new_placeholders, filter=True, matches=matches)
            paths.name = key
            if self.return_path:
                return paths
            res = xarray.apply_ufunc(lambda p: "" if p is None else str(p), paths, vectorize=True)
            return res
        else:
            return xarray.merge([self.get_mult_glob(k) for k in key], join='outer', fill_value=None if self.return_path else "")


    def fill(self, keep_optionals=True) -> "FileTree":
        """Fills in singular placeholder values.

        Args:
            keep_optionals: if True keep optional parameters that have not been set

        Returns:
            FileTree: new tree with singular placeholder values filled into the templates and removed from the placeholder dict
        """
        new_templates: Dict[str, Template] = {}
        to_assign = dict(self._templates)
        get_keys = {t: k for k, t in to_assign.items()}
        already_transformed = {}
        while len(to_assign) > 0:
            for key, old_template in list(to_assign.items()):
                if old_template in already_transformed:
                    new_templates[key] = already_transformed[old_template]
                    del to_assign[key]
                    continue
                if old_template.parent is None:
                    new_parent = None
                elif get_keys[old_template.parent] in new_templates:
                    new_parent = new_templates[get_keys[old_template.parent]]
                else:
                    continue
                new_templates[key] = Template(new_parent, str(Template(None, old_template.unique_part).format_single(self.placeholders, check=False, keep_optionals=keep_optionals)))
                already_transformed[old_template] = new_templates[key]
                del to_assign[key]
        _, mult_placeholders = self.placeholders.split()
        return FileTree(new_templates, mult_placeholders)

    # iteration
    def iter_vars(self, placeholders: Sequence[str]) -> Generator["FileTree", None, None]:
        """Iterate over the placeholder placeholder names

        Args:
            placeholders (Sequence[str]): sequence of placeholder names to iterate over

        Returns:
            Generator[FileTree]: yields trees, where each placeholder only has a single possible value
        """
        for sub_placeholders in self.placeholders.iter_over(placeholders):
            yield FileTree(self._templates, sub_placeholders, self.return_path)

    def iter(self, template: str, check_exists: bool=False) -> Generator["FileTree", None, None]:
        """Iterate over trees containng all possible values for template

        Args:
            template (str): short name identifier of the template
            check_exists (bool): set to True to only return trees for which the template actually exists
        
        Returns:
            Generator[FileTree]: yields trees, where each placeholder in given template only has a single possible value
        """
        placeholders = self.get_template(template).placeholders(valid=self.placeholders.keys())
        for tree in self.iter_vars(placeholders):
            if not check_exists or Path(tree.get(template)).exists:
                yield tree

    # convert to string
    def to_string(self, indentation=4) -> str:
        """Converts FileTree into a valid filetree definition

        An identical FileTree can be created by running :meth:`from_string` on the resulting string.

        Args:
            indentation (int, optional): Number of spaces to use for indendation. Defaults to 4.
        """
        placeholder_lines = []
        for key, value in self.placeholders.items():
            if value is None:
                continue
            if isinstance(key, frozenset):
                # linked placeholder
                for linked_key, linked_value in value.items():
                    placeholder_lines.append(f"{linked_key} = {', '.join([str(v) for v in linked_value])}")
                placeholder_lines.append(f"&LINK {', '.join(key)}")

            elif np.array(value).ndim == 1:
                placeholder_lines.append(f"{key} = {', '.join([str(v) for v in value])}")
            else:
                placeholder_lines.append(f"{key} = {value}")
        lines = ['\n'.join(placeholder_lines)]

        top_level = sorted([(key, template) for key, template in self._templates.items() if template.parent is None], key=lambda k: k[0])
        already_done = set()
        for _, t in top_level:
            if t not in already_done:
                lines.append(t.as_multi_line(self._templates, indentation=indentation))
                already_done.add(t)
        return '\n\n'.join(lines)

    def write(self, filename, indentation=4):
        """Writes the FileTree to a disk as a text file

        The first few lines will contain the placeholders.
        The remaining lines will contain the actual FileTree with all the templates (including sub-trees).
        The top-level directory is not stored in the file and hence will need to be provided when reading the tree from the file.

        Args:
            filename (str or Path): where to store the file (directory should exist already)
            indentation (int, optional): Number of spaces to use in indendation. Defaults to 4.
        """
        with open(filename, 'w') as f:
            f.write(self.to_string(indentation=indentation))

    def report(self, fill=True, pager=False):
        """Prints a formatted report of the filetree to the console.

        Prints a report of the file-tree to the terminal with:
        - table with placeholders and their values
        - tree of templates with template keys marked in cyan

        Args:
            fill (bool, optional): by default any fixed placeholders are filled in before printing the tree (using :meth:`fill`). Set to False to disable this.
            pager (bool, optional): if set to True, the report will be filed into a pager (recommended if the output is very large)
        """
        if fill:
            self = self.fill()

        if pager:
            from rich.console import Console
            printer = Console()
            with printer.pager():
                for part in self._generate_rich_report():
                    printer.print(part)
        else:
            for part in self._generate_rich_report():
                rich.print(part)

    def _generate_rich_report(self):
        """
        Generates a sequence of Rich renderables to produce report
        """
        from rich.table import Table
        from rich.tree import Tree
        single_var_table = Table("name", "value", title="Defined placeholders")
        multi_var_table = Table("name", "value", title="Placeholders with multiple options")
        linked_vars = []
        for key, value in self.placeholders.items():
            if value is None:
                continue
            if isinstance(key, frozenset):
                linked_vars.append(key)
                for linked_key, linked_value in value.items():
                    multi_var_table.add_row(linked_key, ', '.join(str(v) for v in linked_value))
            elif np.array(value).ndim == 1:
                multi_var_table.add_row(key, ', '.join(str(v) for v in value))
            else:
                single_var_table.add_row(key, value)
        if single_var_table.row_count > 0:
            yield single_var_table
        if multi_var_table.row_count > 0:
            yield multi_var_table
        if len(linked_vars) > 0:
            yield "Linked variables:\n" + ("\n".join([', '.join(v) for v in linked_vars]))

        def add_children(t: Template, tree: Optional[Tree]):
            for child in t.children(self._templates.values()):
                child_tree = tree.add(child.rich_line(self._templates))
                add_children(child, child_tree)

        top_level = sorted([(key, template) for key, template in self._templates.items() if template.parent is None], key=lambda k: k[0])
        already_done = set()
        for _, t in top_level:
            if t not in already_done:
                base_tree = Tree(t.rich_line(self._templates))
                add_children(t, base_tree)
                yield base_tree

    def run_app(self, ):
        """
        Open a terminal-based App to explore the filetree interactively

        The resulting app runs directly in the terminal, 
        so it should work when ssh'ing to some remote cluster.

        There will be two panels:

            - The left panel will show all the templates in a tree format. 
              Template keys are shown in cyan. 
              For each template the number of files that exist on disc out of the total number is shown
              colour coded based on completeness (red: no files; yellow: some files; blue: all files).
              Templates can be selected by hovering over them.
              Clicking on directories with hide/show their content.
            - The right panel will show for the selected template the complete template string
              and a table showing for which combination of placeholders the file is present/absent
              (rows for absent files are colour-coded red).
        """
        from . import app
        app._current_tree = self
        app.FileTreeViewer.run()
        app._current_tree = None


def convert(src_tree: FileTree, target_tree: Optional[FileTree]=None, keys=None, symlink=False, overwrite=False):
    """
    Copies or links files defined in `keys` from the `src_tree` to the `target_tree`.

    Given two example trees
    
        - source:: 

            subject = A,B

            sub-{subject}
                data
                    T1w.nii.gz
                    FLAIR.nii.gz

        - target:: 

            subject = A,B

            data
                sub-{subject}
                    {subject}-T1w.nii.gz (T1w)
                    {subject}-T2w.nii.gz (T2w)

    Given pre-existing data matching the source tree::

        .
        ├── sub-A
        │   └── data
        │       ├── FLAIR.nii.gz
        │       └── T1w.nii.gz
        └── sub-B
            └── data
                ├── FLAIR.nii.gz
                └── T1w.nii.gz

    We can do the following conversions:

        - `convert(source, target)`: 
            copies all matching keys from `source` to `target`. 
            This will only copy the "T1w.nii.gz" files, because they are the only match in the template keys.
            Note that the `data` template key also matches between the two trees, but this template is not a leave, so is ignored.
        - `convert(source, target, keys=['T1w', ('FLAIR', 'T2w')])`: 
            copies the "T1w.nii.gz" files from `source` to `target` and 
            copies the "FLAIR.nii.gz" in `source` to "T2w..nii.gz" in `target`.
        - `convert(source.update(subject='B'), source.update(subject='C'))`: 
            creates a new "data/sub-C" directory and 
            copies all the data from "data/sub-B" into that directory.
        - `convert(source, keys=[('FLAIR', 'T1w')], overwrite=True)`: 
            copies the "FLAIR.nii.gz" into the "T1w.nii.gz" files overwriting the originals.

    Warnings are raised in two cases:
    - if a source file is missing
    - if a target file already exists and `overwrite` is False

    Args:
        src_tree: prepopulated filetree with the source files
        target_tree: filetree that will be populated. Defaults to same as `src_tree`.
        keys (collection of str or (str, str), optional): collection of template keys to transfer from `src_tree` to `target_tree`. Defaults to all templates keys shared between `src_tree` and `target_tree`.
        symlink: if set to true links the files rather than copying them
        overwrite: if set to True overwrite any existing files
    """
    if target_tree is None and keys is None:
        raise ValueError("Conversion requires either `target_tree` or `keys` to be set")
    src_tree = src_tree.copy()
    if target_tree is None:
        target_tree = src_tree
    target_tree = target_tree.copy()
    if keys is None:
        keys = set(src_tree.template_keys(only_leaves=True)).intersection(target_tree.template_keys(only_leaves=True))

    full_keys = {(key_definition, key_definition) if isinstance(key_definition, str) else key_definition for key_definition in keys}
    for src_key, target_key in full_keys:
        # ensure template placeholders are consistent between source and target tree
        for placeholder in src_tree.get_template(src_key).placeholders() + target_tree.get_template(target_key).placeholders():
            if placeholder not in src_tree.placeholders:
                if placeholder not in target_tree.placeholders:
                    raise ValueError(f"Can not convert template {src_key}, because no values have been set for {placeholder}")
                src_tree.placeholders[placeholder] = target_tree.placeholders[placeholder]
            elif placeholder not in target_tree.placeholders:
                target_tree.placeholders[placeholder] = src_tree.placeholders[placeholder]
            nsrc = -1 if is_singular(src_tree.placeholders[placeholder]) else len(src_tree.placeholders[placeholder])
            ntarget = -1 if is_singular(target_tree.placeholders[placeholder]) else len(target_tree.placeholders[placeholder])
            if nsrc != ntarget:
                raise ValueError(f"Number of possible values for {placeholder} do not match between source and target tree")

        # ensure non-singular placeholders match
        src_non_singular = {p for p in src_tree.get_template(src_key).placeholders() if not is_singular(src_tree.placeholders[p])}
        target_non_singular = {p for p in target_tree.get_template(target_key).placeholders() if not is_singular(target_tree.placeholders[p])}

        diff = src_non_singular.difference(target_non_singular)
        if len(diff) > 0:
            raise ValueError("Placholders {diff} in source template {src_key} has no equivalent in target template {target_key}")
        diff = target_non_singular.difference(src_non_singular)
        if len(diff) > 0:
            raise ValueError("Placholders {diff} in target template {target_key} has no equivalent in source template {src_key}")

    # all checks have passed; let's get to work
    to_warn_about = ([], [])

    for src_key, target_key in sorted(full_keys):
        iter_placeholders = sorted({p for p in src_tree.get_template(src_key).placeholders() if not is_singular(src_tree.placeholders[p])})
        for single_src_tree, single_target_tree in zip(
            src_tree.iter_vars(iter_placeholders),
            target_tree.iter_vars(iter_placeholders),
        ):
            _convert_file(
                Path(single_src_tree.get(src_key)), 
                Path(single_target_tree.get(target_key)),
                to_warn_about,
                symlink=symlink,
                overwrite=overwrite,
            )
    if len(to_warn_about[0]) > 0:
        warn(f"Following source files were not found during FileTree conversion: {to_warn_about[0]}")
    if len(to_warn_about[1]) > 0:
        warn(f"Following target files already existed during FileTree conversion: {to_warn_about[1]}")


def _convert_file(source: Path, target: Path, to_warn_about, symlink=False, overwrite=False):
    """
    Copies or links `source` file to `target` file

    Helper function for :func:`convert`
    """
    if not source.exists():
        to_warn_about[0].append(str(source))
        return
    if target.exists():
        if not overwrite:
            to_warn_about[1].append(str(target))
            return
        os.remove(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    if not symlink:
        copyfile(source, target, follow_symlinks=False)
    elif source.is_absolute():
        target.symlink_to(source)
    else:
        target.symlink_to(os.path.relpath(source, target.parent))
