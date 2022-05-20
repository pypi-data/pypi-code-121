import sys, os
dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(dir_path)

import feature_handler
import helper
def main():
    helper.coloured_text("this program is a fork of:\n&https://github.com/fieryhenry/BCGM-Python&", "#FFFFFF", "#FFFF00")
    helper.coloured_text("&i& (&jo912345& aka &!j0&) made this so that i could use &fieryhenry&'s tool without", "#FFFFFF", "#0A00ff")
    helper.coloured_text("wxpython &failing& to install because of a setup tools &bug&.\n", "#FFFFFF", "#FF0000")
    helper.check_update()
    while True:
        feature_handler.menu()
        print()

try:
    main()
except KeyboardInterrupt:
    exit()
    