# -*- coding: utf-8 -*-
# Copyright (c) 2020-2022 Salvador E. Tropea
# Copyright (c) 2020-2022 Instituto Nacional de Tecnología Industrial
# Copyright (c) 2018 John Beard
# License: GPL-3.0
# Project: KiBot (formerly KiPlot)
# Adapted from: https://github.com/johnbeard/kiplot
"""
Main KiBot code
"""

import os
import re
from sys import exit
from sys import path as sys_path
from shutil import which
from subprocess import run, PIPE
from glob import glob
from distutils.version import StrictVersion
from importlib.util import (spec_from_file_location, module_from_spec)
from collections import OrderedDict

from .gs import GS
from .registrable import RegOutput
from .misc import (PLOT_ERROR, MISSING_TOOL, CMD_EESCHEMA_DO, URL_EESCHEMA_DO, CORRUPTED_PCB,
                   EXIT_BAD_ARGS, CORRUPTED_SCH, EXIT_BAD_CONFIG, WRONG_INSTALL, UI_SMD, UI_VIRTUAL, TRY_INSTALL_CHECK,
                   MOD_SMD, MOD_THROUGH_HOLE, MOD_VIRTUAL, W_PCBNOSCH, W_NONEEDSKIP, W_WRONGCHAR, name2make, W_TIMEOUT,
                   W_KIAUTO, W_VARSCH, NO_SCH_FILE, NO_PCB_FILE, W_VARPCB, NO_YAML_MODULE, WRONG_ARGUMENTS)
from .error import PlotError, KiPlotConfigurationError, config_error, trace_dump
from .config_reader import CfgYamlReader
from .pre_base import BasePreFlight
from .kicad.v5_sch import Schematic, SchFileError, SchError
from .kicad.v6_sch import SchematicV6
from .kicad.config import KiConfError
from . import log

logger = log.get_logger()
# Cache to avoid running external many times to check their versions
script_versions = {}
actions_loaded = False

try:
    import yaml
except ImportError:
    log.init()
    logger.error('No yaml module for Python, install python3-yaml')
    logger.error(TRY_INSTALL_CHECK)
    exit(NO_YAML_MODULE)


def _import(name, path):
    # Python 3.4+ import mechanism
    spec = spec_from_file_location("kibot."+name, path)
    mod = module_from_spec(spec)
    try:
        spec.loader.exec_module(mod)
    except ImportError as e:
        trace_dump()
        logger.error('Unable to import plug-ins: '+str(e))
        logger.error('Make sure you used `--no-compile` if you used pip for installation')
        logger.error('Python path: '+str(sys_path))
        exit(WRONG_INSTALL)


def _load_actions(path, load_internals=False):
    logger.debug("Importing from "+path)
    lst = glob(os.path.join(path, 'out_*.py')) + glob(os.path.join(path, 'pre_*.py'))
    lst += glob(os.path.join(path, 'var_*.py')) + glob(os.path.join(path, 'fil_*.py'))
    if load_internals:
        lst += [os.path.join(path, 'globals.py')]
    for p in lst:
        name = os.path.splitext(os.path.basename(p))[0]
        logger.debug("- Importing "+name)
        _import(name, p)


def load_actions():
    """ Load all the available outputs and preflights """
    global actions_loaded
    if actions_loaded:
        return
    actions_loaded = True
    from kibot.mcpyrate import activate
    # activate.activate()
    _load_actions(os.path.abspath(os.path.dirname(__file__)), True)
    home = os.environ.get('HOME')
    if home:
        dir = os.path.join(home, '.config', 'kiplot', 'plugins')
        if os.path.isdir(dir):
            _load_actions(dir)
        dir = os.path.join(home, '.config', 'kibot', 'plugins')
        if os.path.isdir(dir):
            _load_actions(dir)
    # de_activate in old mcpy
    if 'deactivate' in activate.__dict__:
        logger.debug('Deactivating macros')
        activate.deactivate()


