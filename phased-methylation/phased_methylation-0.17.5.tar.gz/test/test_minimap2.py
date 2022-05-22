import pytest
import pysam

from phased_methylation.env import (MINIMAP2_EXAMPLE_HUMAN,
                                    MINIMAP2_EXAMPLE_ORANG,
                                    MINIMAP2_EXAMPLE_ALIGNMENT)
from phased_methylation.map import minimap2

@pytest.fixture
def human():
    return MINIMAP2_EXAMPLE_HUMAN


@pytest.fixture
def orang():
    return MINIMAP2_EXAMPLE_ORANG


def test_map(human, orang, tmp_path):
    exact_alignment = pysam.AlignmentFile(MINIMAP2_EXAMPLE_ALIGNMENT, 'rb')
    test_alignment = pysam.AlignmentFile(minimap2(human, query=orang,
        output_bam=str(tmp_path / 'test.bam')), 'rb')
    for test_read, exact_read in zip(test_alignment.fetch(),
                                     exact_alignment.fetch()):
        assert test_read.to_string() == exact_read.to_string()
    test_alignment.close()
    exact_alignment.close()
