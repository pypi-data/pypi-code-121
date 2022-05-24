# -*- coding: utf-8 -*-
# Copyright (c) 2022 Salvador E. Tropea
# Copyright (c) 2022 Instituto Nacional de Tecnología Industrial
# License: GPL-3.0
# Project: KiBot (formerly KiPlot)
import os
import re
import pcbnew
from subprocess import check_output, STDOUT, CalledProcessError
from shutil import which

from .gs import GS
from .misc import (UI_SMD, UI_VIRTUAL, MOD_THROUGH_HOLE, MOD_SMD, MOD_EXCLUDE_FROM_POS_FILES, PANDOC, MISSING_TOOL,
                   FAILED_EXECUTE, W_WRONGEXT, W_WRONGOAR, W_ECCLASST, W_MISSTOOL, ToolDependency, ToolDependencyRole,
                   TRY_INSTALL_CHECK)
from .registrable import RegOutput, RegDependency
from .out_base import BaseOptions
from .error import KiPlotConfigurationError
from .kiplot import config_output
from .macros import macros, document, output_class  # noqa: F401
from . import log

logger = log.get_logger()
INF = float('inf')
PANDOC_INSTALL = ("In CI/CD environments: the `kicad_auto_test` docker image contains it.\n"
                  "In Debian/Ubuntu environments: install `pandoc`, `texlive-latex-base` and `texlive-latex-recommended`")
RegDependency.register(ToolDependency('report', 'Pandoc', 'https://pandoc.org/',
                                      url_down='https://github.com/jgm/pandoc/releases',
                                      extra_deb=['texlive-latex-base', 'texlive-latex-recommended'],
                                      roles=ToolDependencyRole(desc='Create PDF/ODF/DOCX files')))


def do_round(v, dig):
    v = round(v+1e-9, dig)
    return v if dig else int(v)


def to_mm(iu, dig=2):
    """ KiCad Internal Units to millimeters """
    if isinstance(iu, pcbnew.wxPoint):
        return (do_round(iu.x/pcbnew.IU_PER_MM, dig), do_round(iu.y/pcbnew.IU_PER_MM, dig))
    if isinstance(iu, pcbnew.wxSize):
        return (do_round(iu.x/pcbnew.IU_PER_MM, dig), do_round(iu.y/pcbnew.IU_PER_MM, dig))
    return do_round(iu/pcbnew.IU_PER_MM, dig)


def to_mils(iu, dig=0):
    """ KiCad Internal Units to mils (1/1000 inch) """
    return do_round(iu/pcbnew.IU_PER_MILS, dig)


def to_inches(iu, dig=2):
    """ KiCad Internal Units to inches """
    return do_round(iu/(pcbnew.IU_PER_MILS*1000), dig)


def get_class_index(val, lst):
    """ Used to search in an Eurocircuits class vector.
        Returns the first match that is >= to val. """
    val = to_mm(val, 3)
    for c, v in enumerate(lst):
        if val >= v:
            return c
    return c+1


def get_pattern_class(track, clearance, oar, case, target=None):
    """ Returns the Eurocircuits Pattern class for a track width, clearance and OAR """
    c1 = (0.25, 0.2, 0.175, 0.150, 0.125, 0.1, 0.09)
    c2 = (0.2, 0.15, 0.15, 0.125, 0.125, 0.1, 0.1)
    ct = get_class_index(track, c1)
    cc = get_class_index(clearance, c1)
    co = get_class_index(oar, c2)
    cf = max(ct, max(cc, co))+3
    if target is not None and cf > target:
        if ct+3 > target:
            logger.warning(W_ECCLASST+"Track too narrow {} mm, should be ≥ {} mm".format(to_mm(track), c1[target-3]))
        if cc+3 > target:
            logger.warning(W_ECCLASST+"Clearance too small {} mm, should be ≥ {} mm".
                           format(to_mm(clearance), c1[target-3]))
        if co+3 > target:
            logger.warning(W_ECCLASST+"OAR too small {} mm, should be ≥ {} mm".format(to_mm(oar), c2[target-3]))
    logger.debug('Eurocircuits Pattern class for `{}` is {} because the clearance is {}, track is {} and OAR is {}'.
                 format(case, cf, to_mm(clearance), to_mm(track), to_mm(oar)))
    return cf