def check_version(command, version):
    global script_versions
    if command in script_versions:
        return
    cmd = [command, '--version']
    logger.debug('Running: '+str(cmd))
    result = run(cmd, stdout=PIPE, stderr=PIPE, universal_newlines=True)
    z = re.match(command + r' (\d+\.\d+\.\d+)', result.stdout, re.IGNORECASE)
    if not z:
        z = re.search(r'Version: (\d+\.\d+\.\d+)', result.stdout, re.IGNORECASE)
    if not z:
        logger.error('Unable to determine ' + command + ' version:\n' +
                     result.stdout)
        exit(MISSING_TOOL)
    res = z.groups()
    if StrictVersion(res[0]) < StrictVersion(version):
        logger.error('Wrong version for `'+command+'` ('+res[0]+'), must be ' +
                     version+' or newer.')
        exit(MISSING_TOOL)
    script_versions[command] = res[0]


def check_script(cmd, url, version=None):
    if which(cmd) is None:
        logger.error('No `'+cmd+'` command found.\n'
                     'Please install it, visit: '+url)
        logger.error(TRY_INSTALL_CHECK)
        exit(MISSING_TOOL)
    if version is not None:
        check_version(cmd, version)


def check_eeschema_do():
    check_script(CMD_EESCHEMA_DO, URL_EESCHEMA_DO, '1.5.4')


def search_as_plugin(cmd, names):
    """ If a command isn't in the path look for it in the KiCad plugins """
    if which(cmd) is not None:
        return cmd
    for dir in GS.kicad_plugins_dirs:
        for name in names:
            fname = os.path.join(dir, name, cmd)
            if os.path.isfile(fname):
                logger.debug('Using `{}` for `{}` ({})'.format(fname, cmd, name))
                return fname
    return cmd


def extract_errors(text):
    in_error = in_warning = False
    msg = ''
    for line in text.split('\n'):
        line += '\n'
        if line[0] == ' ' and (in_error or in_warning):
            msg += line
        else:
            if in_error:
                in_error = False
                logger.error(msg.rstrip())
            elif in_warning:
                in_warning = False
                logger.warning(W_KIAUTO+msg.rstrip())
        if line.startswith('ERROR:'):
            in_error = True
            msg = line[6:]
        elif line.startswith('WARNING:'):
            in_warning = True
            msg = line[8:]
    if in_error:
        in_error = False
        logger.error(msg.rstrip())
    elif in_warning:
        in_warning = False
        logger.warning(W_KIAUTO+msg.rstrip())


def exec_with_retry(cmd):
    logger.debug('Executing: '+str(cmd))
    if GS.debug_level > 2:
        logger.debug('Command line: '+' '.join(cmd))
    retry = 2
    while retry:
        result = run(cmd, stdout=PIPE, stderr=PIPE, universal_newlines=True)
        ret = result.returncode
        retry -= 1
        if ret != 16 and (ret > 0 and ret < 128 and retry):
            # 16 is KiCad crash
            logger.debug('Failed with error {}, retrying ...'.format(ret))
        else:
            extract_errors(result.stderr)
            err = '> '+result.stderr.replace('\n', '\n> ')
            logger.debug('Output from command:\n'+err)
            if 'Timed out' in err:
                logger.warning(W_TIMEOUT+'Time out detected, on slow machines or complex projects try:')
                logger.warning(W_TIMEOUT+'`kiauto_time_out_scale` and/or `kiauto_wait_start` global options')
            return ret


def add_extra_options(cmd):
    is_gitlab_ci = 'GITLAB_CI' in os.environ
    video_remove = (not GS.debug_enabled) and is_gitlab_ci
    if GS.debug_enabled:
        cmd.insert(1, '-'+'v'*GS.debug_level)
    if GS.debug_enabled or is_gitlab_ci:
        # Forcing record on GitLab CI/CD (black magic)
        cmd.insert(1, '-r')
    if GS.global_kiauto_time_out_scale:
        cmd.insert(1, str(GS.global_kiauto_time_out_scale))
        cmd.insert(1, '--time_out_scale')
    if GS.global_kiauto_wait_start:
        cmd.insert(1, str(GS.global_kiauto_wait_start))
        cmd.insert(1, '--wait_start')
    return cmd, video_remove


