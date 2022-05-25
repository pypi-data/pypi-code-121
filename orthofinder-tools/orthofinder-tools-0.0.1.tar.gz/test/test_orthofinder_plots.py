from unittest import TestCase
from orthofinder_tools import create_plots


class TestOrthoFinderPlots(TestCase):
    def test_create_plots_og(self):
        """
        orthofinder_plots \
            data/SpeciesTree_rooted.txt data/Orthogroups.tsv \
            output/plots/og svg False False
        """
        create_plots(
            tree='../data/SpeciesTree_rooted.txt',
            orthogroups_tsv='../data/Orthogroups.tsv',
            out='../output/plots/og',
            format='svg',
            no_labels=False
        )

    def test_create_plots_hog(self):
        """
        orthofinder_plots \
            data/SpeciesTree_rooted.txt data/N0.tsv \
            output/plots/hog svg False True
        """
        create_plots(
            tree='../data/SpeciesTree_rooted.txt',
            orthogroups_tsv='../data/N0.tsv',
            out='../output/plots/hog',
            format='svg',
            no_labels=False,
            hog=True
        )
