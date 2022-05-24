# -*- coding: utf-8 -*-
# Copyright (c) 2022 Salvador E. Tropea
# Copyright (c) 2022 Instituto Nacional de Tecnología Industrial
# License: GPL-3.0
# Project: KiBot (formerly KiPlot)
# KiCad bugs:
# - Text bold doesn't work
# - Shape Line and Rect swapped
"""
KiCad v5/6 Worksheet format.
A basic implementation of the .kicad_wks file format.
Documentation: https://dev-docs.kicad.org/en/file-formats/sexpr-worksheet/
"""
import io
from struct import unpack
from pcbnew import (wxPoint, wxSize, FromMM, GR_TEXT_HJUSTIFY_LEFT, GR_TEXT_HJUSTIFY_RIGHT, GR_TEXT_HJUSTIFY_CENTER,
                    GR_TEXT_VJUSTIFY_TOP, GR_TEXT_VJUSTIFY_CENTER, GR_TEXT_VJUSTIFY_BOTTOM, wxPointMM)
from ..gs import GS
if not GS.kicad_version_n:
    # When running the regression tests we need it
    from kibot.__main__ import detect_kicad
    detect_kicad()
if GS.ki6():
    from pcbnew import PCB_SHAPE, PCB_TEXT, FILL_T_FILLED_SHAPE, SHAPE_T_POLY
else:
    from pcbnew import DRAWSEGMENT, TEXTE_PCB
    PCB_SHAPE = DRAWSEGMENT
    PCB_TEXT = TEXTE_PCB
    FILL_T_FILLED_SHAPE = 0
    SHAPE_T_POLY = 4
from .sexpdata import load, SExpData
from .v6_sch import (_check_is_symbol_list, _check_float, _check_integer, _check_symbol_value, _check_str, _check_symbol,
                     _check_relaxed, _get_points, _check_symbol_str)
from ..svgutils.transform import ImageElement, GroupElement
from ..misc import W_WKSVERSION, KICAD5_SVG_SCALE
from .. import log

logger = log.get_logger()
setup = None
# The version of "kicad_wks" used for all tests
SUP_VERSION = 20210606
# Hash to convert KiCad 5 "%X" markers to KiCad 6 "${XXX}" text variables
KI5_2_KI6 = {'K': 'KICAD_VERSION', 'S': '#', 'N': '##', 'C0': 'COMMENT1', 'C1': 'COMMENT2', 'C2': 'COMMENT3',
             'C3': 'COMMENT4', 'C4': 'COMMENT5', 'C5': 'COMMENT6', 'C6': 'COMMENT7', 'C7': 'COMMENT8',
             'C8': 'COMMENT9', 'Y': 'COMPANY', 'F': 'FILENAME', 'D': 'ISSUE_DATE', 'Z': 'PAPER', 'R': 'REVISION',
             'P': 'SHEETNAME', 'T': 'TITLE'}


class WksError(Exception):
    pass


def text_from_ki5(text):
    for k, v in KI5_2_KI6.items():
        text = text.replace('%'+k, '${'+v+'}')
    text = text.replace('%%', '%')
    return text


def _check_mm(items, pos, name):
    return FromMM(_check_float(items, pos, name))


def _get_point(items, pos, sname, name):
    value = _check_symbol_value(items, pos, name, sname)
    ref = 'rbcorner'
    if len(value) > 3:
        ref = _check_symbol(value, 3, sname+' reference')
    return wxPoint(_check_mm(value, 1, sname+' x'), _check_mm(value, 2, sname+' y')), ref


def _get_size(items, pos, sname, name):
    value = _check_symbol_value(items, pos, name, sname)
    return wxSize(_check_mm(value, 1, sname+' x'), _check_mm(value, 2, sname+' y'))