def load_board(pcb_file=None):
    if GS.board is not None:
        # Already loaded
        return GS.board
    import pcbnew
    if not pcb_file:
        GS.check_pcb()
        pcb_file = GS.pcb_file
    try:
        board = pcbnew.LoadBoard(pcb_file)
        if BasePreFlight.get_option('check_zone_fills'):
            pcbnew.ZONE_FILLER(board).Fill(board.Zones())
        if GS.global_units and GS.ki6():
            # In KiCad 6 "dimensions" has units.
            # The default value is DIM_UNITS_MODE_AUTOMATIC.
            # But this has a meaning only in the GUI where you have default units.
            # So now we have global.units and here we patch the board.
            UNIT_NAME_TO_INDEX = {'millimeters': pcbnew.DIM_UNITS_MODE_MILLIMETRES,
                                  'inches': pcbnew.DIM_UNITS_MODE_INCHES,
                                  'mils': pcbnew.DIM_UNITS_MODE_MILS}
            forced_units = UNIT_NAME_TO_INDEX[GS.global_units]
            for dr in board.GetDrawings():
                if dr.GetClass().startswith('PCB_DIM_') and dr.GetUnitsMode() == pcbnew.DIM_UNITS_MODE_AUTOMATIC:
                    dr.SetUnitsMode(forced_units)
                    dr.Update()
        GS.board = board
    except OSError as e:
        logger.error('Error loading PCB file. Corrupted?')
        logger.error(e)
        exit(CORRUPTED_PCB)
    assert board is not None
    logger.debug("Board loaded")
    return board


def load_any_sch(file, project):
    if file[-9:] == 'kicad_sch':
        sch = SchematicV6()
        load_libs = False
    else:
        sch = Schematic()
        load_libs = True
    try:
        sch.load(file, project)
        if load_libs:
            sch.load_libs(file)
        if GS.debug_level > 1:
            logger.debug('Schematic dependencies: '+str(sch.get_files()))
    except SchFileError as e:
        trace_dump()
        logger.error('At line {} of `{}`: {}'.format(e.line, e.file, e.msg))
        logger.error('Line content: `{}`'.format(e.code))
        exit(CORRUPTED_SCH)
    except SchError as e:
        trace_dump()
        logger.error('While loading `{}`'.format(file))
        logger.error(str(e))
        exit(CORRUPTED_SCH)
    except KiConfError as e:
        trace_dump()
        logger.error('At line {} of `{}`: {}'.format(e.line, e.file, e.msg))
        logger.error('Line content: `{}`'.format(e.code))
        exit(EXIT_BAD_CONFIG)
    return sch


def load_sch():
    if GS.sch:  # Already loaded
        return
    GS.check_sch()
    GS.sch = load_any_sch(GS.sch_file, GS.sch_basename)


def get_board_comps_data(comps):
    """ Add information from the PCB to the list of components from the schematic.
        Note that we do it every time the function is called to reset transformation filters like rot_footprint. """
    if not GS.pcb_file:
        return
    load_board()
    comps_hash = {c.ref: c for c in comps}
    for m in GS.get_modules():
        ref = m.GetReference()
        if ref not in comps_hash:
            logger.warning(W_PCBNOSCH + '`{}` component in board, but not in schematic'.format(ref))
            continue
        c = comps_hash[ref]
        c.bottom = m.IsFlipped()
        c.footprint_rot = m.GetOrientationDegrees()
        center = GS.get_center(m)
        c.footprint_x = center.x
        c.footprint_y = center.y
        (c.footprint_w, c.footprint_h) = GS.get_fp_size(m)
        attrs = m.GetAttributes()
        if GS.ki5():
            # KiCad 5
            if attrs == UI_SMD:
                c.smd = True
            elif attrs == UI_VIRTUAL:
                c.virtual = True
            else:
                c.tht = True
        else:
            # KiCad 6
            if attrs & MOD_SMD:
                c.smd = True
            if attrs & MOD_THROUGH_HOLE:
                c.tht = True
            if attrs & MOD_VIRTUAL == MOD_VIRTUAL:
                c.virtual = True


def preflight_checks(skip_pre):
    logger.debug("Preflight checks")

    if skip_pre is not None:
        if skip_pre == 'all':
            logger.debug("Skipping all preflight actions")
            return
        else:
            skip_list = skip_pre.split(',')
            for skip in skip_list:
                if skip == 'all':
                    logger.error('All can\'t be part of a list of actions '
                                 'to skip. Use `--skip all`')
                    exit(EXIT_BAD_ARGS)
                else:
                    if not BasePreFlight.is_registered(skip):
                        logger.error('Unknown preflight `{}`'.format(skip))
                        exit(EXIT_BAD_ARGS)
                    o_pre = BasePreFlight.get_preflight(skip)
                    if not o_pre:
                        logger.warning(W_NONEEDSKIP + '`{}` preflight is not in use, no need to skip'.format(skip))
                    else:
                        logger.debug('Skipping `{}`'.format(skip))
                        o_pre.disable()
    BasePreFlight.run_enabled()


