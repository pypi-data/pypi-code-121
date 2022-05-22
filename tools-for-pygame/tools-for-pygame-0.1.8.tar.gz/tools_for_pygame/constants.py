#!/usr/bin/env python3

# Ani
PERC         = 0b000001
PREV_VAL     = 0b000010
STARTING_VAL = 0b000100
FRAME        = 0b001000
ANIMATION    = 0b010000
ELEMENT      = 0b100000

# Button
BUTTON_NORMAL = 1
BUTTON_HOVER  = 2
BUTTON_CLICK  = 3

# Draw
ODD_CIRCLE_CACHE  = 0b001
EVEN_CIRCLE_CACHE = 0b010
RECT_CACHE        = 0b100
ALL_CACHES        = 0b111

# Colors
BLACK       = (1  , 1  , 1  , 255)
WHITE       = (255, 255, 255, 255)

RED         = (255, 0  , 0  , 255)
GREEN       = (0  , 255, 0  , 255)
BLUE        = (0  , 0  , 255, 255)
YELLOW      = (255, 255, 0  , 255)
CYAN        = (0  , 255, 255, 255)
MAGENTA     = (255, 0  , 255, 255)

MAROON      = (127, 0  , 0  , 255)
EMERALD     = (0  , 127, 0  , 255)
NAVY        = (0  , 0  , 127, 255)
OLIVE       = (127, 127, 0  , 255)
TEAL        = (0  , 127, 127, 255)
PURPURA     = (127, 0  , 127, 255)

ORANGE      = (255, 127, 0  , 255)
LIME        = (127, 255, 0  , 255)
AQUA        = (0  , 255, 127, 255)
LIGHT_BLUE  = (0  , 127, 255, 255)
PURPLE      = (127, 0  , 255, 255)
FUCHSIA     = (255, 0  , 127, 255)

SALMON      = (255, 127, 127, 255)
LIGHT_GREEN = (127, 255, 127, 255)
COBALT      = (127, 127, 255, 255)

LEMON       = (255, 255, 127, 255)
SKY_BLUE    = (127, 255, 255, 255)
PINK        = (255, 127, 255, 255)

# Anchor points
UL = "ul"
UC = "uc"
UR = "ur"
CL = "cl"
CC = "cc"
CR = "cr"
DL = "dl"
DC = "dc"
DR = "dr"

# Label styles
NO_AA     = 0b0001
BOLD      = 0b0010
ITALIC    = 0b0100
UNDERLINE = 0b1000

# Label alignments
LEFT = 0
RIGHT = 1
CENTER = 2

# Position options
ABSOLUTE = 0
AUTOMATIC = 1
