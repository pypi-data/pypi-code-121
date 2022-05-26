import functools

# ansi codes let us control the terminal just
# by printing special escape sequences
esc = '\033['
codes = {'reset': esc+'0m',
        'bold': esc+'1m', 'b': esc+'1m',
        'bold_off': esc+'22m',
        'light': esc+'2m', 'dim': esc+'2m',
        'italic': esc+'3m', 'it': esc+'3m',
        'underlined': esc+'4m', 'u': esc+'4m',
        'blink': esc+'5m', 'flash': esc+'5m', 'f': esc+'5m',
        'highlight': esc+'7m', 'hi': esc+'7m', 'reverse': esc+'7m',  'mark': esc+'7m',
        'hidden': esc+'8m', 'invisible': esc+'8m',
        'crossout': esc+'9m',
        'red': esc+'31m', 'r': esc+'31m',
        'green': esc+'32m', 'g': esc+'32m',
        'yellow': esc+'33m',
        'blue': esc+'34m',
        'reset_color': esc+'39m',
        # the next escape codes are more powerful
        'clear': esc+'2J',
        'clear_to_end': esc+'J',
        'move_to_top': esc+'H',  # home
        'hide_cursor': esc+'?25l',
        'show_cursor': esc+'?25h',
        'save_cursor': esc+'s',
        'restore_cursor': esc+'u',
        'save_screen': esc+'?47h',
        'restore_screen': esc+'?47l',
        'up_line': esc+'F',
        'down_line': '\033E',
        'clear_line': esc+'K',
        'line_wrap_off': esc+'?7l',
        'line_wrap_on': esc+'?7h',
        }

def _do(n=1, cmd=None):
        print(codes[cmd]*n, end='', flush=True)
for key in codes:
        globals()[key] = functools.partial(_do, cmd=key)