def get_output_dir(o_dir, obj, dry=False):
    # outdir is a combination of the config and output
    outdir = os.path.abspath(obj.expand_dirname(os.path.join(GS.out_dir, o_dir)))
    # Create directory if needed
    logger.debug("Output destination: {}".format(outdir))
    if not dry and not os.path.exists(outdir):
        os.makedirs(outdir)
    return outdir


def config_output(out, dry=False, dont_stop=False):
    if out._configured:
        return True
    # Should we load the PCB?
    if not dry:
        if out.is_pcb():
            load_board()
        if out.is_sch():
            load_sch()
    ok = True
    try:
        out.config(None)
    except KiPlotConfigurationError as e:
        msg = "In section '"+out.name+"' ("+out.type+"): "+str(e)
        if dont_stop:
            logger.error(msg)
        else:
            config_error(msg)
        ok = False
    except SystemExit:
        if not dont_stop:
            raise
        ok = False
    return ok


def run_output(out, dont_stop=False):
    if out._done:
        return
    GS.current_output = out.name
    try:
        out.run(get_output_dir(out.dir, out))
        out._done = True
    except PlotError as e:
        logger.error("In output `"+str(out)+"`: "+str(e))
        if not dont_stop:
            exit(PLOT_ERROR)
    except KiPlotConfigurationError as e:
        msg = "In section '"+out.name+"' ("+out.type+"): "+str(e)
        if dont_stop:
            logger.error(msg)
        else:
            config_error(msg)
    except SystemExit:
        if not dont_stop:
            raise


def generate_outputs(outputs, target, invert, skip_pre, cli_order, dont_stop=False):
    logger.debug("Starting outputs for board {}".format(GS.pcb_file))
    preflight_checks(skip_pre)
    # Check if the preflights pulled options
    for out in RegOutput.get_prioritary_outputs():
        if config_output(out, dont_stop=dont_stop):
            logger.info('- '+str(out))
            run_output(out, dont_stop=dont_stop)
    # Check if all must be skipped
    n = len(target)
    if n == 0 and invert:
        # Skip all targets
        logger.debug('Skipping all outputs')
        return
    # Check we got a valid list of outputs
    for name in target:
        out = RegOutput.get_output(name)
        if out is None:
            logger.error('Unknown output `{}`'.format(name))
            exit(EXIT_BAD_ARGS)
    # Generate outputs
    if cli_order and not invert:
        # Use the CLI order
        for name in target:
            out = RegOutput.get_output(name)
            if config_output(out, dont_stop=dont_stop):
                logger.info('- '+str(out))
                run_output(out, dont_stop)
    else:
        # Use the declaration order
        for out in RegOutput.get_outputs():
            if (((n == 0 or ((out.name not in target) and invert)) and out.run_by_default) or
               ((out.name in target) and not invert)):
                if config_output(out, dont_stop=dont_stop):
                    logger.info('- '+str(out))
                    run_output(out, dont_stop)
            else:
                logger.debug('Skipping `%s` output', str(out))


def adapt_file_name(name):
    if not name.startswith('/usr'):
        name = os.path.relpath(name)
    name = name.replace(' ', r'\ ')
    if '$' in name:
        logger.warning(W_WRONGCHAR+'Wrong character in file name `{}`'.format(name))
    return name


def gen_global_targets(f, pre_targets, out_targets, type):
    extra_targets = []
    pre = 'pre_'+type
    out = 'out_'+type
    all = 'all_'+type
    if pre_targets:
        f.write('{}:{}\n\n'.format(pre, pre_targets))
        extra_targets.append(pre)
    if out_targets:
        f.write('{}:{}\n\n'.format(out, out_targets))
        extra_targets.append(out)
    if pre_targets or out_targets:
        tg = ''
        if pre_targets:
            tg = ' '+pre
        if out_targets:
            tg += ' '+out
        f.write('{}:{}\n\n'.format(all, tg))
        extra_targets.append(all)
    return extra_targets


