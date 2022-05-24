# -*- coding: utf-8 -*-
# Copyright (c) 2022 Salvador E. Tropea
# Copyright (c) 2022 Instituto Nacional de Tecnología Industrial
# License: GPL-3.0
# Project: KiBot (formerly KiPlot)
import os
import sys
import json
from subprocess import run, PIPE
from .error import KiPlotConfigurationError
from .misc import FAILED_EXECUTE, W_EMPTREP, git_dependency
from .optionable import Optionable
from .pre_base import BasePreFlight
from .gs import GS
from .registrable import RegDependency
from .macros import macros, document, pre_class  # noqa: F401
from . import log

logger = log.get_logger()
RegDependency.register(git_dependency('set_text_variables'))


class KiCadVariable(Optionable):
    """ KiCad variable definition """
    def __init__(self):
        super().__init__()
        self._unkown_is_error = True
        with document:
            self.name = ''
            """ Name of the variable. The `version` variable will be expanded using `${version}` """
            self.variable = None
            """ {name} """
            self.text = ''
            """ Text to insert instead of the variable """
            self.command = ''
            """ Command to execute to get the text, will be used only if `text` is empty """
            self.before = ''
            """ Text to add before the output of `command` """
            self.after = ''
            """ Text to add after the output of `command` """
            self.expand_kibot_patterns = True
            """ Expand %X patterns. The context is `schematic` """

    def config(self, parent):
        super().config(parent)
        if not self.name:
            raise KiPlotConfigurationError("Missing variable name ({})".format(str(self._tree)))


class Set_Text_VariablesOptions(Optionable):
    """ A list of KiCad variables """
    def __init__(self):
        super().__init__()
        with document:
            self.variables = KiCadVariable
            """ [dict|list(dict)] Variables """

    def config(self, parent):
        super().config(parent)
        if isinstance(self.variables, type):
            self.variables = []
        elif isinstance(self.variables, KiCadVariable):
            self.variables = [self.variables]


@pre_class
class Set_Text_Variables(BasePreFlight):  # noqa: F821
    """ [dict|list(dict)] Defines KiCad 6 variables.
        They are expanded using ${VARIABLE}, and stored in the project file.
        This preflight replaces `pcb_replace` and `sch_replace` when using KiCad 6.
        The KiCad project file is modified """
    def __init__(self, name, value):
        f = Set_Text_VariablesOptions()
        f.set_tree({'variables': value})
        f.config(self)
        super().__init__(name, f.variables)

    @classmethod
    def get_doc(cls):
        return cls.__doc__, KiCadVariable

    @classmethod
    def get_example(cls):
        """ Returns a YAML value for the example config """
        return ("\n    - name: 'git_hash'"
                "\n      command: 'git log -1 --format=\"%h\" $KIBOT_PCB_NAME'"
                "\n      before: 'Git hash: <'"
                "\n      after: '>'")

    def apply(self):
        o = self._value
        if len(o) == 0:
            return
        if GS.ki5():
            raise KiPlotConfigurationError("The `set_text_variables` preflight is for KiCad 6 or newer")
        pro_name = GS.pro_file
        if not pro_name or not os.path.isfile(pro_name):
            raise KiPlotConfigurationError("Trying to define KiCad 6 variables but the project is missing ({})".
                                           format(pro_name))
        # Get the current definitions
        with open(pro_name, 'rt') as f:
            pro_text = f.read()
        data = json.loads(pro_text)
        text_variables = data.get('text_variables', {})
        GS.pro_variables = text_variables
        logger.debug("- Current variables: {}".format(text_variables))
        # Define the requested variables
        if GS.pcb_file:
            os.environ['KIBOT_PCB_NAME'] = GS.pcb_file
        if GS.sch_file:
            os.environ['KIBOT_SCH_NAME'] = GS.sch_file
        for r in o:
            text = r.text
            if not text:
                cmd = ['/bin/bash', '-c', r.command]
                result = run(cmd, stdout=PIPE, stderr=PIPE, universal_newlines=True)
                if result.returncode:
                    logger.error('Failed to execute:\n{}\nreturn code {}'.format(r.command, result.returncode))
                    sys.exit(FAILED_EXECUTE)
                if not result.stdout:
                    logger.warning(W_EMPTREP+"Empty value from `{}` skipping it".format(r.command))
                    continue
                text = result.stdout.strip()
            text = r.before + text + r.after
            logger.debug('  - ' + r.name + ' -> ' + text)
            text_variables[r.name] = text
        logger.debug("- Expanding %X patterns in variables")
        # Now that we have the variables defined expand the %X patterns (they could use variables)
        for r in o:
            if r.expand_kibot_patterns:
                text = text_variables[r.name]
                new_text = Optionable.expand_filename_both(self, text, make_safe=False)
                if text != new_text:
                    logger.debug('  - ' + r.name + ' -> ' + new_text)
                    text_variables[r.name] = new_text
        logger.debug("- New list of variables: {}".format(text_variables))
        # Store the modified project
        data['text_variables'] = text_variables
        GS.make_bkp(pro_name)
        with open(pro_name, 'wt') as f:
            f.write(json.dumps(data, sort_keys=True, indent=2))
        # Force the PCB reload (will reload the project file)
        GS.board = None
