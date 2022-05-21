import gzip
import logging
import math
import pickle
import sys
from fractions import Fraction

import allesfitter
import lightkurve
import numpy
import pandas
from astroplan import Observer
import astropy.units as u
from astropy.time import Time

from lcbuilder.eleanor import TargetData
from sherlockpipe.nbodies.megno import MegnoStabilityCalculator
from sherlockpipe.nbodies.stability_calculator import StabilityCalculator
from sherlockpipe.sherlock import Sherlock
from sherlockpipe.validate import Validator

# sherlock = Sherlock(None)
# sherlock.setup_files(True, True, False)
# sherlock = sherlock.filter_multiplanet_ois()
# sherlock.ois.to_csv("multiplanet_ois.csv")

#Allesfitter stuff
# alles = allesfitter.allesclass("/mnt/0242522242521AAD/dev/workspaces/git_repositories/sherlockpipe/TIC305048087_[2]_bck/fit_2/")
# alles.posterior_samples("lc", "SOI_2_period")
# allesfitter.ns_output("/mnt/0242522242521AAD/dev/workspaces/git_repositories/sherlockpipe/run_tests/analysis/TIC142748283_all/fit_0/ttvs_0")
# results = pickle.load(open('/mnt/0242522242521AAD/dev/workspaces/git_repositories/sherlockpipe/run_tests/analysis/dietrich/TIC467179528_all/fit_2/results/ns_derived_samples.pickle', 'rb'))
# logging.info(results)

#Stability plots
# stability_dir = "/mnt/0242522242521AAD/dev/workspaces/git_repositories/sherlockpipe/run_tests/analysis/dietrich/TIC467179528_all/fit_2/stability_0/"
# df = pandas.read_csv(stability_dir + "stability_megno.csv")
# df = df[(df["megno"] < 3)]
# stability_calc = MegnoStabilityCalculator(5e2)
# for key, row in df.iterrows():
#     stability_calc.plot_simulation(row, stability_dir, str(key))

# Dataframe manipulation
filename = "TIC251848941_INP_sg_1.5/lc_2.csv"
df = pandas.read_csv(filename, float_precision='round_trip', sep=',',
                                     usecols=['#time', 'flux', 'flux_err'])
#df["flux"] = df["flux"] + 1
df = df.sort_values(by=['#time'], ascending=True)
df.to_csv(filename, index=False)

# periods = [5.43, 1.75, 2.62, 6.17]
# p1 = 1.75
# p2 = 5.43
# fraction = Fraction(1.75/5.43).limit_denominator(max_denominator=int(9))
# print(p2 * fraction.numerator % fraction.denominator)

# def compute_resonance(periods, tolerance=0.03):
#     max_number = 9
#     result = []
#     periods = numpy.sort(periods)
#     for i in range(0, len(periods)):
#         result.append([])
#         for j in range(0, len(periods)):
#             if j <= i:
#                 result[i].append("-")
#                 continue
#             fraction = Fraction(periods[i] / periods[j]).limit_denominator(max_denominator=int(max_number))
#             model = periods[j] * fraction.numerator / fraction.denominator
#             result[i].append("-" if numpy.sqrt((model - periods[i]) ** 2) > tolerance \
#                 else str(fraction.numerator) + "/" + str(fraction.denominator))
#     return periods, result
#
# formatter = logging.Formatter('%(message)s')
# logger = logging.getLogger()
# while len(logger.handlers) > 0:
#     logger.handlers.pop()
# logger.setLevel(logging.INFO)
# handler = logging.StreamHandler(sys.stdout)
# handler.setLevel(logging.INFO)
# handler.setFormatter(formatter)
# sorted_periods, resonances = compute_resonance([1.75, 5.43, 2.62, 6.17])
# header = "   "
# for period in sorted_periods:
#     header = header + "   " + str(sorted_periods)
# print(sorted_periods)
# for row_label, row in zip(sorted_periods, resonances):
#     print('%s [%s]' % (row_label, ' '.join('%03s' % i for i in row)))

# import psfmachine as psf
# import lightkurve as lk
# tpfs = lk.search_targetpixelfile('TIC 166184428', mission='TESS', sector=11, radius=100, limit=200, cadence='short')[0].download_all(quality_bitmask=None)
# machine = psf.TPFMachine.from_TPFs(tpfs, n_r_knots=10, n_phi_knots=12)
# try:
#     machine.fit_lightcurves(plot=True, fit_va=True)
#     for lc in machine.lcs:
#         lc.to_csv(lc.meta["LABEL"] + ".csv")
# finally:
#     print("FINISHED")

print(str(math.gcd(10, 10.945, 1.14)))