class WksSetup(object):
    def __init__(self):
        super().__init__()
        self.text_w = self.text_h = FromMM(1.5)
        self.line_width = self.text_line_width = FromMM(0.15)
        self.left_margin = self.right_margin = self.top_margin = self.bottom_margin = FromMM(10)

    @staticmethod
    def parse(items):
        s = WksSetup()
        for i in items[1:]:
            i_type = _check_is_symbol_list(i)
            if i_type == 'textsize':
                s.text_w = _check_mm(i, 1, 'textsize width')
                s.text_h = _check_mm(i, 2, 'textsize height')
            elif i_type == 'linewidth':
                s.line_width = _check_mm(i, 1, i_type)
            elif i_type == 'textlinewidth':
                s.text_line_width = _check_mm(i, 1, i_type)
            elif i_type in ['left_margin', 'right_margin', 'top_margin', 'bottom_margin']:
                setattr(s, i_type, _check_mm(i, 1, i_type))
            else:
                raise WksError('Unknown setup attribute `{}`'.format(i))
        return s


class WksDrawing(object):
    c_name = 'base'

    def __init__(self):
        super().__init__()
        self.repeat = 1
        self.incrx = self.incry = 0
        self.comment = ''
        self.name = ''
        self.option = ''

    def parse_fixed_args(self, items):
        """ Default parser for fixed arguments.
            Used when no fixed args are used. """
        return 1

    def parse_specific_args(self, i_type, i, items, offset):
        """ Default parser for arguments specific for the class. """
        raise WksError('Unknown {} attribute `{}`'.format(self.c_name, i))

    @classmethod
    def parse(cls, items):
        s = cls()
        offset = s.parse_fixed_args(items)
        for c, i in enumerate(items[offset:]):
            i_type = _check_is_symbol_list(i)
            if i_type == 'repeat':
                s.repeat = _check_integer(i, 1, i_type)
            elif i_type in ['incrx', 'incry']:
                setattr(s, i_type, _check_mm(i, 1, i_type))
            elif i_type == 'comment':
                s.comment = _check_str(i, 1, i_type)
            elif i_type == 'name':
                s.nm = _check_relaxed(i, 1, i_type)
            elif i_type == 'option':
                # Not documented 2022/04/15
                s.option = _check_symbol(i, 1, i_type)
            else:
                s.parse_specific_args(i_type, i, items, c+offset)
        return s


class WksLine(WksDrawing):
    c_name = 'line'

    def __init__(self):
        super().__init__()
        self.start = wxPoint(0, 0)
        self.start_ref = 'rbcorner'
        self.end = wxPoint(0, 0)
        self.end_ref = 'rbcorner'
        self.line_width = setup.line_width
        self.shape = 0   # SHAPE_T_SEGMENT but is 1!

    def draw_line(e, p, st, en):
        s = PCB_SHAPE()
        s.SetShape(e.shape)
        s.SetStart(st)
        s.SetEnd(en)
        s.SetWidth(e.line_width)
        s.SetLayer(p.layer)
        p.board.Add(s)
        p.pcb_items.append(s)

    def draw(e, p):
        st, sti = p.solve_ref(e.start, e.incrx, e.incry, e.start_ref)
        en, eni = p.solve_ref(e.end, e.incrx, e.incry, e.end_ref)
        for _ in range(e.repeat):
            if GS.ki5() and e.shape:
                # Using KiCad 5 I always get a line. Why? What's missing?
                e.draw_line(p, st, wxPoint(en.x, st.y))
                e.draw_line(p, wxPoint(en.x, st.y), wxPoint(en.x, en.y))
                e.draw_line(p, wxPoint(en.x, en.y), wxPoint(st.x, en.y))
                e.draw_line(p, wxPoint(st.x, en.y), st)
            else:
                e.draw_line(p, st, en)
            st += sti
            en += eni
            if p.out_of_margin(st):
                break

    def parse_specific_args(self, i_type, i, items, offset):
        if i_type == 'linewidth':
            self.line_width = _check_mm(i, 1, i_type)
        elif i_type == 'start':
            self.start, self.start_ref = _get_point(items, offset, i_type, self.c_name)
        elif i_type == 'end':
            self.end, self.end_ref = _get_point(items, offset, i_type, self.c_name)
        else:
            super().parse_specific_args(i_type, i, items, offset)


class WksRect(WksLine):
    c_name = 'rect'

    def __init__(self):
        super().__init__()
        self.shape = 1  # SHAPE_T_RECT but is 0!!!


