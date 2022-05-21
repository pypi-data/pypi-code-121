from typing import Optional, Type

from colorama import Style

from . import BoxStyles


class Box:
    def __init__(self,
                 text: str,
                 style: Optional[Type[BoxStyles.BoxStyle]] = BoxStyles.Thin,
                 *,
                 color: Optional[str] = '',
                 ) -> None:
        self.text = text
        self.style = style
        self.color = color

    @staticmethod
    def from_2d_list(list_2d: list[list[str]],
                     style: Optional[Type[BoxStyles.BoxStyle]] = BoxStyles.Thin,
                     *,
                     color: Optional[str] = '',
                     ) -> 'Box':
        return Box(
            '\n'.join([''.join(x) for x in list_2d]),
            style=style,
            color=color,
        )

    def __str__(self) -> str:
        VERTICAL_LINE = self.style.VERTICAL_LINE
        HORIZONTAL_LINE = self.style.HORIZONTAL_LINE
        TOP_LEFT_CORNER = self.style.TOP_LEFT_CORNER
        TOP_RIGHT_CORNER = self.style.TOP_RIGHT_CORNER
        BOTTOM_LEFT_CORNER = self.style.BOTTOM_LEFT_CORNER
        BOTTOM_RIGHT_CORNER = self.style.BOTTOM_RIGHT_CORNER

        text = self.text.splitlines()
        width = len(max(text, key=len))
        color = self.color

        box = [color + TOP_LEFT_CORNER + (HORIZONTAL_LINE * width) + TOP_RIGHT_CORNER]
        for line in text:
            box.append(color
                       + VERTICAL_LINE
                       + Style.RESET_ALL
                       + line
                       + color
                       + ' ' * (width - len(line))
                       + VERTICAL_LINE)
        box.append(color + BOTTOM_LEFT_CORNER + (HORIZONTAL_LINE * width) + BOTTOM_RIGHT_CORNER)

        return '\n'.join(box)
