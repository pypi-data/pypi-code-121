import os


def check_curses():
    import subprocess
    import sys
    try:
        import curses
    except:
        subprocess.check_call([sys.executable, "-m", "pip", "install", 'windows-curses'])
        import curses

try:
    import curses
except ImportError:
    check_curses()


def cls():
    os.system('cls' if os.name == 'nt' else 'clear')


def softcls():
    print("\n" * (os.get_terminal_size().lines * 2))


def center_message(text: str):
    print("\n" * (os.get_terminal_size().lines // 2 - 2))
    print(" " * ((os.get_terminal_size().columns//2 - (len(text)//2)) - 1) + text)
    print("\n" * (os.get_terminal_size().lines // 2 - 2))
    input()
    cls()


def center_multiline(text: list):
    print("\n" * ((os.get_terminal_size().lines // 2 - (len(text) // 2)) - 1))
    for line in text:
        print(" " * ((os.get_terminal_size().columns//2 - (len(line)//2)) - 1) + line)
    print("\n" * ((os.get_terminal_size().lines // 2 - (len(text) // 2)) - 2))
    input()
    cls()


def menu(menulist: dict):
    def print_menu(stdscr, selected_row_idx, menu):
        stdscr.clear()
        h, w = stdscr.getmaxyx()
        for idx, row in enumerate(menu):
            x = w//2 - len(row)//2
            y = h//2 - len(menu)//2 + idx
            if idx == selected_row_idx:
                stdscr.attron(curses.color_pair(1))
                stdscr.addstr(y, x, row)
                stdscr.attroff(curses.color_pair(1))
            else:
                stdscr.addstr(y, x, row)
        stdscr.refresh()

    global doing
    doing = 0
    global menupath
    menupath = []
    global currentmenu
    currentmenu= menulist
    global returning
    returning = None

    def mainmenu(stdscr):
        global doing
        global currentmenu
        global menupath
        global returning
        curses.curs_set(0)
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
        current_row = 0

        print_menu(stdscr, current_row, currentmenu)

        while True:
            key = stdscr.getch()

            if key == curses.KEY_UP and current_row > 0:
                current_row -= 1
            elif key == curses.KEY_UP and current_row == 0:
                current_row = len(currentmenu)-1
            elif key == curses.KEY_DOWN and current_row < len(currentmenu)-1:
                current_row += 1
            elif key == curses.KEY_DOWN and current_row == len(currentmenu) - 1:
                current_row = 0

            elif key == curses.KEY_ENTER or key in [10, 13] and \
                    isinstance(currentmenu[list(currentmenu.keys())[current_row]], dict):
                menupath.append(list(currentmenu)[current_row])
                currentmenu = currentmenu[list(currentmenu.keys())[current_row]]
                break

            elif key == curses.KEY_BACKSPACE or str(key) in ['KEY_BACKSPACE', '8', '127'] or \
                    currentmenu[list(currentmenu.keys())[current_row]] in ['ezztui_back_value', 'back']:
                menupath = menupath[:-1:]
                try:
                    currentmenu = menulist[list(menupath)[0]]
                    for i in menupath[1:]:
                        currentmenu = menulist[i]
                except:
                    currentmenu = menulist
                mainmenu(stdscr)
                break

            elif key == curses.KEY_ENTER or key in [10, 13] and currentmenu[list(currentmenu.keys())[current_row]] in \
                    ['ezztui_exit_value', 'exit']:
                exit()

            elif key == curses.KEY_ENTER or key in [10, 13]:
                menupath.append(list(currentmenu)[current_row])
                try:
                    returning = currentmenu[list(currentmenu.keys())[current_row]]()
                except TypeError:
                    returning = menupath
                break

            print_menu(stdscr, current_row, currentmenu)

    while returning is None:
        curses.wrapper(mainmenu)
    return returning
