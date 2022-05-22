#!/usr/bin/env python3

"""
pgt.draw

Type: module

Description: a module that contains some useful drawing utilities

Functions:
    - clear_cache(caches)
    - even_circle(surface, center, radius, color, border, border_color)
    - odd_circle(surface, center, radius, color, border, border_color)
    - aa_rect(surface, rect, color, corner_radius, border, border_color)
    - aa_line(surface, color, start_pos, end_pos, width=1)
"""

from typing import Optional

import pygame

from .color import calc_alpha
from .constants import ODD_CIRCLE_CACHE, EVEN_CIRCLE_CACHE, RECT_CACHE, ALL_CACHES
from .mathf import get_i, Pos
from .type_hints import _pos, _col_type

pygame.init()

even_circle_cache = {}
odd_circle_cache = {}
rect_cache = {}


def clear_cache(caches: int = ALL_CACHES) -> None:
    """
    clear_cache(caches=pgt.ALL_CACHES)

    Type: function

    Description: empties the caches of the draw functions, aa_line
        not included

    Args:
        'cashes' (int) specify what caches should be cleared, you can
            pass any combination of RECT_CACHE, EVEN_CIRCLE_CACHE and
            ODD_CIRCLE_CACHE separated by `|`

    Return type: None
    """
    if caches & ODD_CIRCLE_CACHE:
        odd_circle_cache.clear()
    if caches & EVEN_CIRCLE_CACHE:
        even_circle_cache.clear()
    if caches & RECT_CACHE:
        rect_cache.clear()


def _draw_quarters(surf, rad, col, border, b_col, w, h) -> None:
    in_rad = rad - border
    alpha_col = len(col) == 4
    alpha_b_col = b_col and len(b_col) == 4

    for x in range(rad):
        for y in range(rad):
            inv_x = w - x - 1
            inv_y = h - y - 1

            distance = get_i(x - rad, y - rad)

            if distance < in_rad:
                surf.set_at((x, y), col)
                surf.set_at((inv_x, y), col)
                surf.set_at((x, inv_y), col)
                surf.set_at((inv_x, inv_y), col)

            elif border and distance < in_rad + 1:
                alpha = 1 - (distance - in_rad)
                new_color = calc_alpha(col, b_col, alpha)
                surf.set_at((x, y), new_color)
                surf.set_at((inv_x, y), new_color)
                surf.set_at((x, inv_y), new_color)
                surf.set_at((inv_x, inv_y), new_color)

            elif distance < rad:
                surf.set_at((x, y), b_col)
                surf.set_at((inv_x, y), b_col)
                surf.set_at((x, inv_y), b_col)
                surf.set_at((inv_x, inv_y), b_col)

            elif distance < rad + 1:
                if border:
                    alpha = (b_col[3] if alpha_b_col else 255) * (1 - (distance - rad))
                    new_color = list(b_col[:3])
                else:
                    alpha = (col[3] if alpha_col else 255) * (1 - (distance - rad))
                    new_color = list(col[:3])
                new_color.append(alpha)

                surf.set_at((x, y), new_color)
                surf.set_at((inv_x, y), new_color)
                surf.set_at((x, inv_y), new_color)
                surf.set_at((inv_x, inv_y), new_color)


def even_circle(surface: Optional[pygame.Surface],
                center: _pos,
                radius: int,
                color: _col_type,
                border: int = 0,
                border_color: Optional[_col_type] = None) -> pygame.Surface:
    """
    even_circle(surface, center, radius, color, border=0, border_color=None)

    Type: function

    Description: draws a circle with a 2x2 center and returns a surface
        containing it, the same surface is blit onto the target surface
        if given

    Args:
        'surface' (pygame.Surface?): where the circle should be drawn
            if set to None, returns the image itself
        'center' (pgt.Pos): where the top-left pixel of the center should
            be on the surface
        'radius' (int): radius of the circle
        'color' (list, tuple): the color of the circle
        'border' (int): the thickness of the border, if 0 the border
            is not drawn
        'border_color' (tuple, list): the color of the border, can be
            omitted if border == 0

    Return type: pygame.Surface
    """

    blit_pos = (center[0] - radius, center[1] - radius)
    radius = round(radius)
    if radius - border < 0: border = radius

    key = (radius, color, border, border_color)

    surf = even_circle_cache.get(key, None)
    if surface is not None and surf is not None:
        surface.blit(surf, blit_pos)
        return surf

    new_surf = pygame.Surface((radius*2, radius*2), flags=pygame.SRCALPHA)
    new_surf.set_colorkey((0, 0, 0))

    _draw_quarters(
        new_surf,
        radius,
        color,
        border,
        border_color,
        radius*2,
        radius*2
    )

    if surface is not None: surface.blit(new_surf, blit_pos)
    even_circle_cache[key] = new_surf
    return new_surf


