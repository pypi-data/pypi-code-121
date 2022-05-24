# -*- coding: utf-8 -*-
# Copyright (c) 2021-2022 Salvador E. Tropea
# Copyright (c) 2021-2022 Instituto Nacional de Tecnología Industrial
# License: GPL-3.0
# Project: KiBot (formerly KiPlot)
# KiCad 6 bug: https://gitlab.com/kicad/code/kicad/-/issues/9890
import os
from shutil import rmtree
from .misc import (CMD_PCBNEW_3D, URL_PCBNEW_3D, RENDER_3D_ERR, PCB_MAT_COLORS, PCB_FINISH_COLORS, SOLDER_COLORS, SILK_COLORS,
                   KICAD_VERSION_6_0_2, MISSING_TOOL, kiauto_dependency)
from .gs import (GS)
from .kiplot import check_script, exec_with_retry, add_extra_options
from .out_base_3d import Base3DOptions, Base3D
from .registrable import RegDependency
from .macros import macros, document, output_class  # noqa: F401
from . import log

logger = log.get_logger()
RegDependency.register(kiauto_dependency('render_3d', (1, 6, 8)))


class Render3DOptions(Base3DOptions):
    _colors = {'background1': 'bg_color_1',
               'background2': 'bg_color_2',
               'copper': 'copper_color',
               'board': 'board_color',
               'silk': 'silk_color',
               'solder_mask': 'sm_color',
               'solder_paste': 'sp_color'}
    _views = {'top': 'z', 'bottom': 'Z', 'front': 'y', 'rear': 'Y', 'right': 'x', 'left': 'X'}
    _rviews = {v: k for k, v in _views.items()}

    def __init__(self):
        with document:
            self.output = GS.def_global_output
            """ Name for the generated image file (%i='3D_$VIEW' %x='png') """
            self.no_tht = False
            """ Used to exclude 3D models for through hole components """
            self.no_smd = False
            """ Used to exclude 3D models for surface mount components """
            self.background1 = "#66667F"
            """ First color for the background gradient """
            self.background2 = "#CCCCE5"
            """ Second color for the background gradient """
            self.board = "#332B16"
            """ Color for the board without copper or solder mask """
            self.copper = "#8b898c"
            """ Color for the copper """
            self.silk = "#d5dce4"
            """ Color for the silk screen """
            self.solder_mask = "#208b47"
            """ Color for the solder mask """
            self.solder_paste = "#808080"
            """ Color for the solder paste """
            self.move_x = 0
            """ Steps to move in the X axis, positive is to the right.
                Just like pressing the right arrow in the 3D viewer """
            self.move_y = 0
            """ Steps to move in the Y axis, positive is up.
                Just like pressing the up arrow in the 3D viewer """
            self.rotate_x = 0
            """ Steps to rotate around the X axis, positive is clockwise.
                Each step is currently 10 degrees. Only for KiCad 6 """
            self.rotate_y = 0
            """ Steps to rotate around the Y axis, positive is clockwise.
                Each step is currently 10 degrees. Only for KiCad 6 """
            self.rotate_z = 0
            """ Steps to rotate around the Z axis, positive is clockwise.
                Each step is currently 10 degrees. Only for KiCad 6 """
            self.ray_tracing = False
            """ Enable the ray tracing. Much better result, but slow, and you'll need to adjust `wait_rt` """
            self.wait_ray_tracing = -600
            """ How many seconds we must wait before capturing the ray tracing render.
                Lamentably KiCad can save an unfinished image. Enlarge it if your image looks partially rendered.
                Use negative values to enable the auto-detect using CPU load.
                In this case the value is interpreted as a time-out. """
            self.view = 'top'
            """ [top,bottom,front,rear,right,left,z,Z,y,Y,x,X] Point of view """
            self.zoom = 0
            """ Zoom steps. Use positive to enlarge, get closer, and negative to reduce.
                Same result as using the mouse wheel in the 3D viewer """
            self.width = 1280
            """ Image width (aprox.) """
            self.height = 720
            """ Image height (aprox.) """
            self.orthographic = False
            """ Enable the orthographic projection mode (top view looks flat) """
        super().__init__()
        self._expand_ext = 'png'

    def config(self, parent):
        # Apply global defaults
        if GS.global_pcb_material is not None:
            material = GS.global_pcb_material.lower()
            for mat, color in PCB_MAT_COLORS.items():
                if mat in material:
                    self.board = "#"+color
                    break
        # Pre parse the view option
        bottom = False
        if 'view' in self._tree:
            v = self._tree['view']
            bottom = isinstance(v, str) and v == 'bottom'
        # Solder mask
        if bottom:
            name = GS.global_solder_mask_color_bottom or GS.global_solder_mask_color
        else:
            name = GS.global_solder_mask_color_top or GS.global_solder_mask_color
        if name and name.lower() in SOLDER_COLORS:
            (_, self.solder_mask) = SOLDER_COLORS[name.lower()]
            # Add the default opacity (80%)
            self.solder_mask += "D4"
        # Silk screen
        if bottom:
            name = GS.global_silk_screen_color_bottom or GS.global_silk_screen_color
        else:
            name = GS.global_silk_screen_color_top or GS.global_silk_screen_color
        if name and name.lower() in SILK_COLORS:
            self.silk = "#"+SILK_COLORS[name.lower()]
        # PCB finish
        if GS.global_pcb_finish is not None:
            name = GS.global_pcb_finish.lower()
            for nm, color in PCB_FINISH_COLORS.items():
                if nm in name:
                    self.copper = "#"+color
                    break
        super().config(parent)
        self.validate_colors(self._colors.keys())
        view = self._views.get(self.view, None)
        if view is not None:
            self.view = view
        self._expand_id += '_'+self._rviews.get(self.view)

    def add_step(self, cmd, steps, ops):
        if steps:
            cmd.extend([ops, str(steps)])

    def run(self, output):
        super().run(output)
        if GS.ki6() and GS.kicad_version_n < KICAD_VERSION_6_0_2:
            logger.error("3D Viewer not supported for KiCad 6.0.0/1\n"
                         "Please upgrade KiCad to 6.0.2 or newer")
            exit(MISSING_TOOL)
        check_script(CMD_PCBNEW_3D, URL_PCBNEW_3D, '1.6.8')
        # Base command with overwrite
        cmd = [CMD_PCBNEW_3D, '--rec_w', str(self.width+2), '--rec_h', str(self.height+85),
               '3d_view', '--output_name', output]
        # Add user options
        if not self.no_virtual:
            cmd.append('--virtual')
        if self.no_tht:
            cmd.append('--no_tht')
        if self.no_smd:
            cmd.append('--no_smd')
        for color, option in self._colors.items():
            cmd.extend(['--'+option, getattr(self, color)])
        self.add_step(cmd, self.move_x, '--move_x')
        self.add_step(cmd, self.move_y, '--move_y')
        self.add_step(cmd, self.rotate_x, '--rotate_x')
        self.add_step(cmd, self.rotate_y, '--rotate_y')
        self.add_step(cmd, self.rotate_z, '--rotate_z')
        if self.zoom:
            cmd.extend(['--zoom', str(self.zoom)])
        if self.wait_ray_tracing != 5:
            if self.wait_ray_tracing < 0:
                self.wait_ray_tracing = -self.wait_ray_tracing
                cmd.append('--detect_rt')
            cmd.extend(['--wait_rt', str(self.wait_ray_tracing)])
        if self.ray_tracing:
            cmd.append('--ray_tracing')
        if self.orthographic:
            cmd.append('--orthographic')
        if self.view != 'z':
            cmd.extend(['--view', self.view])
        # The board
        board_name = self.filter_components()
        cmd.extend([board_name, os.path.dirname(output)])
        cmd, video_remove = add_extra_options(cmd)
        # Execute it
        ret = exec_with_retry(cmd)
        # Remove the temporal PCB
        self.remove_tmp_board(board_name)
        # Remove the downloaded 3D models
        if self._tmp_dir:
            rmtree(self._tmp_dir)
        if ret:
            logger.error(CMD_PCBNEW_3D+' returned %d', ret)
            exit(RENDER_3D_ERR)
        if video_remove:
            video_name = os.path.join(self.expand_filename_pcb(GS.out_dir), 'pcbnew_3d_view_screencast.ogv')
            if os.path.isfile(video_name):
                os.remove(video_name)


