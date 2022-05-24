# -*- coding: utf-8 -*-
# Copyright (c) 2021-2022 Salvador E. Tropea
# Copyright (c) 2021-2022 Instituto Nacional de Tecnología Industrial
# License: GPL-3.0
# Project: KiBot (formerly KiPlot)
from .gs import GS
from .pre_any_replace import TagReplaceBase, Base_ReplaceOptions, Base_Replace
from .registrable import RegDependency
from .misc import git_dependency
from .macros import macros, document, pre_class  # noqa: F401
from . import log

logger = log.get_logger()
RegDependency.register(git_dependency('pcb_replace'))


class TagReplacePCB(TagReplaceBase):
    """ Tags to be replaced for an PCB """
    def __init__(self):
        super().__init__()
        self._help_command += ".\nKIBOT_PCB_NAME variable is the name of the current PCB"


class PCB_ReplaceOptions(Base_ReplaceOptions):
    """ PCB replacement options """
    def __init__(self):
        super().__init__()
        self.replace_tags = TagReplacePCB


@pre_class
class PCB_Replace(Base_Replace):  # noqa: F821
    """ [dict] Replaces tags in the PCB. I.e. to insert the git hash or last revision date.
        This is useful for KiCad 5, use `set_text_variables` when using KiCad 6.
        This preflight modifies the PCB. Even when a back-up is done use it carefully """
    _context = 'PCB'

    def __init__(self, name, value):
        o = PCB_ReplaceOptions()
        o.set_tree(value)
        o.config(self)
        super().__init__(name, o)

    @classmethod
    def get_doc(cls):
        return cls.__doc__, PCB_ReplaceOptions

    def apply(self):
        o = self._value
        if o.date_command:
            # Convert it into another replacement
            t = TagReplacePCB()
            t.tag = r'^    \(date (\S+|"(?:[^"]|\\")+")\)$'
            t.command = o.date_command
            t.before = '    (date "'
            t.after = '")'
            t._relax_check = True
            o.replace_tags.append(t)
        self.replace(GS.pcb_file)
        # Force the schematic reload
        GS.board = None
