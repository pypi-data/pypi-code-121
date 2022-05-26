import shutil
from io import IOBase
from typing import Callable, Optional

color_names = ('black', 'red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'white')
foreground = {color_names[x]: '3%s' % x for x in range(8)}
background = {color_names[x]: '4%s' % x for x in range(8)}

RESET = '0'
opt_dict = {'bold': '1', 'underscore': '4', 'blink': '5', 'reverse': '7', 'conceal': '8'}


def colorize(text: str = '', opts=(), **kwargs) -> str:
    """
    Return your text, enclosed in ANSI graphics codes.

    Depends on the keyword arguments 'fg' and 'bg', and the contents of
    the opts tuple/list.

    Return the RESET code if no parameters are given.

    Valid colors:
        'black', 'red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'white'

    Valid options:
        'bold'
        'underscore'
        'blink'
        'reverse'
        'conceal'
        'noreset' - string will not be auto-terminated with the RESET code

    Examples:
        colorize('hello', fg='red', bg='blue', opts=('blink',))
        colorize()
        colorize('goodbye', opts=('underscore',))
        print(colorize('first line', fg='red', opts=('noreset',)))
        print('this should be red too')
        print(colorize('and so should this'))
        print('this should not be red')
    """
    code_list = []
    if text == '' and len(opts) == 1 and opts[0] == 'reset':
        return '\x1b[%sm' % RESET
    for k, v in kwargs.items():
        if k == 'fg':
            code_list.append(foreground[v])
        elif k == 'bg':
            code_list.append(background[v])
    for o in opts:
        if o in opt_dict:
            code_list.append(opt_dict[o])
    if 'noreset' not in opts:
        text = '%s\x1b[%sm' % (text or '', RESET)
    return '%s%s' % (('\x1b[%sm' % ';'.join(code_list)), text or '')


def make_style(opts=(), **kwargs) -> Callable[[str], str]:
    """
    Return a function with default parameters for colorize()

    Example:
        bold_red = make_style(opts=('bold',), fg='red')
        print(bold_red('hello'))
        KEYWORD = make_style(fg='yellow')
        COMMENT = make_style(fg='blue', opts=('bold',))
    """
    return lambda text: colorize(text, opts, **kwargs)


NOCOLOR_PALETTE = 'nocolor'
DARK_PALETTE = 'dark'
LIGHT_PALETTE = 'light'

PALETTES = {
    NOCOLOR_PALETTE: {
        'ERROR': {},
        'SUCCESS': {},
        'WARNING': {},
        'INFO': {},
    },
    DARK_PALETTE: {
        'ERROR': {'fg': 'red', 'opts': ('bold',)},
        'SUCCESS': {'fg': 'green', 'opts': ('bold',)},
        'WARNING': {'fg': 'yellow', 'opts': ('bold',)},
        'INFO': {'fg': 'blue'}
    },
    LIGHT_PALETTE: {
        'ERROR': {'fg': 'red', 'opts': ('bold',)},
        'SUCCESS': {'fg': 'green', 'opts': ('bold',)},
        'WARNING': {'fg': 'yellow', 'opts': ('bold',)},
        'INFO': {'fg': 'blue'}
    }
}
DEFAULT_PALETTE = DARK_PALETTE


def show_progress(count: int, total: int, text: str = '', out: Optional[IOBase] = None):
    text = f'{str(text)} ' if text else ''
    textlen, countlen, totallen = len(text), len(str(count)), len(str(total))
    maxlen = max(countlen, totallen)
    termwidth = shutil.get_terminal_size().columns - (textlen + maxlen + totallen + 10)
    rate = count / max(count, total)
    percents = termwidth * rate
    bars = ('█' * int(percents), '░' * int(termwidth - percents))
    msg = f'\r{text}[{count: <{totallen}}/{total: <{totallen}}][{int(rate * 100): >3}%% %s%s]' % bars

    if out:
        out.write(msg)
    else:
        print(msg, end='')
