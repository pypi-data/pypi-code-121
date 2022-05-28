#!/usr/bin/python

from traceback import format_exc
import sys, os, time, re, curses
import locale
locale.setlocale(locale.LC_ALL, '')
os.environ.setdefault('ESCDELAY', '250')
os.environ["NCURSES_NO_UTF8_ACS"] = "1"

colors = {'white': curses.COLOR_WHITE, 'red': curses.COLOR_RED, 'green': curses.COLOR_GREEN,
            'yellow': curses.COLOR_YELLOW, 'blue': curses.COLOR_BLUE, 'magenta': curses.COLOR_MAGENTA,
            'cyan': curses.COLOR_CYAN, 'black': curses.COLOR_BLACK}

class SuspendCurses():
    def __enter__(self):
        curses.endwin()
    def __exit__(self, exc_type, exc_val, tb):
        newscr = curses.initscr()
        newscr.refresh()
        curses.doupdate()

def cp(i):
    return curses.color_pair(i)

def set_pairs(fg, bg):
    curses.init_pair(1, fg, colors['black'])
    curses.init_pair(2, fg, colors['yellow'])
    curses.init_pair(3, fg, colors['white'])
    curses.init_pair(4, fg, colors['red'])
    curses.init_pair(5, colors['black'], bg)
    curses.init_pair(6, colors['yellow'], bg)
    curses.init_pair(7, colors['white'], bg)
    curses.init_pair(8, colors['red'], bg)

def main_loop(stdscr):
    ret = 0
    EXIT = False
    maxc = curses.COLORS
    maxy, maxx = stdscr.getmaxyx()
    if maxy < 10 or maxx < 65:
        with SuspendCurses():
            print('Terminal window needs to be at least 10h by 65w')
            print('Current h:{0}  and w:{1}'.format(maxy, maxx))
        ret = 1
        EXIT = True
    stdscr.refresh()
    h, w = 10, 65
    test_win = stdscr
    cursor = [2, 0]
    test_win.move(2, 2+cursor[1]*20)
    fgcol, bgcol = 1, 1
    set_pairs(fgcol, bgcol)
    test_win.refresh()
    teststr = '! @ # $ % ^ & *     _ + - = '
    while not EXIT:
        test_win.clear()
        test_win.addstr(1, 10, '{0} colors supported'.format(maxc), cp(0))
        test_win.addstr(2, 2, 'FG: {0}  '.format(fgcol), cp(0))
        test_win.addstr(2, 32, 'BG: {0}  '.format(bgcol), cp(0))
        for i in range(1,5):
            test_win.addstr(3+i, 2, teststr, cp(i))
            test_win.addstr(3+i, 32,teststr, cp(i+4))
        test_win.move(1, 2+cursor[1]*30)
        test_win.box()
        test_win.refresh()
        curses.napms(10)
    return ret

if __name__ == '__main__':
    try:
        _ret = curses.wrapper(main_loop)
    except Exception as e:
        print(e)
    finally:
        print('Exit status ' + str(_ret))
        sys.exit(_ret)
