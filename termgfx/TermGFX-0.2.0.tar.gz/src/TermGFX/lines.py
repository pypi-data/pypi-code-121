from engine import Canvas
from shapes import Line

window_size = (20, 22)

lines = [
    Line((1, 1), (1, 10)),
    Line((1, 10), (10, 10)),
    Line((1, 1), (10, 10)),

    Line((18, 18), (15, 15))
]

canvas = Canvas(window_size)

for line in lines:
    line.draw(canvas)

canvas.draw()
