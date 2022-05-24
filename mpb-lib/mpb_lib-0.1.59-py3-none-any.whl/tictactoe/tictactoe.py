from IPython.display import display, HTML

from .tictactoe_html import CSS, FRAME

cell_tmpl = """
<span class="order">{0}</span>
<span class="{1}">{2}</span>
"""


def show_board(gl):
    cell = [""]*9

    for n in range(1, 10):
        if f"c{n}" in gl:
            c = cell_tmpl.format(n, "pc", "X")
            cell[gl[f"c{n}"]-1] = c
        if f"p{n}" in gl:
            c = cell_tmpl.format(n, "human", "O")
            cell[gl[f"p{n}"]-1] = c

    if "c" in gl:
        for n, pl in enumerate(gl["c"]):
            c = cell_tmpl.format(n, "pc", "X")
            cell[pl-1] = c

    if "p" in gl:
        for n, pl in enumerate(gl["p"]):
            c = cell_tmpl.format(n, "human", "O")
            cell[pl-1] = c

    html_body = CSS
    html_body += FRAME.format(cell)
    display(HTML(html_body))


