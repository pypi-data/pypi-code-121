# -*- coding: utf-8 -*-

# Python imports
import cProfile
import pstats
import io
import os

# Third party imports

# Local imports
from trendreview.GraphAll import GraphAll
from trendreview.reporting import FDDReporting

# Declarations
filepath = os.path.abspath("../data/ddvav_test.csv")
equipment_type = 'GraphAll'
log_filepath = os.path.abspath("../reports/report_profile.txt")
pstats_filepath = os.path.abspath("../reports/pstats_out.txt")

# %%

# Profile code below


def profile(fnc):
    """Code profiling for long run time of certain graphing issues"""

    def inner(*args, **kwargs):

        # Profile function in question
        profile = cProfile.Profile()
        profile.enable()
        return_val = fnc(*args, **kwargs)
        profile.disable()

        # Create string for storing process statistics and display
        s = io.StringIO()  # In-memory

        sortby = 'cumulative'
        ps = pstats.Stats(profile, stream=s).sort_stats(sortby)
        ps.print_stats()
        print(s.getvalue())
        with open(pstats_filepath, "wt", encoding="utf-8") as fs:
            fs.write(s.getvalue())

        return return_val

    return inner


@profile
def profile_graph_all_data():

    # For creating reports and visualizations
    reporter = FDDReporting(log_filepath=log_filepath)

    # Possilbe configuration in the future
    independent_axis_name = 'DateTime'
    dependent_axis_names = None  # Graph all

    # Load data
    graphall = GraphAll(filepath)
    graphall.graph_all_data(
        reporter, independent_axis_name, dependent_axis_names)

    return None


if __name__ == "__main__":
    profile_graph_all_data()
