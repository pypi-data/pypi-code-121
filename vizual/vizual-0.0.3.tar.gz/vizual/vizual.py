"""Runs the debug server on the dersire file

Usage:
    vizual [--file=FILE]
    
"""

import docopt
import os

def main():
    args = docopt.docopt(__doc__)
    target = args['--file'] # something.py filepath relative to the terminal.
    server = os.path.join(os.path.dirname(__file__), 'server.py')

    cmd = "(trap 'kill 0' SIGINT; python3 " + target + " & python3 " + server + ")"

    os.system(cmd)

if __name__ == '__main__':
    main()