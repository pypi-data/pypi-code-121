## Testing color support ##

from engine import Canvas, paint

canvas = Canvas((20, 10))

canvas.set((1, 1), paint("█", "#ff0000"))  # Red pixel, HEX color code
canvas.set((2, 1), paint("█", (0, 255, 0), mode="rgb"))  # Green pixel, RGB color code

canvas.draw()