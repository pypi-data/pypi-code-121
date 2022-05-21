##  Some rects  ##

## Imports
from engine import Canvas
from shapes import BaseRect, FilledRect


# Defs
window_size = (25, 10)

rect1 = BaseRect((
    list("uwu"),
    list("kek")
))

rect2 = FilledRect((5, 4))


# Main
canvas = Canvas(window_size)

rect1.draw(canvas, (5, 2))
rect2.draw(canvas, (14, 5))

canvas.draw()
