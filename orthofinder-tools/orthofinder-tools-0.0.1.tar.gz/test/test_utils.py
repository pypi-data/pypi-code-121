from unittest import TestCase
import os
import pandas as pd
from orthofinder_tools import load_og, load_hog, ALLOWED_RESULT_TYPES


def import_orthofinder_table(path_to_table):
    """
    old function
    """
    assert os.path.isfile(path_to_table)
    pandas_table = pd.read_table(path_to_table, sep='\t', engine='c')
    pandas_table.set_index('Orthogroup', inplace=True)
    pandas_table = pandas_table.notna()  # make binary
    return pandas_table


class TestOrthoFinderPlots(TestCase):
    def test_compare(self):
        t1 = import_orthofinder_table('../data/Orthogroups.tsv')
        t2 = load_og('../data/Orthogroups.tsv', result_type='boolean')

        assert not (t1 != t2).any().any()

    def test_result_types_og(self):
        for result_type in ALLOWED_RESULT_TYPES:
            df = load_og('../data/Orthogroups.tsv', result_type=result_type)
            print(df)

    def test_result_types_hog(self):
        for result_type in ALLOWED_RESULT_TYPES:
            df = load_hog('../data/N0.tsv', result_type=result_type)
            print(df)