@output_class
class Render_3D(Base3D):  # noqa: F821
    """ 3D render of the PCB
        Exports the image generated by KiCad's 3D viewer. """
    def __init__(self):
        super().__init__()
        with document:
            self.options = Render3DOptions
            """ [dict] Options for the `render_3d` output """

    @staticmethod
    def get_conf_examples(name, layers, templates):
        outs = []
        has_top = False
        has_bottom = False
        for la in layers:
            if la.is_top() or la.layer.startswith('F.'):
                has_top = True
            elif la.is_bottom() or la.layer.startswith('B.'):
                has_bottom = True
        if has_top:
            gb = {}
            gb['name'] = 'basic_{}_top'.format(name)
            gb['comment'] = '3D view from top'
            gb['type'] = name
            gb['dir'] = '3D'
            gb['options'] = {'ray_tracing': True, 'orthographic': True}
            outs.append(gb)
            if GS.ki6():
                gb = {}
                gb['name'] = 'basic_{}_30deg'.format(name)
                gb['comment'] = '3D view from 30 degrees'
                gb['type'] = name
                gb['dir'] = '3D'
                gb['output_id'] = '30deg'
                gb['options'] = {'ray_tracing': True, 'rotate_x': 3, 'rotate_z': -2}
                outs.append(gb)
        if has_bottom:
            gb = {}
            gb['name'] = 'basic_{}_bottom'.format(name)
            gb['comment'] = '3D view from bottom'
            gb['type'] = name
            gb['dir'] = '3D'
            gb['options'] = {'ray_tracing': True, 'orthographic': True, 'view': 'bottom'}
            outs.append(gb)
        return outs