def odd_circle(surface: Optional[pygame.Surface],
               center: _pos,
               radius: int,
               color: _col_type,
               border: int = 0,
               border_color: Optional[_col_type] = None) -> pygame.Surface:
    """
    odd_circle(surface, center, radius, color, border=0, border_color=None)

    Type: function

    Description: draws a circle with a 1x1 center and returns a surface
        containing it, the same surface is blit onto the target surface
        if given

    Args:
        'surface' (pygame.Surface?): where the circle should be drawn
            if set to None, returns the image itself
        'center' (pgt.Pos): where the center should be on the surface
        'radius' (int): radius of the circle
        'color' (list, tuple): the color of the circle
        'border' (int): the thickness of the border, if 0 the border
            is not drawn
        'border_color' (tuple, list): the color of the border, can be
            omitted if border == 0

    Return type: pygame.Surface
    """
    blit_pos = (center[0] - radius, center[1] - radius)
    radius = round(radius)
    if radius - border < 0: border = radius

    key = (radius, color, border, border_color)

    surf = odd_circle_cache.get(key, None)
    if surface is not None and surf is not None:
        surface.blit(surf, blit_pos)
        return surf

    size = (radius * 2 + 1, radius * 2 + 1)

    new_surf = pygame.Surface(size, flags=pygame.SRCALPHA)
    new_surf.set_colorkey((0, 0, 0))

    _draw_quarters(
        new_surf,
        radius,
        color,
        border,
        border_color,
        radius * 2 + 1,
        radius * 2 + 1
    )

    if border:
        pygame.draw.line(new_surf, border_color, (radius, 0), (radius, radius*2))
        pygame.draw.line(new_surf, border_color, (0, radius), (radius*2, radius))
    pygame.draw.line(new_surf, color, (radius, border), (radius, radius*2 - border))
    pygame.draw.line(new_surf, color, (border, radius), (radius*2 - border, radius))

    if surface is not None: surface.blit(new_surf, blit_pos)
    odd_circle_cache[key] = new_surf
    return new_surf


def aa_rect(surface: Optional[pygame.Surface],
            rect: pygame.Rect,
            color: _col_type,
            corner_radius: int = 0,
            border: int = 0,
            border_color: Optional[_col_type] = None) -> pygame.Surface:
    """
    aa_rect(surface, rect, color, corner_radius=0, border=0, border_color=None)

    Type: function

    Description: draws a rect like pygame.draw.rect but anti-aliasing
        the corners and returns a surface containing it, the same
        surface is blit onto the target surface if given

    Args:
        'surface' (pygame.Surface?): where the rect should be drawn
            if set to None, returns the image itself
        'rect' (pygame.Rect): the rectangle to draw
        'color' (list, tuple): the color of the rectangle
        'corner_radius' (int): the radius of the curvature of the
            corners
        'border' (int): the thickness of the border, if 0 the border
            is not drawn
        'border_color' (tuple, list): the color of the border, can be
            omitted if border == 0

    Return type: pygame.Surface
    """
    corner_radius = round(corner_radius)
    if corner_radius > min(rect.width, rect.height) / 2:
        corner_radius = int(min(rect.width, rect.height) / 2)

    if border > min(rect.width, rect.height) / 2:
        border = int(min(rect.width, rect.height) / 2)

    key = (rect.size, color, corner_radius, border, border_color)

    surf = rect_cache.get(key, None)
    if surface is not None and surf is not None:
        surface.blit(surf, rect.topleft)
        return surf

    new_surf = pygame.Surface(rect.size, flags=pygame.SRCALPHA)
    new_surf.set_colorkey((0, 0, 0))
    line_rect = pygame.Rect(0, 0, rect.w, rect.h)
    inner_rect = pygame.Rect(border, border, rect.w - border*2, rect.h - border*2)
    inner_radius = corner_radius - border

    if border:
        pygame.draw.rect(new_surf, border_color, line_rect, 0, corner_radius)
    pygame.draw.rect(new_surf, color, inner_rect, 0, inner_radius)

    _draw_quarters(
        new_surf,
        corner_radius,
        color,
        border,
        border_color,
        rect.w,
        rect.h
    )

    if surface is not None: surface.blit(new_surf, rect.topleft)
    rect_cache[key] = new_surf
    return new_surf


def aa_line(surface: pygame.Surface,
            color: _col_type,
            start_pos: _pos,
            end_pos: _pos,
            width: int = 1) -> None:
    """
    aa_line(surface, color, start_pos, end_pos, width=1)

    Type: function

    Description: draws an anti-aliased line that can be thicker than
        one pixel

    Args:
        'surface' (pygame.Surface): the surface where to draw the line
        'color' (list, tuple): the color of the line
        'start_pos' (pgt.Pos): the position of the first point
        'end_pos' (pgt.Pos): the position of the second point
        'width' (int): the width of the line (can only be an odd number)

    Return type: None
    """
    if width <= 0: return
    # The line doesn't look good with an even width
    if not width % 2: width += 1

    horizontal = abs(start_pos[0] - end_pos[0]) <= abs(start_pos[1] - end_pos[1])

    pygame.draw.line(surface, color, start_pos, end_pos, round(width))
    line_offset = (width / 2, 0) if horizontal else (0, width / 2)
    pygame.draw.aaline(surface, color, start_pos + line_offset, end_pos + line_offset)
    pygame.draw.aaline(surface, color, start_pos - line_offset, end_pos - line_offset)
