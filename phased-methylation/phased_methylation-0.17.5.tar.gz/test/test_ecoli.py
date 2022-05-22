import pytest
import shutil
from phased_methylation.env import ECOLI_REFERENCE, ECOLI_READS
from phased_methylation.map import index_reference, map_reads
from phased_methylation.phase import (longshot, extract_phased_read_ids,
                                     add_contigs_to_vcf)

@pytest.fixture
def ecoli_reads():
    return ECOLI_READS


def test_map_phase(ecoli_reads, tmp_path):
    shutil.copy(ECOLI_REFERENCE, tmp_path / 'draft.fa')
    ecoli_reference = str(tmp_path / 'draft.fa')
    minimap2_ont_bam = str(tmp_path / 'reads.bam')
    longshot_vcf = tmp_path / 'longshot.vcf'
    tagged_bam = str(tmp_path / 'tagged.bam')
    fixed_vcf = tmp_path / 'fixed.vcf'
    read_ids_unphased = tmp_path / 'read_ids_unphased.txt'
    read_ids_hap1 = tmp_path / 'read_ids_hap1.txt'
    read_ids_hap2 = tmp_path / 'read_ids_hap2.txt'

    index_reference(ecoli_reference)
    map_reads(ecoli_reference, ecoli_reads, minimap2_ont_bam)
    longshot(ecoli_reference, minimap2_ont_bam,
             longshot_vcf, tagged_bam=tagged_bam)
    for file, read_ids in zip((read_ids_unphased, read_ids_hap1, read_ids_hap2),
                              extract_phased_read_ids(tagged_bam)):
        with open(file, 'w') as f:
            f.write('\n'.join(read_ids) + '\n')
    add_contigs_to_vcf(ecoli_reference, longshot_vcf, fixed_vcf)
