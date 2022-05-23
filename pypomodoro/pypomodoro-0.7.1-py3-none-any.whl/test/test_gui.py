import unittest
import curses
import pathlib


from pypomodoro.gui import Gui

class TestGui(unittest.TestCase):
    
    def setUp(self):
        self.debug_text = None

        self.screen = curses.initscr()
        curses.start_color()
        self.gui = Gui(self.screen)

    def tearDown(self):
        curses.endwin()
        if self.debug_text:
            print("\n\n" + self.debug_text + "\n")

    def test_get_time_display(self):
        
        # Get expected output
        display_out_file = pathlib.Path(__file__).parent.joinpath('data/display_text_out.txt')
        with open(display_out_file, 'r') as f:
            expected_display_text = f.read()

        time_display = self.gui.get_time_display("01:23:04")
        self.assertEqual(time_display, expected_display_text)

    def test_get_center_start(self):
        # Text: 3 lines, longest line is 20chars 
        text = "aaaaaaaaaaaaaaaaaaaa\nbbbbbbbbbbbbb\naaaaaaaaaaaa"

        num_rows, num_cols = self.screen.getmaxyx()
        middle_row = int(num_rows / 2)
        middle_col = int(num_cols / 2)

        expected_y = middle_row - int(3/2)
        expected_x = middle_col - int(20/2)

        center_start = self.gui.get_center_start(text.splitlines())

        self.assertEqual(center_start, (expected_y, expected_x))
