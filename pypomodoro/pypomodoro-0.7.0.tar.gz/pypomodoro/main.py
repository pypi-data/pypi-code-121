#!/usr/bin/env python3
"""
Pomodoro
"""

__author__ = "Andrew Lowe"
__version__ = "0.7.0"
__license__ = "MIT"

import curses
import argparse
import time
import datetime as dt

from pomodoro import Pomodoro
from gui import Gui

def init_args():
  """ This is executed when run from the command line """
  parser = argparse.ArgumentParser()
  parser.add_argument("-w", "--work", default=25, type=float, action="store", dest="work_mins", help="Number of miinutes for work")
  parser.add_argument("-b", "--break", default=5, type=float, action="store", dest="break_mins", help="Number of minutes for break")
  parser.add_argument("-v", "--verbose", action="store_true", help="Move detailed display")
  
  # Specify output of "--version"
  parser.add_argument(
      "--version",
      action="version",
      version="%(prog)s (version {version})".format(version=__version__))

  args = parser.parse_args()
  return args

def start(screen):
    state_params = {
      'pomo' : {
        'text': 'Time to work',
        'alerted': False
      },
      'break': {
        'text': 'Take a break',
        'alerted': False
      },
      'done': {
        'text': 'Press space to get back to work',
        'alerted': False
      },
      'init': {
        'text': 'Press space to start work',
      }
    }

    time_left_init = "00:00:00"

    args = init_args()

    pomo = Pomodoro(args.work_mins,args.break_mins)
    gui = Gui(screen)

    gui.clear_screen()

    while True:
      pom_state = pomo.get_state()

      key_pressed = gui.handle_screen_input()

      if key_pressed == 'q':
        exit(0);

      now = dt.datetime.now()
      pom_end_time = pomo.pomo_end_time
      break_end_time = pomo.break_end_time
      pom_start_time = pomo.start_time

      if pom_state == "init":
        time_left = time_left_init
        if key_pressed == ' ':
          pomo.start()
          continue
      elif pom_state == "pomo":
        time_left = pom_end_time - now
      elif pom_state == "done":
        time_left = time_left_init
        if key_pressed == ' ':
          for st in state_params:
            state_params[st]['alerted'] = False
          pomo.restart()
          continue
      else :
        time_left = break_end_time - now

      display_info = state_params[pom_state]['text']

      if key_pressed != '':
        display_info = "Press 'q' to quit"
      
      if args.verbose and pom_state != "init":
        display_info += "\n" + f"Pomo number: {pomo.pomo_number}"
        display_info += "\n" + f"Pomo end time: {pomo.pomo_end_time:%H:%M:%S}"
        display_info += "\n" + f"Break end time: {pomo.break_end_time:%H:%M:%S%z}"
      time_left = str(time_left).split(".")[0]
      time_left = "{:0>8}".format(time_left)
      display_text = gui.get_time_display(time_left)
      display_text = display_text + "\n" + display_info

      if pom_state != 'init' and state_params[pom_state]['alerted'] == False:
        gui.beep()
        state_params[pom_state]['alerted'] = True
      gui.print_screen(display_text)
      time.sleep(1)

def main(screen=None):
  
  if not screen:
      curses.wrapper(main)
  else:
    start(screen)

if __name__ == "__main__": main()
