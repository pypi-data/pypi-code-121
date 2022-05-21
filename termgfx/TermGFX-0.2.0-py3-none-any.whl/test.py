from engine import Canvas
from shapes import Line

canvas = Canvas((20, 10))
line = Line((3, 1), (6, 4))

line.draw(canvas)

canvas.draw()

line.move((0, 0))
line.draw(canvas)

canvas.draw()