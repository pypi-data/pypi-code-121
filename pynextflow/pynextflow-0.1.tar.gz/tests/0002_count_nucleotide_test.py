import pynextflow as nf


@nf.process
def count_adenine(fasta_file: nf.path):
    return count_nucleotide('A', fasta_file)


def count_nucleotide(nucleotide: str, fasta_file: nf.path):
    total = 0
    with open(fasta_file, "r") as fd:
        for line in fd.readlines():
            if line.startswith(">"):
                continue
            total += np.count_nonzero(np.array(list(line)) == nucleotide)
    return fasta_file, total

#
# TESTS
#
import pytest

import os
import numpy as np

from tests.utils import load_script, launch_folder

# Skip test that require to run Nextflow
SKIP_NEXTFLOW_TESTS = os.environ.get('SKIP_NEXTFLOW_TESTS')


def test_count_adenine_single():
    launch_folder('0002_count_nucleotide')
    _, total = count_adenine("data/ggal/ref1.fa")
    assert total == 48293


def test_count_adenine_local():
    launch_folder('0002_count_nucleotide')
    fasta_files = nf.from_path("data/ggal/*.fa")
    with nf.Local():
        res = count_adenine(fasta_files)
    total = sum(t for _, t in res)
    assert total == 144879


@pytest.mark.skipif(SKIP_NEXTFLOW_TESTS, reason="unset SKIP_NEXTFLOW_TESTS to run it")
def test_count_adenine_nextflow():
    launch_folder('0002_count_nucleotide')
    fasta_files = nf.from_path("data/ggal/*.fa")
    with nf.Nextflow():
        res = count_adenine(fasta_files)
    total = sum(t for _, t in res)
    assert total == 144879


def test_count_adenine_nextflow_script():
    fasta_files = nf.from_path("data/ggal/*.fa")
    with nf.Nextflow(debug=True):
        script = count_adenine(fasta_files)

    assert script == load_script("0002_count_nucleotide.nf")