class WksFont(object):
    name = 'font'

    def __init__(self):
        super().__init__()
        self.bold = False
        self.italic = False
        self.size = wxSize(setup.text_w, setup.text_h)
        self.line_width = setup.text_line_width

    @staticmethod
    def parse(items):
        s = WksFont()
        for c, i in enumerate(items[1:]):
            i_type = _check_is_symbol_list(i, allow_orphan_symbol=('bold', 'italic'))
            if i_type == 'bold':
                s.bold = True
            elif i_type == 'italic':
                s.italic = True
            elif i_type == 'size':
                s.size = _get_size(items, c+1, i_type, WksFont.name)
            elif i_type == 'linewidth':
                s.line_width = _check_mm(i, 1, i_type)
            else:
                raise WksError('Unknown font attribute `{}`'.format(i))
        return s


class WksText(WksDrawing):
    c_name = 'tbtext'
    V_JUSTIFY = {'top': GR_TEXT_VJUSTIFY_TOP, 'bottom': GR_TEXT_VJUSTIFY_BOTTOM}
    H_JUSTIFY = {'center': GR_TEXT_HJUSTIFY_CENTER, 'right': GR_TEXT_HJUSTIFY_RIGHT, 'left': GR_TEXT_HJUSTIFY_LEFT}

    def __init__(self):
        super().__init__()
        self.pos = wxPoint(0, 0)
        self.pos_ref = 'rbcorner'
        self.font = WksFont()
        self.h_justify = GR_TEXT_HJUSTIFY_LEFT
        self.v_justify = GR_TEXT_VJUSTIFY_CENTER
        self.text = ''
        self.rotate = 0
        self.max_len = 0
        self.max_height = 0
        self.incr_label = 1

    def parse_fixed_args(self, items):
        self.text = _check_relaxed(items, 1, self.c_name+' text')
        return 2

    def parse_specific_args(self, i_type, i, items, offset):
        if i_type == 'rotate':
            self.rotate = _check_float(i, 1, i_type)
        elif i_type == 'pos':
            self.pos, self.pos_ref = _get_point(items, offset, i_type, self.c_name)
        elif i_type == 'justify':
            # Not documented 2022/04/15
            for index in range(len(i)-1):
                val = _check_symbol(i, index+1, i_type)
                if val in WksText.V_JUSTIFY:
                    self.v_justify = WksText.V_JUSTIFY[val]
                elif val in WksText.H_JUSTIFY:
                    self.h_justify = WksText.H_JUSTIFY[val]
                else:
                    raise WksError('Unknown justify value `{}`'.format(val))
        elif i_type == 'font':
            self.font = WksFont.parse(i)
        elif i_type == 'maxlen':
            # Not documented 2022/04/15
            self.max_len = _check_mm(i, 1, i_type)
        elif i_type == 'maxheight':
            # Not documented 2022/04/15
            self.max_height = _check_mm(i, 1, i_type)
        elif i_type == 'incrlabel':
            # Not documented 2022/04/15
            self.incr_label = _check_integer(i, 1, i_type)
        else:
            super().parse_specific_args(i_type, i, items, offset)

    def draw(e, p):
        pos, posi = p.solve_ref(e.pos, e.incrx, e.incry, e.pos_ref)
        text = GS.expand_text_variables(e.text, p.tb_vars)
        for _ in range(e.repeat):
            s = PCB_TEXT(None)
            s.SetText(text)
            s.SetPosition(pos)
            s.SetTextSize(e.font.size)
            if e.font.bold:
                s.SetBold(True)
                thickness = round(e.font.line_width*2)
            else:
                thickness = e.font.line_width
            if hasattr(s, 'SetTextThickness'):
                s.SetTextThickness(thickness)
            else:
                s.SetThickness(thickness)
            s.SetHorizJustify(e.h_justify)
            s.SetVertJustify(e.v_justify)
            s.SetLayer(p.layer)
            if e.font.italic:
                s.SetItalic(True)
            if e.rotate:
                s.SetTextAngle(e.rotate*10)
            # Adjust the text size to the maximum allowed
            if e.max_len > 0:
                w = s.GetBoundingBox().GetWidth()
                if w > e.max_len:
                    s.SetTextWidth(round(e.font.size.x*e.max_len/w))
            if e.max_height > 0:
                h = s.GetBoundingBox().GetHeight()
                if h > e.max_height:
                    s.SetTextHeight(round(e.font.size.y*e.max_height/h))
            # Add it to the board and to the list of things to remove
            p.board.Add(s)
            p.pcb_items.append(s)
            # Increment the position
            pos += posi
            if p.out_of_margin(pos):
                break
            # Increment the text
            # This is what KiCad does ... not very cleaver
            if text:
                text_end = text[-1]
                if text_end.isdigit():
                    # Only increment the last digit "9" -> "10", "10" -> "11", "19" -> "110"?!!
                    text_end = str(int(text_end)+e.incr_label)
                else:
                    text_end = chr((ord(text_end)+e.incr_label) % 256)
                text = text[:-1]+text_end
            else:
                text = '?'


