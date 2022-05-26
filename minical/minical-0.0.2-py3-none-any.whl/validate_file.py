"""
Convenience CLI script for making sure an event is valid
Takes a path, sets folder of path to be the events dir, and loads the event using the rest

This might be useful if you make a file using some other tool that's not hooked into the automatic
validation from the web UI or python modules
"""

import sys

from . import util

def main():
    """Take a path and throw errors if file is badly formatted"""
    path = sys.argv[1]

    event = util.load_event_from_file(path, is_path=True)
    util.validate_event(event)

if __name__ == "__main__":
    main()
