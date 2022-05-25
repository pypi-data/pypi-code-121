#!/usr/bin/env python
# PYTHON_ARGCOMPLETE_OK

"""
Post processing script to compute correlation functions from particle trajectories.
"""

import argh
import argparse
try:
    import argcomplete
except:
    argcomplete = None
from atooms.core.utils import setup_logging
from atooms.core.utils import add_first_last_skip
import atooms.postprocessing as postprocessing
import atooms.postprocessing.core
from atooms.postprocessing.api import msd, vacf, fkt, fskt, gr, sk, chi4qs, ik, alpha2, qst, qt, ba
from atooms.postprocessing.core import CustomHelpFormatter

# We add some global some flags. For backward compatibility, we keep
# them in the function signature as well.
parser = argparse.ArgumentParser(formatter_class=CustomHelpFormatter, description=__doc__)
parser = add_first_last_skip(parser)
parser.add_argument('--fmt', dest='fmt', help='trajectory format')
parser.add_argument('--center', action='store_true', dest='center', help='center system in cell')
parser.add_argument('--output', dest='output', default='{trajectory.filename}.pp.{symbol}.{tag}', help='output path')
parser.add_argument('--fast', action='store_true', dest='fast', help='deprecated: all backends are fast by default')
parser.add_argument('--legacy', action='store_true', dest='legacy', help='enable legacy backends')
parser.add_argument('--quiet', action='store_true', dest='quiet', help='quiet output')
parser.add_argument('--verbose', action='store_true', dest='verbose', help='verbose output')
parser.add_argument('--debug', action='store_true', dest='debug', help='debug output')
parser.add_argument('--nup', action='store_true', dest='nup', help='answer to NUP query')
parser.add_argument('--update', action='store_true', dest='update', help='compute only if update is needed')
parser.add_argument('--no-cache', action='store_true', dest='no_cache', help='disable trajectory cache')
parser.add_argument('--species-layout', dest='species_layout', help='force species layout to F, C or A')
parser.add_argument('--norigins', dest='norigins', help="time origins for averages")
parser.add_argument('--no-partial', action='store_true', dest='no_partial', help='disable partial correlations')
parser.add_argument('--filter', dest='filter', help='filter correlation function via arbitrary condition on particle properties')
argh.add_commands(parser, [msd, vacf, fkt, fskt, chi4qs, gr, sk, ik, alpha2, qst, qt, ba], func_kwargs={'formatter_class': CustomHelpFormatter})
if argcomplete is not None:
    argcomplete.autocomplete(parser)
args = parser.parse_args()

# Modify output path
postprocessing.correlation.core.pp_output_path = args.output 

if args.verbose:
    setup_logging('atooms', level=40)
    setup_logging('atooms.postprocessing', level=20)
    import atooms.postprocessing.progress
    atooms.postprocessing.progress.active = True
elif args.quiet:
    setup_logging('atooms', level=40)
    setup_logging('atooms.postprocessing', level=40)
    import atooms.postprocessing.progress
    atooms.postprocessing.progress.active = False
elif args.debug:
    setup_logging('atooms', level=40)
    setup_logging('atooms.postprocessing', level=10)
else:
    # Default is verbose
    setup_logging('atooms', level=40)
    setup_logging('atooms.postprocessing', level=20)
    import atooms.postprocessing.progress
    atooms.postprocessing.progress.active = True

argh.dispatching.dispatch(parser)