def get_pre_targets(targets, dependencies, is_pre):
    pcb_targets = sch_targets = ''
    prefs = BasePreFlight.get_in_use_objs()
    try:
        for pre in prefs:
            tg = pre.get_targets()
            if not tg:
                continue
            name = pre._name
            targets[name] = [adapt_file_name(fn) for fn in tg]
            dependencies[name] = [adapt_file_name(fn) for fn in pre.get_dependencies()]
            is_pre.add(name)
            if pre.is_sch():
                sch_targets += ' '+name
            if pre.is_pcb():
                pcb_targets += ' '+name
    except KiPlotConfigurationError as e:
        config_error("In preflight '"+name+"': "+str(e))
    return pcb_targets, sch_targets


def get_out_targets(outputs, ori_names, targets, dependencies, comments):
    pcb_targets = sch_targets = ''
    try:
        for out in outputs:
            name = name2make(out.name)
            ori_names[name] = out.name
            tg = out.get_targets(out.expand_dirname(os.path.join(GS.out_dir, out.dir)))
            if not tg:
                continue
            targets[name] = [adapt_file_name(fn) for fn in tg]
            dependencies[name] = [adapt_file_name(fn) for fn in out.get_dependencies()]
            if out.comment:
                comments[name] = out.comment
            if out.is_sch():
                sch_targets += ' '+name
            if out.is_pcb():
                pcb_targets += ' '+name
    except KiPlotConfigurationError as e:
        config_error("In output '"+name+"': "+str(e))
    return pcb_targets, sch_targets


def generate_makefile(makefile, cfg_file, outputs, kibot_sys=False):
    cfg_file = os.path.relpath(cfg_file)
    logger.info('- Creating makefile `{}` from `{}`'.format(makefile, cfg_file))
    with open(makefile, 'wt') as f:
        f.write('#!/usr/bin/make\n')
        f.write('# Automatically generated by KiBot from `{}`\n'.format(cfg_file))
        fname = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src', 'kibot'))
        if kibot_sys or not os.path.isfile(fname):
            fname = 'kibot'
        f.write('KIBOT?={}\n'.format(fname))
        dbg = ''
        if GS.debug_level > 0:
            dbg = '-'+'v'*GS.debug_level
        f.write('DEBUG?={}\n'.format(dbg))
        f.write('CONFIG={}\n'.format(cfg_file))
        if GS.sch_file:
            f.write('SCH={}\n'.format(os.path.relpath(GS.sch_file)))
        if GS.pcb_file:
            f.write('PCB={}\n'.format(os.path.relpath(GS.pcb_file)))
        f.write('DEST={}\n'.format(os.path.relpath(GS.out_dir)))
        f.write('KIBOT_CMD=$(KIBOT) $(DEBUG) -c $(CONFIG) -e $(SCH) -b $(PCB) -d $(DEST)\n')
        f.write('LOGFILE?=kibot_error.log\n')
        f.write('\n')
        # Configure all outputs
        for out in outputs:
            config_output(out)
        # Get all targets and dependencies
        targets = OrderedDict()
        dependencies = OrderedDict()
        comments = {}
        ori_names = {}
        is_pre = set()
        # Preflights
        pre_pcb_targets, pre_sch_targets = get_pre_targets(targets, dependencies, is_pre)
        # Outputs
        out_pcb_targets, out_sch_targets = get_out_targets(outputs, ori_names, targets, dependencies, comments)
        # all target
        f.write('#\n# Default target\n#\n')
        f.write('all: '+' '.join(targets.keys())+'\n\n')
        extra_targets = ['all']
        # PCB/SCH specific targets
        f.write('#\n# SCH/PCB targets\n#\n')
        extra_targets.extend(gen_global_targets(f, pre_sch_targets, out_sch_targets, 'sch'))
        extra_targets.extend(gen_global_targets(f, pre_pcb_targets, out_pcb_targets, 'pcb'))
        # Generate the output targets
        f.write('#\n# Available targets (outputs)\n#\n')
        for name, target in targets.items():
            f.write(name+': '+' '.join(target)+'\n\n')
        # Generate the output dependencies
        f.write('#\n# Rules and dependencies\n#\n')
        if GS.debug_enabled:
            kibot_cmd = '\t$(KIBOT_CMD)'
            log_action = ''
        else:
            kibot_cmd = '\t@$(KIBOT_CMD)'
            log_action = ' 2>> $(LOGFILE)'
        for name, dep in dependencies.items():
            if name in comments:
                f.write('# '+comments[name]+'\n')
            dep.append(cfg_file)
            f.write(' '.join(targets[name])+': '+' '.join(dep)+'\n')
            if name in is_pre:
                skip = filter(lambda n: n != name, is_pre)
                f.write('{} -s {} -i{}\n\n'.format(kibot_cmd, ','.join(skip), log_action))
            else:
                f.write('{} -s all "{}"{}\n\n'.format(kibot_cmd, ori_names[name], log_action))
        # Mark all outputs as PHONY
        f.write('.PHONY: '+' '.join(extra_targets+list(targets.keys()))+'\n')


