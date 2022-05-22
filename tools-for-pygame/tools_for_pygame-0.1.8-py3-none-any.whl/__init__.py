#!/usr/bin/env python3
r"""
Pygame Tools by TheSilvered

This package is created to make pygame easier to use.
It introduces an entity system, math functions, a gui system and much
more.

Classes:
    - Pos  (pgt.mathf.Pos)
    - Size (pgt.mathf.Size)

    - Element                    (pgt.element.Element)
    - AniElement                 (pgt.element.AniElement)
    - MouseInteractionElement    (pgt.element.MouseInteractionElement)
    - MouseInteractionAniElement (pgt.element.MouseInteractionAniElement)

    - Lang (lang.Lang)

    - ani.FuncAniFrames (pgt.ani.FuncAniFrames)
    - ani.AniBase       (pgt.ani.AniBase)
    - ani.FuncAniBase   (pgt.ani.FuncAniBase)
    - ani.TextureAni    (pgt.ani.TextureAni)
    - ani.PosAni        (pgt.ani.PosAni)
    - ani.TextAni       (pgt.ani.TextAni)

    - gui.Button (pgt.gui.button.Button)
    - gui.Draggable (pgt.gui.draggable.Draggable)
    - gui.Font (pgt.gui.font.Font)
    - gui.GUIElement    (pgt.gui.gui_element.GUIElement)
    - gui.GUIAniElement (pgt.gui.gui_element.GUIAniElement)
    - gui.GUILayout (pgt.gui.gui_layout.GUILayout)
    - gui.Label    (pgt.gui.Label)
    - gui.AniLabel (pgt.gui.AniLabel)
    - gui.HSlider (pgt.gui.slider.HSlider)
    - gui.VSlider (pgt.gui.slider.VSlider)
    - gui.SurfaceElement (pgt.gui.surface_element.SurfaceElement)

    - Pos  (pgt.mathf.Pos)
    - Size (pgt.mathf.Size)

    - Stack (pgt.stack.Stack)

Exceptions:
    - InvalidPosError (pgt.exceptions.InvalidPosError)
    - EmptyStackError (pgt.exceptions.EmptyStackError)
    - LangError       (pgt.exceptions.LangError)

Functions:
    - add_col    (pgt.color.add_col)
    - sub_col    (pgt.color.sub_col)
    - mul_col    (pgt.color.mul_col)
    - min_col    (pgt.color.min_col)
    - max_col    (pgt.color.max_col)
    - calc_alpha (pgt.color.calc_alpha)
    - c_alpha    (pgt.color.c_alpha)
    - GRAY       (pgt.color.GRAY)
    - R          (pgt.color.R)
    - G          (pgt.color.G)
    - B          (pgt.color.B)

    - clamp            (pgt.mathf.clamp)
    - get_i            (pgt.mathf.clamp)
    - get_c            (pgt.mathf.clamp)
    - distance         (pgt.mathf.clamp)
    - abs_distance     (pgt.mathf.clamp)
    - e_in_sin         (pgt.mathf.e_in_sin)
    - e_out_sin        (pgt.mathf.e_out_sin)
    - e_in_out_sin     (pgt.mathf.e_in_out_sin)
    - e_in_quad        (pgt.mathf.e_in_quad)
    - e_out_quad       (pgt.mathf.e_out_quad)
    - e_in_out_quad    (pgt.mathf.e_in_out_quad)
    - e_in_cubic       (pgt.mathf.e_in_cubic)
    - e_out_cubic      (pgt.mathf.e_out_cubic)
    - e_in_out_cubic   (pgt.mathf.e_in_out_cubic)
    - e_in_quart       (pgt.mathf.e_in_quart)
    - e_out_quart      (pgt.mathf.e_out_quart)
    - e_in_out_quart   (pgt.mathf.e_in_out_quart)
    - e_in_quint       (pgt.mathf.e_in_quint)
    - e_out_quint      (pgt.mathf.e_out_quint)
    - e_in_out_quint   (pgt.mathf.e_in_out_quint)
    - e_in_exp         (pgt.mathf.e_in_exp)
    - e_out_exp        (pgt.mathf.e_out_exp)
    - e_in_out_exp     (pgt.mathf.e_in_out_exp)
    - e_in_circ        (pgt.mathf.e_in_circ)
    - e_out_circ       (pgt.mathf.e_out_circ)
    - e_in_out_circ    (pgt.mathf.e_in_out_circ)
    - e_in_back        (pgt.mathf.e_in_back)
    - e_out_back       (pgt.mathf.e_out_back)
    - e_in_out_back    (pgt.mathf.e_in_out_back)
    - e_in_elastic     (pgt.mathf.e_in_elastic)
    - e_out_elastic    (pgt.mathf.e_out_elastic)
    - e_in_out_elastic (pgt.mathf.e_in_out_elastic)
    - e_in_bounce      (pgt.mathf.e_in_bounce)
    - e_out_bounce     (pgt.mathf.e_out_bounce)
    - e_in_out_bounce  (pgt.mathf.e_in_out_bounce)

    - draw.clear_cache (pgt.draw.clear_cache)
    - draw.even_circle (pgt.draw.even_circle)
    - draw.odd_circle  (pgt.draw.odd_circle)
    - draw.aa_rect     (pgt.draw.aa_rect)
    - draw.aa_line     (pgt.draw.aa_line)

    - parse_json_file  (pgt.utils.parse_json_file)
    - load_image       (pgt.utils.load_image)
    - filled_surface   (pgt.utils.filled_surface)
    - replace_color    (pgt.utils.replace_color)
    - change_image_ani (pgt.utils.change_image_ani)
    - transform_func   (pgt.utils.transform_func)

Constants:
    - BLACK       (pgt.constants.BLACK)
    - WHITE       (pgt.constants.WHITE)
    - RED         (pgt.constants.RED)
    - GREEN       (pgt.constants.GREEN)
    - BLUE        (pgt.constants.BLUE)
    - YELLOW      (pgt.constants.YELLOW)
    - CYAN        (pgt.constants.CYAN)
    - MAGENTA     (pgt.constants.MAGENTA)
    - MAROON      (pgt.constants.MAROON)
    - EMERALD     (pgt.constants.EMERALD)
    - NAVY        (pgt.constants.NAVY)
    - OLIVE       (pgt.constants.OLIVE)
    - TEAL        (pgt.constants.TEAL)
    - PURPURA     (pgt.constants.PURPURA)
    - ORANGE      (pgt.constants.ORANGE)
    - LIME        (pgt.constants.LIME)
    - AQUA        (pgt.constants.AQUA)
    - LIGHT_BLUE  (pgt.constants.LIGHT_BLUE)
    - PURPLE      (pgt.constants.PURPLE)
    - FUCHSIA     (pgt.constants.FUCHSIA)
    - SALMON      (pgt.constants.SALMON)
    - LIGHT_GREEN (pgt.constants.LIGHT_GREEN)
    - COBALT      (pgt.constants.COBALT)
    - LEMON       (pgt.constants.LEMON)
    - SKY_BLUE    (pgt.constants.SKY_BLUE)
    - PINK        (pgt.constants.PINK)

    - UL (pgt.constants.UL)
    - UC (pgt.constants.UC)
    - UR (pgt.constants.UR)
    - CL (pgt.constants.CL)
    - CC (pgt.constants.CC)
    - CR (pgt.constants.CR)
    - DL (pgt.constants.DL)
    - DC (pgt.constants.DC)
    - DR (pgt.constants.DR)

    - PERC         (pgt.constants.PERC)
    - PREV_VAL     (pgt.constants.PREV_VAL)
    - STARTING_VAL (pgt.constants.STARTING_VAL)
    - FRAME        (pgt.constants.FRAME)
    - ANIMATION    (pgt.constants.ANIMATION)

    - ODD_CIRCLE_CACHE  (pgt.constants.ODD_CIRCLE_CACHE)
    - EVEN_CIRCLE_CACHE (pgt.constants.EVEN_CIRCLE_CACHE)
    - RECT_CACHE        (pgt.constants.RECT_CACHE)

    - BUTTON_NORMAL (pgt.constants.BUTTON_NORMAL)
    - BUTTON_HOVER  (pgt.constants.BUTTON_HOVER)
    - BUTTON_CLICK  (pgt.constants.BUTTON_CLICK)

    - NO_AA     (pgt.constants.NO_AA)
    - BOLD      (pgt.constants.BOLD)
    - ITALIC    (pgt.constants.ITALIC)
    - UNDERLINE (pgt.constants.UNDERLINE)

    - LEFT   (pgt.constants.LEFT)
    - RIGHT  (pgt.constants.RIGHT)
    - CENTER (pgt.constants.CENTER)

    - ABSOLUTE  (pgt.constants.ABSOLUTE)
    - AUTOMATIC (pgt.constants.AUTOMATIC)

Variables:
    - draw.even_circle_cache (pgt.draw.even_circle_cache)
    - draw.odd_circle_cache  (pgt.draw.odd_circle_cache)
    - draw.rect_cache        (pgt.draw.rect_cache)
"""

__author__ = "Davide Taffarello - TheSilvered"
__version__ = "0.1.8"

from . import ani
from .color import *
from .constants import *
from . import draw
from .element import *
from .exceptions import *
from . import gui
from . import lang
from .mathf import *
from .particle_manager import ParticleManager
from .stack import Stack
from .utils import *

print(f"Pygame tools by {__author__}, version: {__version__}")
