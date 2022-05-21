import sys


def progressbar(
    step: int,
    total: int,
    title: str = "",
    print_perc: bool = True,
    disp_len: int = 150,
    bar_width: int = 60
) -> None:
    """
    Display a progressbar

    """

    perc = step / total * 100
    full_blocks = int(round(perc / 100 * bar_width))
    empty_blocks = bar_width - full_blocks
    disp = ""

    if step == total:
        disp += " "
    elif step % 2 == 0:
        disp += "|"
    else:
        disp += "-"

    disp += " [" + "#" * full_blocks + " " * empty_blocks + "]"

    if print_perc:
        disp += (" " + str(round(perc)) + "% ")

    if len(title) > 0:  # format the bar
        title = title + " (" + str(step) + "/" + str(total) + ")"
        title_bar_buffer = " " * (disp_len - len(disp) - len(title + ": "))
        disp = title + title_bar_buffer + disp

    sys.stdout.write("\r" + disp)
    sys.stdout.flush()