def get_drill_class(drill, case, target=None):
    """ Returns the Eurocircuits Drill class for a drill size.
        This is the real (tool) size. """
    c3 = (0.6, 0.45, 0.35, 0.25, 0.2)
    cd = get_class_index(drill, c3)
    res = chr(ord('A') + cd)
    if target is not None and cd > target:
        logger.warning(W_ECCLASST+"Drill too small {} mm, should be ≥ {} mm".format(to_mm(drill), c3[target]))
    logger.debug('Eurocircuits Drill class for `{}` is {} because the drill is {}'.format(case, res, to_mm(drill)))
    return res


def to_top_bottom(front, bottom):
    """ Returns a text indicating if the feature is in top/bottom layers """
    if front and bottom:
        return "TOP / BOTTOM"
    elif front:
        return "TOP"
    elif bottom:
        return "BOTTOM"
    return "NONE"


def to_smd_tht(smd, tht):
    """ Returns a text indicating if the components are SMD/THT """
    if smd and tht:
        return "SMD + THT"
    elif smd:
        return "SMD"
    elif tht:
        return "THT"
    return "NONE"


def to_top_bottom_color(front, bottom):
    """ Returns a text indicating the top/bottom colors """
    f = front.strip().lower()
    b = bottom.strip().lower()
    if f == b:
        return front.capitalize()
    return "Top: "+front.capitalize()+" / Bottom: "+bottom.capitalize()


def solve_edge_connector(val):
    if val == 'no':
        return ''
    if val == 'bevelled':
        return 'yes, bevelled'
    return val


def get_pad_info(pad):
    return ("Position {} on layer {}, size {} drill size {}".
            format(to_mm(pad.GetPosition()), GS.board.GetLayerName(pad.GetLayer()),
                   to_mm(pad.GetSize(), 4), to_mm(pad.GetDrillSize(), 4)))


def adjust_drill(val, is_pth=True, pad=None):
    """ Add drill_size_increment if this is a PTH hole and round it to global_extra_pth_drill """
    if val == INF:
        return val
    step = GS.global_drill_size_increment*pcbnew.IU_PER_MM
    if is_pth:
        val += GS.global_extra_pth_drill*pcbnew.IU_PER_MM
    res = int((val+step/2)/step)*step
    # if pad:
    #     logger.error(f"{to_mm(val)} -> {to_mm(res)} {get_pad_info(pad)}")
    # else:
    #     logger.error(f"{to_mm(val)} -> {to_mm(res)}")
    return res