class WksPolygon(WksDrawing):
    c_name = 'polygon'

    def __init__(self):
        super().__init__()
        self.pos = wxPoint(0, 0)
        self.pos_ref = 'rbcorner'
        self.rotate = 0
        self.line_width = setup.line_width
        self.pts = []

    def parse_specific_args(self, i_type, i, items, offset):
        if i_type == 'rotate':
            self.rotate = _check_float(i, 1, i_type)
        elif i_type == 'pos':
            self.pos, self.pos_ref = _get_point(items, offset, i_type, self.c_name)
        elif i_type == 'linewidth':
            self.line_width = _check_mm(i, 1, i_type)
        elif i_type == 'pts':
            self.pts.append([wxPointMM(p.x, p.y) for p in _get_points(i)])
        else:
            super().parse_specific_args(i_type, i, items, offset)

    def draw(e, p):
        pos, posi = p.solve_ref(e.pos, e.incrx, e.incry, e.pos_ref)
        for _ in range(e.repeat):
            for pts in e.pts:
                s = PCB_SHAPE()
                s.SetShape(SHAPE_T_POLY)
                if hasattr(s, 'SetFillMode'):
                    s.SetFillMode(FILL_T_FILLED_SHAPE)
                s.SetPolyPoints([pos+p for p in pts])
                s.SetWidth(e.line_width)
                s.SetLayer(p.layer)
                if e.rotate:
                    s.Rotate(pos, e.rotate*10)
                p.board.Add(s)
                p.pcb_items.append(s)
            pos += posi
            if p.out_of_margin(pos):
                break


class WksBitmap(WksDrawing):
    c_name = 'bitmap'

    def __init__(self):
        super().__init__()
        self.pos = wxPoint(0, 0)
        self.pos_ref = 'rbcorner'
        self.scale = 1.0
        self.data = b''

    def parse_specific_args(self, i_type, i, items, offset):
        if i_type == 'pos':
            self.pos, self.pos_ref = _get_point(items, offset, i_type, self.c_name)
        elif i_type == 'scale':
            self.scale = _check_float(i, 1, i_type)
        elif i_type == 'pngdata':
            for c in range(len(i)-1):
                v = _check_symbol_str(i, c+1, self.c_name+' pngdata', 'data')
                self.data += bytes([int(c, 16) for c in v.split(' ') if c])
        else:
            super().parse_specific_args(i_type, i, items, offset)

    def draw(e, p):
        # Can we draw it using KiCad? I don't see how
        # Make a list to be added to the SVG output
        p.images.append(e)

    def add_to_svg(e, svg, p):
        s = e.data
        w, h = unpack('>LL', s[16:24])
        # For KiCad 300 dpi is 1:1 scale
        dpi = 300/e.scale
        # Convert pixels to mm and then to KiCad units
        w = FromMM(w/dpi*25.4)
        h = FromMM(h/dpi*25.4)
        # KiCad informs the position for the center of the image
        pos, posi = p.solve_ref(e.pos, e.incrx, e.incry, e.pos_ref)
        for _ in range(e.repeat):
            img = ImageElement(io.BytesIO(s), w, h)
            x = pos.x-round(w/2)
            y = pos.y-round(h/2)
            img.moveto(x, y)
            if GS.ki5():
                # KiCad 5 uses Inches and with less resolution
                img.scale(KICAD5_SVG_SCALE)
            # Put the image in a group
            g = GroupElement([img])
            # Add the group to the SVG
            svg.append(g)
            # Increment the position
            pos += posi
            if p.out_of_margin(pos):
                break


