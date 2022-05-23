"""
Gui classs: handles printing to the screen and user input
"""
import curses
from typing import Tuple

class Gui:

    def __init__(self,screen):
        curses.curs_set(0)
        curses.use_default_colors()
        curses.init_pair(1, curses.COLOR_RED, -1)

        self.screen = screen
        self.screen.nodelay(True)

    def clear_screen(self):
        self.screen.clear()

    def beep(self):
      curses.beep()
        
    def get_time_display(self,time_text) -> str:
      a = "####" 
      b = "#  #"
      c = "#   "
      d = "   #"
      o = "   "
      x = " # "

        
                   # 0,1,2,3,4,5,6,7,8,9,:
      templates = [ [a,d,a,a,b,a,a,a,a,a,o],
                    [b,d,d,d,b,c,c,d,b,b,x],
                    [b,d,a,a,a,a,a,d,a,a,o],
                    [b,d,c,d,d,d,b,d,b,d,x],
                    [a,d,a,a,d,a,a,d,a,a,o] ]

      out = ""
      for row in templates: 
        for digit in time_text:
          if digit == ":":
            digit = 10
          else:
            digit = int(digit,10)
          out = out + row[digit] + " "
        out = out + "\n"

      return out
      
    def print_screen(self,text):
        lines = text.rstrip("\n").split("\n")
        y,x = self.get_center_start(lines)
        self.display_lines(lines,y,x)

    def get_center_start(self, lines: list[str]) -> Tuple[int,int]:
        x = 0
        y = 0

        num_rows, num_cols = self.screen.getmaxyx()
        middle_row = int(num_rows / 2)
        middle_col = int(num_cols / 2)

        longest_line = max(map(len,lines))

        y = middle_row - int(len(lines) / 2)
        x = middle_col - int(longest_line / 2)

        return y,x

    def display_lines(self, lines: list[str], y: int, x: int):
      for line in lines:
        self.screen.addstr(y,x,line + "\n", curses.color_pair(1))
        y = y + 1
      self.screen.refresh()

    def handle_screen_input(self):
      try:
        key = self.screen.getkey()
      except curses.error as e:
        if str(e) == 'no input': return ''
        raise e
      return key
