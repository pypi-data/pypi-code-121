"""
Sets up and runs the textual app for some FileTree

It is not recommended to run any of the functions in this module. 
Instead load a :class:`FileTree <file_tree.file_tree.FileTree>` and 
then run :meth:`FileTree.run_app <file_tree.file_tree.FileTree.run_app>` and 
"""
from textual.app import App
from .file_tree import FileTree, Template
from textual.widgets import ScrollView, TreeControl, TreeNode, TreeClick
from textual.message import Message
from rich.table import Table
from rich.style import Style
from rich.text import Text
import itertools
import os
from argparse import ArgumentParser
from functools import lru_cache
from textual import events

_current_tree = None


class TemplateSelect(Message, bubble=True):
    """
    Message sent when a template in the sidebar gets selected
    """
    def __init__(self, sender, template: Template):
        self.template = template
        super().__init__(sender)


class TemplateTreeControl(TreeControl[Template]):
    """
    Sidebar containing all template definitions in FileTree
    """
    def __init__(self, tree: FileTree, name: str = None):
        """
        Creates a new template sidebar based on given FileTree

        Args:
            tree: FileTree to interact with
            name: name of the sidebar within textual
        """
        self.tree = tree
        data = self.tree.get_template('')
        super().__init__(data.as_string, name=name, data=data)
        self.root.tree.guide_style = "black"
        self.current_node = None

    async def find_children(self, node: TreeNode[Template]):
        """
        Finds all the children of a template and add them to the node

        Calls itself recursively
        """
        template = node.data
        children = set()
        for child in template.children(self.tree._templates.values()):
            if child not in children:
                children.add(child)
                await node.add(child.unique_part, data=child)
        await node.expand()
        for child in node.children:
            await self.find_children(child)

    def render_node(self, node: TreeNode[Template]):
        """
        Creates a rendering for the given template in the tree

        Rendered text will contain information about the keys and the number of files on disk.

        This uses caching in the node, so that it only has to evaluate once
        """
        label = self._render_node_helper(node).copy()
        if node.id == self.hover_node:
            label.stylize("underline")
            if self.current_node != node:
                self.current_node = node
                self.emit_no_wait(TemplateSelect(self, node.data))
        if not node.expanded and len(node.children) > 0:
            label = Text("📁 ") + label
        return label

    @lru_cache(None)
    def _render_node_helper(self, node):
        meta = {
            "@click": f"click_label({node.id})",
            "tree_node": node.id,
            "cursor": node.is_cursor,
        }
        paths = self.tree.get_mult(_get_template_key(self.tree, node.data), filter=True).data.flatten()
        existing = [p for p in paths if p != '']
        color = 'blue' if len(existing) == len(paths) else 'yellow'
        if len(existing) == 0:
            color = 'red'
        counter = f" [{color}][{len(existing)}/{len(paths)}][/{color}]"
        res = Text.from_markup(node.data.rich_line(self.tree._templates) + counter, overflow='ellipsis')
        res.apply_meta(meta)
        return res

    async def on_mount(self, event):
        """
        Called when sidebar is created
        """
        await self.find_children(self.root)

    async def handle_tree_click(self, message: TreeClick[Template]):
        """
        Called when node is clicked. Will emit `TemplateSelect`
        """
        await message.node.toggle()


class FileTreeViewer(App):
    """
    FileTree viewer app
    """
    async def on_load(self):
        """
        Process FileTree before viewer is created
        """
        self.tree: FileTree = _current_tree.fill().update_glob(_current_tree.template_keys(only_leaves=True))

    async def on_mount(self, ):
        """
        Create template sidebar and main viewing window
        """
        self.template_selector = TemplateTreeControl(self.tree)
        self.body = ScrollView()
        await self.view.dock(ScrollView(self.template_selector, name='scroller'), edge='left', size=40, name='sidebar')
        await self.view.dock(self.body)

    async def handle_template_select(self, message: TemplateSelect):
        """User has selected a template"""
        template = message.template
        self.app.sub_title = template.as_string
        await self.body.update(TemplateRenderer(template, self.tree))


def _get_template_key(tree, template):
    keys = {k for k, t in tree._templates.items() if t is template}
    return next(iter(keys))


class TemplateRenderer:
    """
    Helper class to create a Rich rendering of a template

    There are two parts:
    - a text file with the template
    - a table with the possible placeholder value combinations (shaded red for non-existing files)
    """
    def __init__(self, template: Template, tree: FileTree):
        self.template = template
        self.tree = tree

    def __rich_console__(self, console, options):
        yield self.template.as_string
        xr = self.tree.get_mult(_get_template_key(self.tree, self.template), filter=True)
        coords = sorted(xr.coords.keys())
        single_var_table = Table(*coords)
        for values in itertools.product(*[xr.coords[c].data for c in coords]):
            path = xr.sel(**{c: v for c, v in zip(coords, values)}).item()
            style = Style(
                bgcolor=None if path != '' else 'red'
            )
            single_var_table.add_row(*[str(v) for v in values], style=style)
        yield single_var_table


def run():
    """CLI interface to app"""
    parser = ArgumentParser(description="Interactive terminal-based interface with file-trees")
    parser.add_argument("file_tree", help="Which file-tree to visualise")
    parser.add_argument("-d", "--directory", default='.', help="top-level directory")
    args = parser.parse_args()
    FileTree.read(args.file_tree, args.directory).run_app()