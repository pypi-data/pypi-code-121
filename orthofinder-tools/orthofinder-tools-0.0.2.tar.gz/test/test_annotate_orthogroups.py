from unittest import TestCase
import os
from orthofinder_tools import OrthogroupToGeneName

BASE = os.path.expanduser('~/PycharmProjects/opengenomebrowser-alt-dbs/demo-folder_structure/OrthoFinder')
PATH_TO_ORTHOFINDER_FASTAS = f'{BASE}/fastas'


class TestOrthogroupToGeneName(TestCase):
    def setUp(self) -> None:
        self.ogn = OrthogroupToGeneName(
            fasta_dir=PATH_TO_ORTHOFINDER_FASTAS,
            file_endings='faa'
        )

    def test_run_og(self):
        """
        annotate_orthogroups \
            data/Orthogroups.tsv $OF_PATH output/og_majority_df.tsv False faa
        """
        self.ogn.load_og(
            og_tsv='../data/Orthogroups.tsv'
        )
        self.ogn.save_majority_df(out_file=F'../output/og_majority_df.tsv')
        self.ogn.save_orthogroup_to_best_name(out_file=F'../output/og_majority_df_bn.tsv', header=True)
        print('number of OG entries:', len(self.ogn.majority_dict))

    def test_run_hog_0(self):
        """
        annotate_orthogroups \
            data/N0.tsv $OF_PATH output/hog_majority_df.tsv True faa
        """
        self.ogn.load_hog(
            hog_tsv='../data/N0.tsv'
        )
        self.ogn.save_majority_df(out_file=F'../output/hog.0_majority_df.tsv')
        self.ogn.save_orthogroup_to_best_name(out_file=F'../output/hog.0_majority_df_bn.tsv', header=True)
        print('number of HOG entries:', len(self.ogn.majority_dict))

    def test_run_hog_1(self):
        self.ogn.load_hog(
            hog_tsv='../data/N1.tsv'
        )
        self.ogn.save_majority_df(out_file=F'../output/hog.1_majority_df.tsv')
        print('number of HOG entries:', len(self.ogn.majority_dict))

    def test_run_hog_2(self):
        self.ogn.load_hog(
            hog_tsv='../data/N2.tsv'
        )
        self.ogn.save_majority_df(out_file=F'../output/hog.2_majority_df.tsv')
        print('number of HOG entries:', len(self.ogn.majority_dict))

    def test_run_hog_3(self):
        self.ogn.load_hog(
            hog_tsv='../data/N3.tsv'
        )
        self.ogn.save_majority_df(out_file=F'../output/hog.3_majority_df.tsv')
        print('number of HOG entries:', len(self.ogn.majority_dict))

    def test_run_hog_4(self):
        self.ogn.load_hog(
            hog_tsv='../data/N4.tsv'
        )
        self.ogn.save_majority_df(out_file=F'../output/hog.4_majority_df.tsv')
        print('number of HOG entries:', len(self.ogn.majority_dict))

    def test_run_hog_22(self):
        self.ogn.load_hog(
            hog_tsv='../data/N22.tsv'
        )
        self.ogn.save_majority_df(out_file=F'../output/hog.22_majority_df.tsv')
        print('number of HOG entries:', len(self.ogn.majority_dict))