class Worksheet(object):
    def __init__(self, setup, elements, version, generator, has_images):
        super().__init__()
        self.setup = setup
        self.elements = elements
        self.version = version
        self.generator = generator
        self.has_images = has_images

    @staticmethod
    def load(file):
        with open(file, 'rt') as fh:
            error = None
            try:
                wks = load(fh)[0]
            except SExpData as e:
                error = str(e)
            if error:
                raise WksError(error)
        if not isinstance(wks, list) or (wks[0].value() != 'page_layout' and wks[0].value() != 'kicad_wks'):
            raise WksError('No kicad_wks signature')
        elements = []
        global setup
        setup = WksSetup()
        version = 0
        generator = ''
        has_images = False
        for e in wks[1:]:
            e_type = _check_is_symbol_list(e)
            if e_type == 'setup':
                setup = WksSetup.parse(e)
            elif e_type == 'rect':
                elements.append(WksRect.parse(e))
            elif e_type == 'line':
                elements.append(WksLine.parse(e))
            elif e_type == 'tbtext':
                obj = WksText.parse(e)
                if not version:
                    obj.text = text_from_ki5(obj.text)
                elements.append(obj)
            elif e_type == 'polygon':
                elements.append(WksPolygon.parse(e))
            elif e_type == 'bitmap':
                elements.append(WksBitmap.parse(e))
                has_images = True
            elif e_type == 'version':
                version = _check_integer(e, 1, e_type)
                if version > SUP_VERSION:
                    logger.warning(W_WKSVERSION+"Unsupported worksheet version, loading could fail")
            elif e_type == 'generator':
                generator = _check_symbol(e, 1, e_type)
            else:
                raise WksError('Unknown worksheet attribute `{}`'.format(e_type))
        return Worksheet(setup, elements, version, generator, has_images)

    def set_page(self, pw, ph):
        pw = FromMM(pw)
        ph = FromMM(ph)
        self.pw = pw
        self.ph = ph
        self.lm = self.setup.left_margin
        self.tm = self.setup.top_margin
        self.rm = pw-self.setup.right_margin
        self.bm = ph-self.setup.bottom_margin

    def solve_ref(self, pt, inc_x, inc_y, ref):
        pt = wxPoint(pt.x, pt.y)   # Make a copy
        if ref[0] == 'l':
            pt.x += self.lm
        elif ref[0] == 'r':
            pt.x = self.rm-pt.x
            inc_x = -inc_x
        if ref[1] == 't':
            pt.y += self.tm
        elif ref[1] == 'b':
            pt.y = self.bm-pt.y
            inc_y = -inc_y
        return pt, wxPoint(inc_x, inc_y)

    def check_page(self, e):
        return e.option and ((e.option == 'page1only' and self.page != 1) or (e.option == 'notonpage1' and self.page == 1))

    def draw(self, board, layer, page, page_w, page_h, tb_vars):
        self.pcb_items = []
        self.set_page(page_w, page_h)
        self.layer = layer
        self.board = board
        self.page = page
        self.tb_vars = tb_vars
        self.images = []
        for e in self.elements:
            # Some objects are for the first page, other for all but the first page, and most for all
            if self.check_page(e):
                continue
            e.draw(self)

    def add_images_to_svg(self, svg):
        for e in self.images:
            e.add_to_svg(svg, self)

    def out_of_margin(self, p):
        """ Used to check if the repeat went outside the page usable area """
        return p.x > self.rm or p.y > self.bm

    def undraw(self, board):
        for e in self.pcb_items:
            board.Remove(e)