def guess_ki6_sch(schematics):
    schematics = list(filter(lambda x: x.endswith('.kicad_sch'), schematics))
    if len(schematics) == 1:
        return schematics[0]
    if len(schematics) == 0:
        return None
    for fname in schematics:
        with open(fname, 'rt') as f:
            text = f.read()
        if 'sheet_instances' in text:
            return fname
    return None


def solve_schematic(base_dir, a_schematic=None, a_board_file=None, config=None, sug_e=True):
    schematic = a_schematic
    if not schematic and a_board_file:
        base = os.path.splitext(a_board_file)[0]
        sch = os.path.join(base_dir, base+'.sch')
        if os.path.isfile(sch):
            schematic = sch
        else:
            sch = os.path.join(base_dir, base+'.kicad_sch')
            if os.path.isfile(sch):
                schematic = sch
    if not schematic:
        schematics = glob(os.path.join(base_dir, '*.sch'))
        if GS.ki6():
            schematics += glob(os.path.join(base_dir, '*.kicad_sch'))
        if len(schematics) == 1:
            schematic = schematics[0]
            logger.info('Using SCH file: '+os.path.relpath(schematic))
        elif len(schematics) > 1:
            # Look for a schematic with the same name as the config
            if config:
                if config[0] == '.':
                    # Unhide hidden config
                    config = config[1:]
                # Remove any extension
                while '.' in config:
                    config = os.path.splitext(config)[0]
                # Try KiCad 5
                sch = os.path.join(base_dir, config+'.sch')
                if os.path.isfile(sch):
                    schematic = sch
                elif GS.ki6():
                    # Try KiCad 6
                    sch = os.path.join(base_dir, config+'.kicad_sch')
                    if os.path.isfile(sch):
                        schematic = sch
            if not schematic:
                # Look for a schematic with a PCB and/or project
                for sch in schematics:
                    base = os.path.splitext(sch)[0]
                    if (os.path.isfile(os.path.join(base_dir, base+'.pro')) or
                       os.path.isfile(os.path.join(base_dir, base+'.kicad_pro')) or
                       os.path.isfile(os.path.join(base_dir, base+'.kicad_pcb'))):
                        schematic = sch
                        break
                else:
                    # No way to select one, just take the first
                    if GS.ki6():
                        schematic = guess_ki6_sch(schematics)
                    if not schematic:
                        schematic = schematics[0]
            msg = ' if you want to use another use -e option' if sug_e else ''
            logger.warning(W_VARSCH + 'More than one SCH file found in `'+base_dir+'`.\n'
                           '  Using '+schematic+msg+'.')
    if schematic and not os.path.isfile(schematic):
        logger.error("Schematic file not found: "+schematic)
        exit(NO_SCH_FILE)
    if schematic:
        schematic = os.path.abspath(schematic)
        logger.debug('Using schematic: `{}`'.format(schematic))
    else:
        logger.debug('No schematic file found')
    return schematic


def check_board_file(board_file):
    if board_file and not os.path.isfile(board_file):
        logger.error("Board file not found: "+board_file)
        exit(NO_PCB_FILE)


def solve_board_file(base_dir, a_board_file=None, sug_b=True):
    schematic = GS.sch_file
    board_file = a_board_file
    if not board_file and schematic:
        pcb = os.path.join(base_dir, os.path.splitext(schematic)[0]+'.kicad_pcb')
        if os.path.isfile(pcb):
            board_file = pcb
            logger.info('Using PCB file: '+os.path.relpath(board_file))
    if not board_file:
        board_files = glob(os.path.join(base_dir, '*.kicad_pcb'))
        if len(board_files) == 1:
            board_file = board_files[0]
            logger.info('Using PCB file: '+os.path.relpath(board_file))
        elif len(board_files) > 1:
            board_file = board_files[0]
            msg = ' if you want to use another use -b option' if sug_b else ''
            logger.warning(W_VARPCB + 'More than one PCB file found in `'+base_dir+'`.\n'
                           '  Using '+board_file+msg+'.')
    check_board_file(board_file)
    if board_file:
        logger.debug('Using PCB: `{}`'.format(board_file))
    else:
        logger.debug('No PCB file found')
    return board_file


