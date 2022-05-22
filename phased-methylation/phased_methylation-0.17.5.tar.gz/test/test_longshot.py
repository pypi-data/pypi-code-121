import pytest
import pysam

from phased_methylation.env import (LONGSHOT_EXAMPLE_REFERENCE,
                                    LONGSHOT_EXAMPLE_READS,
                                    LONGSHOT_EXAMPLE_VARIANTS,
                                    LONGSHOT_EXACT_VARIANTS,
                                    LONGSHOT_UNPHASED_IDS,
                                    LONGSHOT_PHASED_IDS_1,
                                    LONGSHOT_PHASED_IDS_2)

from phased_methylation.phase import longshot

@pytest.fixture
def reference():
    return LONGSHOT_EXAMPLE_REFERENCE


@pytest.fixture
def reads():
    return LONGSHOT_EXAMPLE_READS


@pytest.fixture
def true_variants():
    return pysam.VariantFile(LONGSHOT_EXAMPLE_VARIANTS)


@pytest.fixture
def exact_variants():
    return pysam.VariantFile(LONGSHOT_EXACT_VARIANTS)


@pytest.fixture
def test_variants(reference, reads, tmp_path):
    longshot(reference, reads, tmp_path / 'out.vcf')
    return pysam.VariantFile(tmp_path / 'out.vcf')


def generate_phased_read_ids():
    for read_ids in (LONGSHOT_UNPHASED_IDS, LONGSHOT_PHASED_IDS_1,
                     LONGSHOT_PHASED_IDS_2):
        with open(read_ids) as f:
            yield tuple(l.rstrip() for l in f.readlines())


@pytest.fixture
def phased_read_ids():
    return tuple(generate_phased_read_ids())


def test_longshot_exact(test_variants, exact_variants):
    for test_rec in test_variants.fetch():
        exact_rec_tup = tuple(exact_variants.fetch(test_rec.contig,
                                                   test_rec.pos - 1,
                                                   test_rec.pos))
        assert len(exact_rec_tup) == 1
        exact_rec = exact_rec_tup[0]
        assert test_rec.contig == exact_rec.contig
        assert test_rec.pos == exact_rec.pos
        assert test_rec.id == exact_rec.id
        assert test_rec.alleles == exact_rec.alleles
        assert set(test_rec.samples.values()[0].alleles) == set(exact_rec.samples.values()[0].alleles)


def test_longshot_ground_truth(test_variants, true_variants):
    for test_rec in test_variants.fetch():
        true_rec_tup = tuple(true_variants.fetch(test_rec.contig,
                                                 test_rec.pos - 1,
                                                 test_rec.pos))
        assert len(true_rec_tup) == 1
        true_rec = true_rec_tup[0]
        assert test_rec.contig == true_rec.contig
        assert test_rec.pos == true_rec.pos
        assert test_rec.id == true_rec.id
        assert test_rec.ref == true_rec.ref
        if test_rec.alleles == true_rec.alleles:
            assert set(test_rec.samples.values()[0].alleles) == set(
                true_rec.samples.values()[0].alleles)
