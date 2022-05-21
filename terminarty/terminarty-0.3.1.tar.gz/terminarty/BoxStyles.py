class BoxStyle:
    VERTICAL_LINE: str = ...
    HORIZONTAL_LINE: str = ...

    TOP_LEFT_CORNER: str = ...
    TOP_RIGHT_CORNER: str = ...
    BOTTOM_LEFT_CORNER: str = ...
    BOTTOM_RIGHT_CORNER: str = ...


class Ascii(BoxStyle):
    VERTICAL_LINE = '│'
    HORIZONTAL_LINE = '─'

    TOP_LEFT_CORNER = '+'
    TOP_RIGHT_CORNER = '+'
    BOTTOM_LEFT_CORNER = '+'
    BOTTOM_RIGHT_CORNER = '+'


class Thin(BoxStyle):
    VERTICAL_LINE = '│'
    HORIZONTAL_LINE = '─'

    TOP_LEFT_CORNER = '┌'
    TOP_RIGHT_CORNER = '┐'
    BOTTOM_LEFT_CORNER = '└'
    BOTTOM_RIGHT_CORNER = '┘'


class Thick(BoxStyle):
    VERTICAL_LINE = '┃'
    HORIZONTAL_LINE = '━'

    TOP_LEFT_CORNER = '┏'
    TOP_RIGHT_CORNER = '┓'
    BOTTOM_LEFT_CORNER = '┗'
    BOTTOM_RIGHT_CORNER = '┛'


class Double(BoxStyle):
    VERTICAL_LINE = '║'
    HORIZONTAL_LINE = '═'

    TOP_LEFT_CORNER = '╔'
    TOP_RIGHT_CORNER = '╗'
    BOTTOM_LEFT_CORNER = '╚'
    BOTTOM_RIGHT_CORNER = '╝'


class Round(BoxStyle):
    VERTICAL_LINE = '│'
    HORIZONTAL_LINE = '─'

    TOP_LEFT_CORNER = '╭'
    TOP_RIGHT_CORNER = '╮'
    BOTTOM_LEFT_CORNER = '╰'
    BOTTOM_RIGHT_CORNER = '╯'


class Dotted(BoxStyle):
    VERTICAL_LINE = '┊'
    HORIZONTAL_LINE = '┈'

    TOP_LEFT_CORNER = '┌'
    TOP_RIGHT_CORNER = '┐'
    BOTTOM_LEFT_CORNER = '└'
    BOTTOM_RIGHT_CORNER = '┘'
