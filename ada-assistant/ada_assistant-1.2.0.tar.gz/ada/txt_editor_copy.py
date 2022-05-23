import curses
import curses.textpad

# a simple vim like editor
VIEW_STR = "[VIEW MODE]"
CMD_STR = "[CMD MODE]"
INSERT_STR = "[INSERT MODE]"
UNKNOWN_STR = "[UNKNOW STATE!!!]"

MOVE_KEYS = [curses.KEY_UP, curses.KEY_DOWN, curses.KEY_LEFT, curses.KEY_RIGHT]

# class Textbox(curses.textpad.Textbox):
#     def do_command(self, ch):
#         if ch == 127:
#             super(curses.textpad.Textbox, self).do_command(4)
#         else:
#             super(curses.textpad.Textbox, self).do_command(ch)


# heler function to get the code of key
def keyLookup():
    stdscr = curses.initscr()
    ch = stdscr.getch()
    curses.endwin()
    print(ch)


class TxtEditor:
    def __init__(self, content):
        self.content_ = content
        ## 0 is view mode, 1 is cmd mode, 2 is insert mode
        self.state_ = 0
        self.cmd_buff_ = ""
        self.stay_editing_ = True
        # cursor pos of cmd window
        self.yxc_ = [1, 0]
        # cursor pos of txt window
        self.yxt_ = [0, 0]


    def _render_state(self, window):
        if self.state_ == 0:
            stt_str = VIEW_STR
        elif self.state_ == 1:
            stt_str = CMD_STR
        elif self.state_ == 2:
            stt_str = INSERT_STR
        else:
            stt_str = UNKNOWN_STR
        # yx = curses.getsyx()

        window.addstr(0, 0, stt_str + '\n' + self.cmd_buff_)
        # window.move(*yx)


    def _render_content(self, window):
        yx = curses.getsyx()

        window.addstr(0, 0, '\n'.join(self.content_))
        #if self.state_ != 1:
        #    window.move(*yx)


    def _take_and_process_view(self, window):
        c = window.getch()
        if c == ord('i'):
            self.state_ = 2
        elif c == ord(':'):
            self.state_ = 1
            self.cmd_buff_ = ":"
        elif c in MOVE_KEYS:
            self._move_cursor(c)


    def _take_and_process_cmd(self, window):
        c = window.getch()
        if c >= 97 and c <= 122:
            self.cmd_buff_ = self.cmd_buff_ + chr(c)
            self.yxc_ = [2, len(self.cmd_buff_)]
        elif c == 10: # ENTER
            if self.cmd_buff_ == ":q":
                self.stay_editing_ = False
                self.cmd_buff_ = ""
        elif c == 27:
            self.cmd_buff_ = ""
            self.state_ = 0
        #window.move(2, len(self.cmd_buff_))


    def _take_and_process_insert(self, window):
        c = window.getch()
        self.stay_editing_ = True
        pass


    def _reset_state(self):
        self.state_ = 0
        self.cmd_buff_ = ""
        self.stay_editing_ = True


    def _move_cursor(self, move):
        assert move in MOVE_KEYS, "UNKNOWN MOVE KEYS"
        #yx = curses.getsyx()
        if move == MOVE_KEYS[0]:
            #window.move(max(0, yx[0] - 1), yx[1])
            self.yxt_[0] = max(0, yx[0] - 1)
        elif move == MOVE_KEYS[1]:
            #window.move(min(len(self.content_) - 1, yx[0] + 1), yx[1])
            #window.move(1, 1)
            self.yxt_[0] = min(len(self.content_) - 1,  yx[0] + 1)
        elif move == MOVE_KEYS[2]:
            #window.move(yx[0], max(0, yx[1] - 1))
            self.yxt_[1] = max(0, yx[1] - 1)
        elif move == MOVE_KEYS[3]:
            #window.move(yx[0], min(len(self.content_[yx[0]]), yx[1] + 1))
            self.yxt_[1] = min(len(self.content_[yx[0]]), yx[1] + 1)


    def run(self):
        self._reset_state()
        cmdscr = curses.initscr()
        txtscr = cmdscr.subwin(2, 0)
        cmdscr.clearok(True)
        txtscr.clearok(True)
        self._render_state(cmdscr)
        self._render_content(txtscr)
        while self.stay_editing_:
            cmdscr.move(*self.yxc_)
            txtscr.move(*self.yxt_)
            if self.state_ == 0:
                cmdscr.refresh()
                self._take_and_process_view(txtscr)
            elif self.state_ == 1:
                txtscr.refresh()
                self._take_and_process_cmd(cmdscr)
            elif self.state_ == 2:
                cmdscr.refresh()
                self._take_and_process_insert(txtscr)
            self._render_state(cmdscr)
            self._render_content(txtscr)
        cmdscr.clear()
        txtscr.clear()
        curses.endwin()
        self._reset_state()
        return self.content_
