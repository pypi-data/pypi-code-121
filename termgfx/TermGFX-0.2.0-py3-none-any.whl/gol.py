"""
A yet another attempt to
implement Game of Life
in Python
"""

## Imports
from engine import Canvas, cursor_move
from time import sleep
import itertools


## Init
WINDOW_SIZE = (100, 30)
ALIVE = "█"
FPS = 30

frame = 1/FPS
alive_cells = [  # TODO: to be supplied by user
    (5, 5),
    (5, 6),
    (6, 6),
    (4, 7),
    (5, 7)
]
adjacent_templ = list(itertools.product(  # A template to represent adjacent alive_cells (excl. the cell itself)
    range(-1, 2),
    range(-1, 2)
)) # - [(0, 0)]
adjacent_templ.remove((0, 0))

canvas = Canvas(WINDOW_SIZE)

for cell in alive_cells:
    canvas.set(cell, ALIVE)

canvas.draw()
sleep(1)

## Main
running = True

while running:
    alive_adjacent = [
        tuple(map(sum, zip(cell, adj))) for adj in adjacent_templ
        for cell in alive_cells
    ]

    # Filter out-of-bounds'
    alive_adjacent = list(filter(lambda c: all(map(lambda x: x[0] - x[1] > 0 and x[1] >= 0, zip(WINDOW_SIZE, c))), alive_adjacent))

    cells = list(set(alive_adjacent + alive_cells))

    revive = []
    die = []

    for x, y in cells:
            # Simplify all living alive_cells
            cells_simpl = [
                tuple(map(
                    lambda p: p[0] - p[1],
                    zip(cell, (x, y))
                ))
                for cell in alive_cells
            ]

            # Find adjacent ones
            adjacent = tuple(filter(lambda c: c in adjacent_templ, cells_simpl))

            # Count them
            neighbors = len(adjacent)

            # Decide what to do with the cell
            match canvas.chars[y][x] == ALIVE:
                case True:
                    if neighbors in (2, 3):
                        pass
                    else:
                        # Die
                        canvas.set((x, y), " ")
                        die.append((x, y))
                case False:
                    if neighbors == 3:
                        # Ressurrect (?)
                        canvas.set((x, y), ALIVE)
                        revive.append((x, y))

    for cell in revive:
        alive_cells.append(cell)

    for cell in die:
        alive_cells.remove(cell)

    canvas.draw()
    print("Cells:", len(cells))

    sleep(frame)
