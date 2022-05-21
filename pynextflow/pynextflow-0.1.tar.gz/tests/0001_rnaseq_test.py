import pynextflow as nf


params = {
    "reads": "$baseDir/data/ggal/ggal_gut_{1,2}.fq",
    "transcriptome": "$baseDir/data/ggal/ggal_1_48850000_49020000.Ggal71.500bpflank.fa",
    "outdir": "results",
    "multiqc": "$baseDir/multiqc"
}


@nf.process(
    tag="$transcriptome.simpleName",
    output=[ nf.path("'index'") ]
)
def index(transcriptome: nf.path) -> nf.bash:
    return \
        f"""
        salmon index --threads $task.cpus -t {transcriptome} -i index
        """


@nf.process(
    tag="$pair_id",
    input=[
        nf.path("index"),
        nf.tuple(nf.val("pair_id"), nf.path("reads"))
    ],
    output=[
        nf.path("pair_id")
    ]
)
def quant(index: str, pair_id: str, reads: str) -> nf.bash:
    return \
        f"""
        salmon quant --threads $task.cpus --libType=U -i {index} -1 {reads[0]} -2 {reads[1]} -o {pair_id}
        """


@nf.process(
    tag="FASTQC on $sample_id",
    publish_dir=params['outdir'],
    output=[nf.path("fastqc_${sample_id}_logs")]
)
def fastqc(sample_id: str, reads: nf.path) -> nf.bash:
    return \
        f"""
        fastqc.sh "{sample_id}" "{reads}"
        """


@nf.process(
    publish_dir=params['outdir'],
    input=[
        nf.path("'*'"),
        nf.path("config")
    ],
    output=[
        nf.path("'multiqc_report.html'")
    ]
)
def multiqc(config: str) -> nf.bash:
    return f"""
        cp {config}/* .
        echo "custom_logo: \\$PWD/logo.png" >> multiqc_config.yaml
        multiqc .
        """


@nf.workflow
def rnaseq(transcriptome, read_pairs):
    return quant(index(transcriptome), read_pairs).concat(fastqc(read_pairs)).collect()


@nf.workflow
def py_main():
    return multiqc(
        rnaseq(
            params["transcriptome"],
            nf.from_file_pairs(params["reads"], check_if_exists=True)
        ),
        params["multiqc"]
    )


#
# TESTS
#

import os
from os.path import join, dirname

import pytest
from tests.utils import launch_folder

# Skip test that require to run Nextflow
SKIP_NEXTFLOW_TESTS = os.environ.get('SKIP_NEXTFLOW_TESTS')


def test_rnaseq_script():
    with nf.Nextflow(debug=True):
        script = py_main()

    expected_script = join(dirname(__file__), "scripts", "0001_rnaseq.nf")
    with open(expected_script, "rt") as fd:
        assert script == fd.read()


@pytest.mark.skipif(SKIP_NEXTFLOW_TESTS, reason="unset SKIP_NEXTFLOW_TESTS to run it")
def test_rnaseq_run():
    launch_folder('0001_rnaseq')
    with nf.Nextflow(profile="docker"):
        py_main()
