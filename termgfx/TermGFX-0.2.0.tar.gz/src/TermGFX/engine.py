import os

# Unicode frame chars (defaults)
VERT_BORDER = "│"
HORIZ_BORDER = "─"
LU_CORNER = "┌"
LL_CORNER = "└"
RU_CORNER = "┐"
RL_CORNER = "┘"

# Types
Pos = tuple[int, int] | list[int, int]
Size = Pos

# Exceptions
class EngineError(Exception):
    pass

# Classes
# Graphics canvas
class Canvas:
    def __init__(self,
                size: Size,
                borders: dict = {
                        "vert": VERT_BORDER,
                        "horiz": HORIZ_BORDER,
                        "lu": LU_CORNER,
                        "ll": LL_CORNER,
                        "ru": RU_CORNER,
                        "rl": RL_CORNER
                     },
                 spacing: int = 0,
                 init_char: str = " "):
        assert size[0] > 0 and size[1] > 0, "Size should be 1 or bigger"

        self.size = size
        self.borders = borders
        self.spacing = spacing
        self.changes = dict()
        self.chars = [[init_char for _ in range(self.size[0])] for _ in range(self.size[1])]

        self.__init_draw()


    def __init_draw(self):
        # Draw the upper border
        print(self.borders["lu"] + \
            self.borders["horiz"] * (self.size[0] + self.spacing * 2) + \
            self.borders["ru"])

        # Draw the middle part(-s)
        for line in self.chars:
            print(self.borders["vert"] + \
                " " * self.spacing + \
                "".join(line) + \
                " " * self.spacing + \
                self.borders["vert"])

        # Draw the lower border
        print(self.borders["ll"] + \
            self.borders["horiz"] * (self.size[0] + self.spacing * 2) + \
            self.borders["rl"])


    # Draw the canvas on the screen (terminal)
    def draw(self, return_at_bottom: bool = True):
        for pos, char in self.changes.items():
            print(pos)
            self.chars[pos[1]][pos[0]] = char

            print(cursor_move(pos) + char, end="")

            if return_at_bottom:
                print(cursor_move((0, self.size[1])))

        # Clear the changes list (dict)
        self.changes = {}


    # Set a "pixel" to a specified value
    def set(self, pos: Pos, char: str):
        self.changes.update({(pos[0], pos[1]): char})


# Return an OS-specific escape sequence
def get_escape():
    if os.name == "posix":
        return "\033"
    else:
        raise EngineError("No support for Windows for now :(")

# Return a color escape sequence from RGB/HEX color code
def color_seq(value, mode="hex"):
    assert mode in ("rgb", "hex"), f"Unknown color mode: {mode}"

    ESC = get_escape()

    if mode == "hex":
        value = value.strip("#")
        colors = []

        HEX_LEN = 6

        for i in range(0, HEX_LEN, 2):
            color = int(value[i:i+2], 16)  # Str representing a color band in HEX

            colors.append(str(color))  # Convert the value to decimal
    else:
        assert len(value) == 3, "RGB values should contain 3 exactly bands"

        colors = map(str, value)

    seq = f"{ESC}[38;2;{';'.join(colors)}m"

    return seq

# Return a provided message colored using escape sequences
def paint(msg, color, mode="hex"):
    ESC = get_escape()
    CLEAR = f"{ESC}[0m"  # Sequence to clear color

    # Transform a color encoding to an escape sequence
    color = color_seq(color, mode=mode)

    colored = f"{color}{msg}{CLEAR}"

    return colored

# Return a cursor moving escape sequence (to be printed)
def cursor_move(pos: Pos):
    ESC = get_escape()

    line = pos[1] + 2  # Add 1 since 0th is border
    column = pos[0] + 2  # Also add 1

    return f"{ESC}[{line};{column}H"