def solve_project_file():
    if GS.pcb_file:
        pro_name = GS.pcb_no_ext+GS.pro_ext
        if os.path.isfile(pro_name):
            return pro_name
    if GS.sch_file:
        pro_name = GS.sch_no_ext+GS.pro_ext
        if os.path.isfile(pro_name):
            return pro_name
    return None


def look_for_used_layers():
    from .layer import Layer
    Layer.reset()
    layers = set()
    components = {}
    # Look inside the modules
    for m in GS.get_modules():
        layer = m.GetLayer()
        components[layer] = components.get(layer, 0)+1
        for gi in m.GraphicalItems():
            layers.add(gi.GetLayer())
        for pad in m.Pads():
            for id in pad.GetLayerSet().Seq():
                layers.add(id)
    # All drawings in the PCB
    for e in GS.board.GetDrawings():
        layers.add(e.GetLayer())
    # Zones
    for e in list(GS.board.Zones()):
        layers.add(e.GetLayer())
    # Tracks and vias
    via_type = 'VIA' if GS.ki5() else 'PCB_VIA'
    for e in GS.board.GetTracks():
        if e.GetClass() == via_type:
            for id in e.GetLayerSet().Seq():
                layers.add(id)
        else:
            layers.add(e.GetLayer())
    # Now filter the pads and vias potential layers
    declared_layers = {la._id for la in Layer.solve('all')}
    layers = sorted(declared_layers.intersection(layers))
    logger.debug('- Detected layers: {}'.format(layers))
    layers = Layer.solve(layers)
    for la in layers:
        la.components = components.get(la._id, 0)
    return layers


def discover_files(dest_dir):
    """ Look for schematic and PCBs at the dest_dir.
        Return the name of the example file to generate. """
    GS.pcb_file = None
    GS.sch_file = None
    # Check if we have useful files
    fname = os.path.join(dest_dir, 'kibot_generated.kibot.yaml')
    GS.set_sch(solve_schematic(dest_dir, sug_e=False))
    GS.set_pcb(solve_board_file(dest_dir, sug_b=False))
    GS.set_pro(solve_project_file())
    return fname


def generate_one_example(dest_dir, types):
    """ Generate a example config for dest_dir """
    fname = discover_files(dest_dir)
    # Abort if none
    if not GS.pcb_file and not GS.sch_file:
        return None
    # Reset the board and schematic
    GS.board = None
    GS.sch = None
    # Create the config
    with open(fname, 'wt') as f:
        logger.info('- Creating {} example configuration'.format(fname))
        f.write("# This is a working example.\n")
        f.write("# For a more complete reference use `--example`\n")
        f.write('kibot:\n  version: 1\n\n')
        # Outputs
        outs = RegOutput.get_registered()
        # List of layers
        layers = []
        if GS.pcb_file:
            load_board(GS.pcb_file)
            layers = look_for_used_layers()
        if GS.sch_file:
            load_sch()
        # Filter some warnings
        fil = [{'number': 1007},  # No information for a component in a distributor
               {'number': 1015},  # More than one component in a search for a distributor
               {'number': 58},    # Missing project file
               ]
        glb = {'filters': fil}
        f.write(yaml.dump({'global': glb}, sort_keys=False))
        f.write('\n')
        # A helper for the JLCPCB stuff
        fil = {'name': 'only_jlc_parts'}
        fil['comment'] = 'Only parts with JLC (LCSC) code'
        fil['type'] = 'generic'
        fil['include_only'] = [{'column': 'LCSC#', 'regex': r'^C\d+'}]
        f.write(yaml.dump({'filters': [fil]}, sort_keys=False))
        f.write('\n')
        # A helper for KiCost demo
        var = {'name': 'place_holder'}
        var['comment'] = 'Just a place holder for pre_transform filters'
        var['type'] = 'kicost'
        var['pre_transform'] = ['_kicost_rename', '_rot_footprint']
        f.write(yaml.dump({'variants': [var]}, sort_keys=False))
        f.write('\n')
        # All the outputs
        outputs = []
        for n, cls in OrderedDict(sorted(outs.items())).items():
            o = cls()
            if types and n not in types:
                logger.debug('- {}, not selected (PCB: {} SCH: {})'.format(n, o.is_pcb(), o.is_sch()))
                continue
            if ((not(o.is_pcb() and GS.pcb_file) and not(o.is_sch() and GS.sch_file)) or
               ((o.is_pcb() and o.is_sch()) and (not GS.pcb_file or not GS.sch_file))):
                logger.debug('- {}, skipped (PCB: {} SCH: {})'.format(n, o.is_pcb(), o.is_sch()))
                continue
            # Look for templates
            tpls = glob(os.path.join(os.path.dirname(__file__), 'config_templates', n, '*.kibot.yaml'))
            if tpls:
                # Load the templates
                tpl_names = tpls
                tpls = [yaml.safe_load(open(t))['outputs'] for t in tpls]
            tree = cls.get_conf_examples(n, layers, tpls)
            if tree:
                logger.debug('- {}, generated'.format(n))
                if tpls:
                    logger.debug(' - Templates: {}'.format(tpl_names))
                outputs.extend(tree)
            else:
                logger.debug('- {}, nothing to do'.format(n))
        if outputs:
            f.write(yaml.dump({'outputs': outputs}, sort_keys=False))
        else:
            return None
    return fname


