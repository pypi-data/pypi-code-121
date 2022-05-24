# -*- coding: utf-8 -*-
# Copyright (c) 2021 Salvador E. Tropea
# Copyright (c) 2021 Instituto Nacional de Tecnología Industrial
# License: GPL-3.0
# Project: KiBot (formerly KiPlot)
import os
from .gs import GS
from .kiplot import load_sch
from .pre_any_replace import TagReplaceBase, Base_ReplaceOptions, Base_Replace
from .registrable import RegDependency
from .misc import git_dependency
from .macros import macros, document, pre_class  # noqa: F401
from . import log

logger = log.get_logger()
RegDependency.register(git_dependency('sch_replace'))


class TagReplaceSCH(TagReplaceBase):
    """ Tags to be replaced for an SCH """
    def __init__(self):
        super().__init__()
        self._help_command += (".\nKIBOT_SCH_NAME variable is the name of the current sheet."
                               "\nKIBOT_TOP_SCH_NAME variable is the name of the top sheet")


class SCH_ReplaceOptions(Base_ReplaceOptions):
    """ SCH replacement options """
    def __init__(self):
        super().__init__()
        self._help_date_command = self._help_date_command.replace('PCB', 'SCH')
        self.replace_tags = TagReplaceSCH


@pre_class
class SCH_Replace(Base_Replace):  # noqa: F821
    """ [dict] Replaces tags in the schematic. I.e. to insert the git hash or last revision date.
        This is useful for KiCad 5, use `set_text_variables` when using KiCad 6.
        This preflight modifies the schematics. Even when a back-up is done use it carefully """
    _context = 'SCH'

    def __init__(self, name, value):
        o = SCH_ReplaceOptions()
        o.set_tree(value)
        o.config(self)
        super().__init__(name, o)

    @classmethod
    def get_doc(cls):
        return cls.__doc__, SCH_ReplaceOptions

    def apply(self):
        o = self._value
        if o.date_command:
            # Convert it into another replacement
            t = TagReplaceSCH()
            if GS.ki5():
                t.tag = r'^Date ("(?:[^"]|\\")*")$'
                t.before = 'Date "'
                t.after = '"'
            else:
                t.tag = r'\(date ("(?:[^"]|\\")*")\)'
                t.before = '(date "'
                t.after = '")'
            t.command = o.date_command
            t._relax_check = True
            o.replace_tags.append(t)
        load_sch()
        os.environ['KIBOT_TOP_SCH_NAME'] = GS.sch_file
        for file in GS.sch.get_files():
            self.replace(file)
        # Force the schematic reload
        GS.sch = None
