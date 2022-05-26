from vinca._lib import ansi
from vinca._lib.terminal import LineWrapOff, AlternateScreen
from vinca._lib.readkey import readkey, keys

FRAME_WIDTH = 6


class Browser:
    quit_keys = ('q', keys.ESC)
    move_keys = ('j', 'k', keys.DOWN, keys.UP)

    def __init__(self, explicit_cardlist, make_basic_card, make_verses_card):
        self.cardlist = explicit_cardlist
        self.reviewing = False
        self.sel = 0
        self.frame = 0
        self.make_basic_card = make_basic_card
        self.make_verses_card = make_verses_card

    def __len__(self):
        return len(self.cardlist)

    @property
    def selected_card(self):
        return self.cardlist[self.sel]

    @property
    def visible_lines(self):
        return min(len(self), FRAME_WIDTH) + bool(self.status_bar)

    @property
    def status_bar(self):
        bar_text = ansi.codes['light'] + f'{self.sel + 1} of {len(self)}.' + \
                   '  ? for help\n' + ansi.codes['reset']
        return bar_text if len(self) > FRAME_WIDTH else ''

    def draw_browser(self):
        ansi.hide_cursor()
        with LineWrapOff():
            print(self.status_bar, end='')
            visible_cards = self.cardlist[self.frame:self.frame + FRAME_WIDTH]
            for i, card in enumerate(visible_cards, start=self.frame):
                if card.is_due:
                    ansi.blue()
                if card.deleted:
                    ansi.red()
                if i == self.sel:
                    ansi.highlight()
                print(card)
                ansi.reset()

    def clear_browser(self):
        ansi.up_line(self.visible_lines)
        ansi.clear_to_end()

    def close_browser(self):
        self.clear_browser()
        ansi.show_cursor()
        exit()

    def redraw_browser(self):
        self.clear_browser()
        self.draw_browser()

    def move(self, key):
        if key in ('j', keys.DOWN):
            self.move_down()
        if key in ('k', keys.UP):
            self.move_up()

    def move_down(self):
        if self.sel == len(self) - 1:
            return  # we are already at the bottom
        self.sel += 1
        # scroll down if we are off the screen
        self.frame += (self.frame + FRAME_WIDTH == self.sel)

    def move_up(self):
        if self.sel == 0:
            return  # we are already at the top
        self.sel -= 1
        # scroll up if we are off the screen
        self.frame -= (self.frame - 1 == self.sel)

    def print_help(self):
        self.clear_browser()
        ansi.show_cursor()
        print(''
              'J      move down               \n'
              'K      move up                 \n'
              'R      review                  \n'
              'E      edit                    \n'
              'T      edit tags               \n'
              'Q      quit                    \n'
              )
        exit()

    def review(self):
        self.reviewing = True
        self.browse()

    def browse(self):
        if not self.cardlist:
            print('no cards')
            return
        self.draw_browser()

        while True:
            self.redraw_browser()

            if self.reviewing:
                self.selected_card.review()
                if self.selected_card.last_action_grade == 'exit':
                    # exit reviewing mode
                    self.reviewing = False
                    continue
                # close the browser if we have reached the bottom
                if self.sel == len(self) - 1:
                    self.close_browser()
                # move down to the next card
                self.move_down()
                continue

            k = readkey()

            if k == 'r' or k == '\n' or k == '\r':
                self.reviewing = True

            if k == '?':
                self.print_help()

            if k in self.quit_keys:
                self.close_browser()

            if k in self.move_keys:
                self.move(k)

            if command := self.selected_card._hotkeys.get(k):
                with AlternateScreen():
                    command()

            if k in ('b', 'v'):
                with AlternateScreen():
                    new_card = self.make_basic_card() if k == 'b' \
                        else self.make_verses_card() if k == 'v' else None
                    self.cardlist.insert(self.sel, new_card)
                # if this makes us draw a status bar we go down an extra line
                if len(self) == FRAME_WIDTH + 1:
                    ansi.down_line()
