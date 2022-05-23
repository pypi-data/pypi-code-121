# -*- coding: utf-8 -*-

"""The graphical part of a Write Structure step"""

from pathlib import PurePath
import pprint  # noqa: F401
import tkinter as tk

from .formats.registries import get_format_metadata
import seamm
from seamm_util import ureg, Q_, units_class  # noqa: F401
import seamm_widgets as sw


class TkWriteStructure(seamm.TkNode):
    """The graphical part of a Write Structure step in a flowchart."""

    def __init__(
        self, tk_flowchart=None, node=None, canvas=None, x=None, y=None, w=200, h=50
    ):
        """Initialize a graphical node

        Keyword arguments:
            tk_flowchart: The graphical flowchart that we are in.
            node: The non-graphical node for this step.
            namespace: The stevedore namespace for finding sub-nodes.
            canvas: The Tk canvas to draw on.
            x: The x position of the nodes cetner on the canvas.
            y: The y position of the nodes cetner on the canvas.
            w: The nodes graphical width, in pixels.
            h: The nodes graphical height, in pixels.
        """
        self.dialog = None

        super().__init__(
            tk_flowchart=tk_flowchart, node=node, canvas=canvas, x=x, y=y, w=w, h=h
        )

    def create_dialog(self):
        """Create a dialog for editing the control parameters"""
        frame = super().create_dialog("Write Structure Step")

        # Create the widgets
        P = self.node.parameters
        for key in P:
            self[key] = P[key].widget(frame)

        # Set bindings
        for name in ("file", "file type"):
            combobox = self[name].combobox
            combobox.bind("<<ComboboxSelected>>", self.reset_dialog)
            combobox.bind("<Return>", self.reset_dialog)
            combobox.bind("<FocusOut>", self.reset_dialog)

        # and lay the widgets out
        self.reset_dialog()

    def reset_dialog(self, widget=None):
        """Layout the widgets in the dialog

        This initial function simply lays them out row by rows with
        aligned labels. You may wish a more complicated layout that
        is controlled by values of some of the control parameters.
        """

        # Remove any widgets previously packed
        frame = self["frame"]
        for slave in frame.grid_slaves():
            slave.grid_forget()

        # What type of file?
        extension = ""
        filename = self["file"].get().strip()
        file_type = self["file type"].get()

        if self.is_expr(filename) or self.is_expr(file_type):
            extension = "all"
        else:
            if file_type != "from extension":
                extension = file_type.split()[0]
            else:
                if filename != "":
                    path = PurePath(filename)
                    extension = path.suffix
                    if extension == ".gz":
                        extension = path.stem.suffix

        # Get the metadata for the format
        metadata = get_format_metadata(extension)

        # and put the correct ones back in.
        row = 0
        widgets = []
        for item in ("file", "file type"):
            self[item].grid(row=row, column=0, columnspan=2, sticky=tk.EW)
            widgets.append(self[item])
            row += 1
        sw.align_labels(widgets)

        items = []
        if extension == "all" or not metadata["single_structure"]:
            items.append("structures")
        items.append("remove hydrogens")
        if len(items) > 0:
            widgets = []
            for item in items:
                self[item].grid(row=row, column=1, sticky=tk.EW)
                widgets.append(self[item])
                row += 1
            sw.align_labels(widgets)

        # Set the widths and expansion
        frame.columnconfigure(0, minsize=50)
        frame.columnconfigure(1, weight=1)

    def right_click(self, event):
        """Probably need to add our dialog..."""

        super().right_click(event)
        self.popup_menu.add_command(label="Edit..", command=self.edit)

        self.popup_menu.tk_popup(event.x_root, event.y_root, 0)