class ReportOptions(BaseOptions):
    def __init__(self):
        with document:
            self.output = GS.def_global_output
            """ Output file name (%i='report', %x='txt') """
            self.template = 'full'
            """ Name for one of the internal templates (full, full_svg, simple) or a custom template file.
                Note: when converting to PDF PanDoc can fail on some Unicode values (use `simple_ASCII`) """
            self.convert_from = 'markdown'
            """ Original format for the report conversion. Current templates are `markdown`. See `do_convert` """
            self.convert_to = 'pdf'
            """ Target format for the report conversion. See `do_convert` """
            self.do_convert = False
            """ Run `Pandoc` to convert the report. Note that Pandoc must be installed.
                The conversion is done assuming the report is in `convert_from` format.
                The output file will be in `convert_to` format.
                The available formats depends on the `Pandoc` installation """
            self.converted_output = GS.def_global_output
            """ Converted output file name (%i='report', %x=`convert_to`).
                Note that the extension should match the `convert_to` value """
            self.eurocircuits_class_target = '10F'
            """ Which Eurocircuits class are we aiming at """
        super().__init__()
        self._expand_id = 'report'
        self._expand_ext = 'txt'
        self._mm_digits = 2
        self._mils_digits = 0
        self._in_digits = 2
        self._help_do_convert += ".\n"+PANDOC_INSTALL

    def config(self, parent):
        super().config(parent)
        self.to_ascii = False
        if self.template.endswith('_ASCII'):
            self.template = self.template[:-6]
            self.to_ascii = True
        if self.template.lower() in ('full', 'simple', 'full_svg'):
            self.template = os.path.abspath(os.path.join(os.path.dirname(__file__), 'report_templates',
                                            'report_'+self.template.lower()+'.txt'))
        if not os.path.isfile(self.template):
            raise KiPlotConfigurationError("Missing report template: `{}`".format(self.template))
        m = re.match(r'(\d+)([A-F])', self.eurocircuits_class_target)
        if not m:
            raise KiPlotConfigurationError("Malformed Eurocircuits class, must be a number and a letter (<=10F)")
        self._ec_pat = int(m.group(1))
        if self._ec_pat < 3 or self._ec_pat > 10:
            raise KiPlotConfigurationError("Eurocircuits Pattern class out of range [3,10]")
        self._ec_drl = ord(m.group(2))-ord('A')

    def do_replacements(self, line, defined):
        """ Replace ${VAR} patterns """
        for var in re.findall(r'\$\{([^\s\}]+)\}', line):
            if var[0] == '_':
                # Prevent access to internal data
                continue
            units = None
            var_ori = var
            m = re.match(r'^(%[^,]+),(.*)$', var)
            pattern = None
            if m:
                pattern = m.group(1)
                var = m.group(2)
            if var.endswith('_mm'):
                units = to_mm
                digits = self._mm_digits
                var = var[:-3]
            elif var.endswith('_in'):
                units = to_inches
                digits = self._in_digits
                var = var[:-3]
            elif var.endswith('_mils'):
                units = to_mils
                digits = self._mils_digits
                var = var[:-5]
            if var in defined:
                val = defined[var]
                if val == INF:
                    val = 'N/A'
                elif units is not None and isinstance(val, (int, float)):
                    val = units(val, digits)
                if pattern is not None:
                    clear = False
                    if 's' in pattern:
                        val = str(val)
                    else:
                        try:
                            val = float(val)
                        except ValueError:
                            val = 0
                            clear = True
                    rep = pattern % val
                    if clear:
                        rep = ' '*len(rep)
                else:
                    rep = str(val)
                line = line.replace('${'+var_ori+'}', rep)
            else:
                print('Error: Unable to expand `{}`'.format(var))
        return line

    def context_defined_tracks(self, line):
        """ Replace iterator for the `defined_tracks` context """
        text = ''
        for t in sorted(self._track_sizes):
            if not t:
                continue  # KiCad 6
            text += self.do_replacements(line, {'track': t})
        return text

    def context_used_tracks(self, line):
        """ Replace iterator for the `used_tracks` context """
        text = ''
        for t in sorted(self._tracks_m.keys()):
            text += self.do_replacements(line, {'track': t, 'count': self._tracks_m[t],
                                         'defined': 'yes' if t in self._tracks_defined else 'no'})
        return text

    def context_defined_vias(self, line):
        """ Replace iterator for the `defined_vias` context """
        text = ''
        for v in self._via_sizes_sorted:
            text += self.do_replacements(line, {'pad': v[1], 'drill': v[0]})
        return text

    def context_used_vias(self, line):
        """ Replace iterator for the `used_vias` context """
        text = ''
        if not self._vias_m:
            return text
        for v in self._vias_m:
            d = v[1]
            h = v[0]
            aspect = round(self.thickness/d, 1)
            # IPC-2222 Table 9.4
            producibility_level = 'C'
            if aspect < 9:
                if aspect < 5:
                    producibility_level = 'A'
                else:
                    producibility_level = 'B'
            defined = {'pad': v[1], 'drill': v[0]}
            defined['count'] = self._vias[v]
            defined['aspect'] = aspect
            defined['producibility_level'] = producibility_level
            defined['defined'] = 'yes' if (h, d) in self._vias_defined else 'no'
            text += self.do_replacements(line, defined)
        return text

    def context_hole_sizes_no_vias(self, line):
        """ Replace iterator for the `hole_sizes_no_vias` context """
        text = ''
        for d in sorted(self._drills.keys()):
            text += self.do_replacements(line, {'drill': d, 'count': self._drills[d]})
        return text

    def context_oval_hole_sizes(self, line):
        """ Replace iterator for the `oval_hole_sizes` context """
        text = ''
        for d in sorted(self._drills_oval.keys()):
            text += self.do_replacements(line, {'drill_1': d[0], 'drill_2': d[1], 'count': self._drills_oval[d]})
        return text

    def context_drill_tools(self, line):
        """ Replace iterator for the `drill_tools` context """
        text = ''
        for d in sorted(self._drills_real.keys()):
            text += self.do_replacements(line, {'drill': d, 'count': self._drills_real[d]})
        return text

    def context_stackup(self, line):
        """ Replace iterator for the `stackup` context """
        text = ''
        for s in self._stackup:
            context = {}
            for k in dir(s):
                val = getattr(s, k)
                if k[0] != '_' and not callable(val):
                    context[k] = val if val is not None else ''
            text += self.do_replacements(line, context)
        return text

    def _context_images(self, line, images):
        """ Replace iterator for the various contexts that expands images """
        text = ''
        for s in images:
            context = {'path': s[0], 'comment': s[1], 'new_line': '\n'}
            text += self.do_replacements(line, context)
        return text

    def context_layer_pdfs(self, line):
        """ Replace iterator for the `layer_pdfs` context """
        return self._context_images(line, self._layer_pdfs)

    def context_layer_svgs(self, line):
        """ Replace iterator for the `layer_svgs` context """
        return self._context_images(line, self._layer_svgs)

    def context_schematic_pdfs(self, line):
        """ Replace iterator for the `schematic_pdfs` context """
        return self._context_images(line, self._schematic_pdfs)

    def context_schematic_svgs(self, line):
        """ Replace iterator for the `schematic_svgs` context """
        return self._context_images(line, self._schematic_svgs)

    def _context_individual_images(self, line, images):
        """ Replace iterator for the various contexts that expands one image """
        text = ''
        context = {'new_line': '\n'}
        for s in images:
            context['path_'+s[2]] = s[0]
            context['comment_'+s[2]] = s[1]
        text += self.do_replacements(line, context)
        return text

    def context_layer_pdf(self, line):
        """ Replace iterator for the `layer_pdf` context """
        return self._context_individual_images(line, self._layer_pdfs)

    def context_layer_svg(self, line):
        """ Replace iterator for the `layer_svg` context """
        return self._context_individual_images(line, self._layer_svgs)

    def context_schematic_pdf(self, line):
        """ Replace iterator for the `schematic_pdf` context """
        return self._context_individual_images(line, self._schematic_pdfs)

    def context_schematic_svg(self, line):
        """ Replace iterator for the `schematic_svg` context """
        return self._context_individual_images(line, self._schematic_svgs)

    @staticmethod
    def is_pure_smd_5(m):
        return m.GetAttributes() == UI_SMD

    @staticmethod
    def is_pure_smd_6(m):
        return m.GetAttributes() & (MOD_THROUGH_HOLE | MOD_SMD) == MOD_SMD

    @staticmethod
    def is_not_virtual_5(m):
        return m.GetAttributes() != UI_VIRTUAL

    @staticmethod
    def is_not_virtual_6(m):
        return not (m.GetAttributes() & MOD_EXCLUDE_FROM_POS_FILES)

    def get_attr_tests(self):
        if GS.ki5():
            return self.is_pure_smd_5, self.is_not_virtual_5
        return self.is_pure_smd_6, self.is_not_virtual_6

    def measure_pcb(self, board):
        edge_layer = board.GetLayerID('Edge.Cuts')
        x1 = y1 = x2 = y2 = None
        draw_type = 'DRAWSEGMENT' if GS.ki5() else 'PCB_SHAPE'
        for d in board.GetDrawings():
            if d.GetClass() == draw_type and d.GetLayer() == edge_layer:
                if x1 is None:
                    p = d.GetStart()
                    x1 = x2 = p.x
                    y1 = y2 = p.y
                for p in [d.GetStart(), d.GetEnd()]:
                    x2 = max(x2, p.x)
                    y2 = max(y2, p.y)
                    x1 = min(x1, p.x)
                    y1 = min(y1, p.y)
        # This is a special case: the PCB edges are in a footprint
        for m in GS.get_modules():
            for gi in m.GraphicalItems():
                if gi.GetClass() == 'MGRAPHIC' and gi.GetLayer() == edge_layer:
                    if x1 is None:
                        p = gi.GetStart()
                        x1 = x2 = p.x
                        y1 = y2 = p.y
                    for p in [gi.GetStart(), gi.GetEnd()]:
                        x2 = max(x2, p.x)
                        y2 = max(y2, p.y)
                        x1 = min(x1, p.x)
                        y1 = min(y1, p.y)
        if x1 is None:
            self.bb_w = self.bb_h = INF
        else:
            self.bb_w = x2-x1
            self.bb_h = y2-y1

    def collect_data(self, board):
        ds = board.GetDesignSettings()
        self.extra_pth_drill = GS.global_extra_pth_drill*pcbnew.IU_PER_MM
        ###########################################################
        # Board size
        ###########################################################
        # The value returned by ComputeBoundingBox(True) adds the drawing width!
        bb = board.ComputeBoundingBox(True)
        self.bb_w_d = bb.GetWidth()
        self.bb_h_d = bb.GetHeight()
        self.measure_pcb(board)
        ###########################################################
        # Board thickness
        ###########################################################
        self.thickness = ds.GetBoardThickness()
        ###########################################################
        # Number of layers
        ###########################################################
        self.layers = ds.GetCopperLayerCount()
        ###########################################################
        # Solder mask layers
        ###########################################################
        fmask = board.IsLayerEnabled(board.GetLayerID('F.Mask'))
        bmask = board.IsLayerEnabled(board.GetLayerID('B.Mask'))
        self.solder_mask = to_top_bottom(fmask, bmask)
        ###########################################################
        # Silk screen
        ###########################################################
        fsilk = board.IsLayerEnabled(board.GetLayerID('F.SilkS'))
        bsilk = board.IsLayerEnabled(board.GetLayerID('B.SilkS'))
        self.silk_screen = to_top_bottom(fsilk, bsilk)
        ###########################################################
        # Clearance
        ###########################################################
        self.clearance = ds.GetSmallestClearanceValue()
        # This seems to be bogus:
        # h2h = ds.m_HoleToHoleMin
        ###########################################################
        # Track width (min)
        ###########################################################
        self.track_d = ds.m_TrackMinWidth
        tracks = board.GetTracks()
        self.oar_vias = self.track = INF
        self._vias = {}
        self._tracks_m = {}
        self._drills_real = {}
        track_type = 'TRACK' if GS.ki5() else 'PCB_TRACK'
        via_type = 'VIA' if GS.ki5() else 'PCB_VIA'
        for t in tracks:
            tclass = t.GetClass()
            if tclass == track_type:
                w = t.GetWidth()
                self.track = min(w, self.track)
                self._tracks_m[w] = self._tracks_m.get(w, 0) + 1
            elif tclass == via_type:
                via = t.Cast()
                via_id = (via.GetDrill(), via.GetWidth())
                self._vias[via_id] = self._vias.get(via_id, 0) + 1
                d = adjust_drill(via_id[0])
                self.oar_vias = min(self.oar_vias, via_id[1] - d)
                self._drills_real[d] = self._drills_real.get(d, 0) + 1
        self.track_min = min(self.track_d, self.track)
        ###########################################################
        # Drill (min)
        ###########################################################
        modules = board.GetModules() if GS.ki5() else board.GetFootprints()
        self._drills = {}
        self._drills_oval = {}
        self.oar_pads = self.pad_drill = self.pad_drill_real = INF
        self.slot = INF
        self.top_smd = self.top_tht = self.bot_smd = self.bot_tht = 0
        top_layer = board.GetLayerID('F.Cu')
        bottom_layer = board.GetLayerID('B.Cu')
        is_pure_smd, is_not_virtual = self.get_attr_tests()
        npth_attrib = 3 if GS.ki5() else pcbnew.PAD_ATTRIB_NPTH
        min_oar = 0.1*pcbnew.IU_PER_MM
        for m in modules:
            layer = m.GetLayer()
            if layer == top_layer:
                if is_pure_smd(m):
                    self.top_smd += 1
                elif is_not_virtual(m):
                    self.top_tht += 1
            elif layer == bottom_layer:
                if is_pure_smd(m):
                    self.bot_smd += 1
                elif is_not_virtual(m):
                    self.bot_tht += 1
            pads = m.Pads()
            for pad in pads:
                dr = pad.GetDrillSize()
                if not dr.x:
                    continue
                self.pad_drill = min(dr.x, self.pad_drill)
                self.pad_drill = min(dr.y, self.pad_drill)
                # Compute the drill size to get it after plating
                is_pth = pad.GetAttribute() != npth_attrib
                dr_x_real = adjust_drill(dr.x, is_pth, pad)
                dr_y_real = adjust_drill(dr.y, is_pth, pad)
                self.pad_drill_real = min(dr_x_real, self.pad_drill_real)
                self.pad_drill_real = min(dr_y_real, self.pad_drill_real)
                if dr.x == dr.y:
                    self._drills[dr.x] = self._drills.get(dr.x, 0) + 1
                    self._drills_real[dr_x_real] = self._drills_real.get(dr_x_real, 0) + 1
                else:
                    if dr.x < dr.y:
                        m = (dr.x, dr.y)
                        d = dr.x
                        d_r = dr_x_real
                    else:
                        m = (dr.y, dr.x)
                        d = dr.y
                        d_r = dr_y_real
                    self._drills_oval[m] = self._drills_oval.get(m, 0) + 1
                    self.slot = min(self.slot, m[0])
                    # print('{} @ {}'.format(dr, pad.GetPosition()))
                    self._drills_real[d_r] = self._drills_real.get(d_r, 0) + 1
                pad_sz = pad.GetSize()
                oar_x = pad_sz.x - dr_x_real
                oar_y = pad_sz.y - dr_y_real
                oar_t = min(oar_x, oar_y)
                if oar_t > 0:
                    self.oar_pads = min(self.oar_pads, oar_t)
                    if oar_t < min_oar:
                        logger.warning(W_WRONGOAR+"Really small OAR detected ({} mm) for pad {}".
                                       format(to_mm(oar_t, 4), get_pad_info(pad)))
                elif oar_t < 0:
                    logger.warning(W_WRONGOAR+"Negative OAR detected for pad "+get_pad_info(pad))
                elif oar_t == 0 and is_pth:
                    logger.warning(W_WRONGOAR+"Plated pad without copper "+get_pad_info(pad))
        self._vias_m = sorted(self._vias.keys())
        # Via Pad size
        self.via_pad_d = ds.m_ViasMinSize
        self.via_pad = self._vias_m[0][1] if self._vias_m else INF
        self.via_pad_min = min(self.via_pad_d, self.via_pad)
        # Via Drill size
        self._vias_m = sorted(self._vias.keys())
        self.via_drill_d = ds.m_ViasMinDrill if GS.ki5() else ds.m_MinThroughDrill
        self.via_drill = self._vias_m[0][0] if self._vias_m else INF
        self.via_drill_min = min(self.via_drill_d, self.via_drill)
        # Via Drill size before platting
        self.via_drill_real_d = adjust_drill(self.via_drill_d)
        self.via_drill_real = adjust_drill(self.via_drill)
        self.via_drill_real_min = adjust_drill(self.via_drill_min)
        # Pad Drill
        # No minimum defined (so no _d)
        self.pad_drill_min = self.pad_drill if GS.ki5() else ds.m_MinThroughDrill
        self.pad_drill_real_min = self.pad_drill_real if GS.ki5() else adjust_drill(ds.m_MinThroughDrill, False)
        # Drill overall
        self.drill_d = min(self.via_drill_d, self.pad_drill)
        self.drill = min(self.via_drill, self.pad_drill)
        self.drill_min = min(self.via_drill_min, self.pad_drill_min)
        # Drill overall size minus 0.1 mm
        self.drill_real_d = min(self.via_drill_real_d, self.pad_drill_real)
        self.drill_real = min(self.via_drill_real, self.pad_drill_real)
        self.drill_real_min = min(self.via_drill_real_min, self.pad_drill_real_min)
        self.top_comp_type = to_smd_tht(self.top_smd, self.top_tht)
        self.bot_comp_type = to_smd_tht(self.bot_smd, self.bot_tht)
        ###########################################################
        # Vias
        ###########################################################
        self.micro_vias = 'yes' if ds.m_MicroViasAllowed else 'no'
        self.blind_vias = 'yes' if ds.m_BlindBuriedViaAllowed else 'no'
        self.uvia_pad = ds.m_MicroViasMinSize
        self.uvia_drill = ds.m_MicroViasMinDrill
        via_sizes = board.GetViasDimensionsList()
        self._vias_defined = set()
        self._via_sizes_sorted = []
        self.oar_vias_d = INF
        for v in sorted(via_sizes, key=lambda x: (x.m_Diameter, x.m_Drill)):
            d = v.m_Diameter
            h = v.m_Drill
            if not d and not h:
                continue  # KiCad 6
            self.oar_vias_d = min(self.oar_vias_d, d - adjust_drill(h))
            self._vias_defined.add((h, d))
            self._via_sizes_sorted.append((h, d))
        ###########################################################
        # Outer Annular Ring
        ###########################################################
        self.oar_pads_min = self.oar_pads
        self.oar_d = min(self.oar_vias_d, self.oar_pads)
        self.oar = min(self.oar_vias, self.oar_pads)
        self.oar_min = min(self.oar_d, self.oar)
        self.oar_vias_min = min(self.oar_vias_d, self.oar_vias)
        ###########################################################
        # Eurocircuits class
        # https://www.eurocircuits.com/pcb-design-guidelines-classification/
        ###########################################################
        # Pattern class
        self.pattern_class_min = get_pattern_class(self.track_min, self.clearance, self.oar_min, 'minimum')
        self.pattern_class = get_pattern_class(self.track, self.clearance, self.oar, 'measured', self._ec_pat)
        self.pattern_class_d = get_pattern_class(self.track_d, self.clearance, self.oar_d, 'defined')
        # Drill class
        self.drill_class_min = get_drill_class(self.drill_real_min, 'minimum')
        self.drill_class = get_drill_class(self.drill_real, 'measured', self._ec_drl)
        self.drill_class_d = get_drill_class(self.drill_real_d, 'defined')
        ###########################################################
        # General stats
        ###########################################################
        self._track_sizes = board.GetTrackWidthList()
        self._tracks_defined = set(self._track_sizes)

    def eval_conditional(self, line):
        context = {k: getattr(self, k) for k in dir(self) if k[0] != '_' and not callable(getattr(self, k))}
        res = None
        text = line[2:].strip()
        logger.debug('- Evaluating `{}`'.format(text))
        try:
            res = eval(text, {}, context)
        except Exception as e:
            raise KiPlotConfigurationError('wrong conditional: `{}`\nPython says: `{}`'.format(text, str(e)))
        logger.debug('- Result `{}`'.format(res))
        return res

    def do_template(self, template_file, output_file):
        text = ''
        logger.debug("Report template: `{}`".format(template_file))
        with open(template_file, "rt") as f:
            skip_next = False
            for line in f:
                if skip_next:
                    skip_next = False
                    continue
                done = False
                if line[0] == '#':
                    if line.startswith('#?'):
                        skip_next = not self.eval_conditional(line)
                        done = True
                        line = ''
                    elif ':' in line:
                        context = line[1:].split(':')[0]
                        logger.debug("- Report context: `{}`".format(context))
                        name = 'context_'+context
                        if hasattr(self, name):
                            # Contexts are members called context_*
                            line = getattr(self, name)(line[len(context)+2:])
                            done = True
                        else:
                            raise KiPlotConfigurationError("Unknown context: `{}`".format(context))
                if not done:
                    # Just replace using any data member (_* excluded)
                    line = self.do_replacements(line, self.__dict__)
                text += line
        logger.debug("Report output: `{}`".format(output_file))
        if self.to_ascii:
            # PanDoc has problems with this Unicode
            text = text.replace('≥', '>=')
        with open(output_file, "wt") as f:
            f.write(text)

    def expand_converted_output(self, out_dir):
        aux = self._expand_ext
        self._expand_ext = str(self.convert_to)
        res = self._parent.expand_filename(out_dir, self.converted_output)
        self._expand_ext = aux
        return res

    def get_targets(self, out_dir):
        files = [self._parent.expand_filename(out_dir, self.output)]
        if self.do_convert:
            files.append(self.expand_converted_output(out_dir))
        return files

    def convert(self, fname):
        if not self.do_convert:
            return
        out = self.expand_converted_output(GS.out_dir)
        logger.debug('Converting the report to: {}'.format(out))
        resources = '--resource-path='+GS.out_dir
        # Pandoc 2.2.1 doesn't support "--to pdf"
        if not out.endswith('.'+self.convert_to):
            logger.warning(W_WRONGEXT+'The conversion tool detects the output format using the extension')
        cmd = [PANDOC, '--from', self.convert_from, resources, fname, '-o', out]
        logger.debug('Executing {}'.format(cmd))
        try:
            check_output(cmd, stderr=STDOUT)
        except FileNotFoundError:
            logger.error("Unable to convert the report, `{}` must be installed.".format(PANDOC))
            logger.error(PANDOC_INSTALL)
            logger.error(TRY_INSTALL_CHECK)
            exit(MISSING_TOOL)
        except CalledProcessError as e:
            logger.error('{} error: {}'.format(PANDOC, e.returncode))
            if e.output:
                logger.debug('Output from command: '+e.output.decode())
            exit(FAILED_EXECUTE)

    def run(self, fname):
        self.pcb_material = GS.global_pcb_material
        self.solder_mask_color = GS.global_solder_mask_color
        self.solder_mask_color_top = GS.global_solder_mask_color_top
        self.solder_mask_color_bottom = GS.global_solder_mask_color_bottom
        self.solder_mask_color_text = to_top_bottom_color(GS.global_solder_mask_color_top, GS.global_solder_mask_color_bottom)
        self.silk_screen_color = GS.global_silk_screen_color
        self.silk_screen_color_top = GS.global_silk_screen_color_top
        self.silk_screen_color_bottom = GS.global_silk_screen_color_bottom
        self.silk_screen_color_text = to_top_bottom_color(GS.global_silk_screen_color_top, GS.global_silk_screen_color_bottom)
        self.pcb_finish = GS.global_pcb_finish
        self.edge_connector = solve_edge_connector(GS.global_edge_connector)
        self.castellated_pads = GS.global_castellated_pads
        self.edge_plating = GS.global_edge_plating
        self.copper_thickness = GS.global_copper_thickness
        self.impedance_controlled = GS.global_impedance_controlled
        self.stackup = 'yes' if GS.stackup else ''
        self._stackup = GS.stackup if GS.stackup else []
        self.collect_data(GS.board)
        base_dir = os.path.dirname(fname)
        # Collect the PCB layers and schematic prints
        self._layer_pdfs = []
        self._layer_svgs = []
        self._schematic_pdfs = []
        self._schematic_svgs = []
        for o in RegOutput.get_outputs():
            dest = None
            if o.type == 'pdf_pcb_print' or o.type == 'pcb_print':
                dest = self._layer_pdfs
            elif o.type == 'svg_pcb_print':
                dest = self._layer_svgs
            elif o.type == 'pdf_sch_print':
                dest = self._schematic_pdfs
            elif o.type == 'svg_sch_print':
                dest = self._schematic_svgs
            if dest is not None:
                if not o._configured:
                    config_output(o)
                if o.type == 'pcb_print' and o.options.format != 'PDF':
                    if o.options.format == 'SVG':
                        dest = self._layer_svgs
                    else:
                        continue
                out_files = o.get_targets(o.expand_dirname(os.path.join(GS.out_dir, o.dir)))
                is_pcb_print_svg = o.type == 'pcb_print' and o.options.format == 'SVG'
                for n, of in enumerate(out_files):
                    rel_path = os.path.relpath(of, base_dir)
                    comment = o.comment
                    if is_pcb_print_svg and o.options.pages[n].sheet:
                        comment += ' '+o.options.pages[n].sheet
                    dest.append((rel_path, comment, o.name))
        self.layer_pdfs = len(self._layer_pdfs) > 0
        self.layer_svgs = len(self._layer_svgs) > 0
        self.schematic_pdfs = len(self._schematic_pdfs) > 0
        self.schematic_svgs = len(self._schematic_svgs) > 0
        self.do_template(self.template, fname)
        self.convert(fname)


@output_class
class Report(BaseOutput):  # noqa: F821
    """ Design report
        Generates a report about the design.
        Mainly oriented to be sent to the manufacturer or check PCB details. """
    def __init__(self):
        super().__init__()
        with document:
            self.options = ReportOptions
            """ [dict] Options for the `report` output """

    @staticmethod
    def get_conf_examples(name, layers, templates):
        if which(PANDOC) is None:
            logger.warning((W_MISSTOOL+'Missing {} tool, disabling report in PDF format\n'+PANDOC_INSTALL).format(PANDOC))
            logger.warning(W_MISSTOOL+TRY_INSTALL_CHECK)
            pandoc = False
        else:
            pandoc = True
        gb = {}
        outs = [gb]
        gb['name'] = 'report_simple'
        gb['comment'] = 'Simple design report'
        gb['type'] = name
        gb['output_id'] = '_simple'
        gb['options'] = {'template': 'simple_ASCII'}
        if pandoc:
            gb['options']['do_convert'] = True
        gb = {}
        gb['name'] = 'report_full'
        gb['comment'] = 'Full design report'
        gb['type'] = name
        gb['options'] = {'template': 'full_SVG'}
        if pandoc:
            gb['options']['do_convert'] = True
        outs.append(gb)
        return outs