def generate_targets(config_file):
    """ Generate all possible targets for the configuration file """
    # Reset the board and schematic
    GS.board = None
    GS.sch = None
    # Reset the list of outputs
    RegOutput.reset()
    # Read the config file
    cr = CfgYamlReader()
    with open(config_file) as cf_file:
        outputs = cr.read(cf_file)
    # Do all the job
    generate_outputs(outputs, [], False, None, False, dont_stop=True)


def _walk(path, depth):
    """ Recursively list files and directories up to a certain depth """
    depth -= 1
    with os.scandir(path) as p:
        for entry in p:
            yield entry.path
            if entry.is_dir() and depth > 0:
                yield from _walk(entry.path, depth)


def generate_examples(start_dir, dry, types):
    if not start_dir:
        start_dir = '.'
    else:
        if not os.path.isdir(start_dir):
            logger.error('Invalid dir {} to quick start'.format(start_dir))
            exit(WRONG_ARGUMENTS)
    # Set default global options
    glb = GS.class_for_global_opts()
    glb.set_tree({})
    glb.config(None)
    # Look for candidate dirs
    k_files_regex = re.compile(r'([^/]+)\.(kicad_pcb|kicad_sch|sch)$')
    candidates = set()
    for f in _walk(start_dir, 6):
        if k_files_regex.search(f):
            candidates.add(os.path.dirname(f))
    # Try to generate the configs in the candidate places
    confs = []
    for c in sorted(candidates):
        logger.info('Analyzing `{}` dir'.format(c))
        res = generate_one_example(c, types)
        if res:
            confs.append(res)
        logger.info('')
    confs.sort()
    # Just the configs, not the targets
    if dry:
        return
    # Try to generate all the stuff
    if GS.out_dir_in_cmd_line:
        out_dir = GS.out_dir
    else:
        out_dir = 'Generated'
    for n, c in enumerate(confs):
        conf_dir = os.path.dirname(c)
        if len(confs) > 1:
            subdir = '%03d-%s' % (n+1, conf_dir.replace('/', ',').replace(' ', '_'))
            dest = os.path.join(out_dir, subdir)
        else:
            dest = out_dir
        GS.out_dir = dest
        logger.info('Generating targets for `{}`, destination: `{}`'.format(c, dest))
        os.makedirs(dest, exist_ok=True)
        # Create a log file with all the debug we can
        fl = log.set_file_log(os.path.join(dest, 'kibot.log'))
        old_lvl = GS.debug_level
        GS.debug_level = 10
        # Detect the SCH and PCB again
        discover_files(conf_dir)
        # Generate all targets
        generate_targets(c)
        # Close the debug file
        log.remove_file_log(fl)
        GS.debug_level = old_lvl
        logger.info('')


# To avoid circular dependencies: Optionable needs it, but almost everything needs Optionable
GS.load_board = load_board
GS.load_sch = load_sch
