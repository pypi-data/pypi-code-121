#######################################################################
#
# Copyright (C) 2020, 2021 David Palao
#
# This file is part of PacBioDataProcessing.
#
#  PacBioDataProcessing is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  PacBio data processing is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with PacBioDataProcessing. If not, see <http://www.gnu.org/licenses/>.
#
#######################################################################

"""Functional Tests for `bam-filter` utility."""

from .utils import run_bam_filter, normalize_whitespaces, run_samtools_get_body

BAM_FILTER_EXE = "bam-filter"
BAM_FILTER_DESC = (
    "Program to filter BAM files after Pacbio sequencing. "
    "Different filters can be applied on demand (by default all the "
    "filters are disabled). "
    "The order in which the filters are applied is: "
    "1) remove rows with len of DNA sequence under some threshold; "
    "2) take only molecules with a minimum number of subreads; "
    "3) choose molecules with sequencing quality above some threshold; "
    "and "
    "4) choose mapping. "
)

EXPECTED_OPTIONS_HELP_MSGS = [
    ("-l NUM, --min-dna-seq-length NUM minimum length of DNA sequence "
     "to be kept (default: 0)"),
    ("-r NUM, --min-subreads-per-molecule NUM "
     "minimum number of subreads per molecule to keep it (default: 1)"),
    ("-q NUM, --quality-threshold NUM "
     "quality threshold of the sample. Between 0 (the lowest) and 255 "
     "(the highest) (default: 0)"),
    ("-m MAPPING [MAPPING ...], --mappings MAPPING [MAPPING ...] "
     "keep only the requested (space separated) list of mappings "
     "(default: keep all)"),
    ("-R NUM, --min-relative-mapping-ratio NUM "
     "minimum ratio (amount of found wanted mappings/all mappings "
     "present) in order to keep the data point (default: take all)"),
    ("-v, --verbose"),
    "--version show program's version number and exit",
]


class TestCaseTryBamFilter:
    """FT for the features that are expected when one tries
    'bam-filter' naively for the first time.
    """
    def test_expected_message_and_return_code_with_no_arg(self):
        # Nathan needs to filter the bam files before running a single
        # molecule analysis. He found that the package comes with a
        # little utility that precisely seems to filter out unwanted
        # data from bam filters.
        # The name of the program is 'bam-filter'. So here he goes to
        # run it just to see what happens:
        with run_bam_filter() as result:
            # he does so and he sees some clarifying error message:
            expected = [_.format(exe=BAM_FILTER_EXE) for _ in (
                "usage: {exe} [-h] [-l NUM] [-r NUM] [-q NUM]",
                "[-m MAPPING [MAPPING ...]] [-R NUM] [-v] [--version]",
                "{exe}: error: the following arguments are required:",
            )]
            for e in expected:
                assert e in normalize_whitespaces(result.stderr.decode())
            # and it returns an error code to the terminal:
            assert result.returncode != 0

    def test_expected_message_and_return_code_with_help(self):
        # Ok, ok, he got it; he needs to call it with -h:
        with run_bam_filter("-h") as help_res:
            # and, he gets a very informative message about its usage. Great!
            expected_help_msgs = [
                normalize_whitespaces(BAM_FILTER_DESC)
            ] + EXPECTED_OPTIONS_HELP_MSGS
            help_res_normalized = normalize_whitespaces(
                help_res.stdout.decode())
            for expected_help in expected_help_msgs:
                assert expected_help in help_res_normalized
            # BTW, the returned code is not an error anymore:
            help_res.check_returncode()

    def test_version_option(self):
        # Nathan is curious about the version of the program he's using.
        with run_bam_filter("--version") as version_res:
            version = version_res.stdout.decode().split(".")
            for i in version:
                int(i)


class TestCaseHappyPathBamFilter:
    """FT to check behaviour of happy path cases with different options.
    """
    def check_bam_filter_with_bam_and_expected_results(
            self, bam, result, *options):
        cmd = (bam,)+options
        with run_bam_filter(*cmd) as cmd_result:
            clean_stdout = normalize_whitespaces(cmd_result.stdout.decode())
            clean_stderr = normalize_whitespaces(cmd_result.stderr.decode())
            output = clean_stdout+clean_stderr
            # and he finds no error:
            for error_indicator in ("error", "critical"):
                assert error_indicator not in output.lower()
            assert len(clean_stdout) == 0
            # and the return code of the program is 0, which reassures him:
            cmd_result.check_returncode()
        # he sees that a new file has been created:
        expected_file_name = bam.parent/("parsed."+bam.name)
        assert expected_file_name.exists()
        # But he realizes now that since he didn't pass any option to
        # the filtering program, actually the binary data contained in the
        # new file should be exactly the same as the original contains:
        with run_samtools_get_body(str(expected_file_name)) as new_bam:
            assert result.read() == new_bam.stdout.decode()

    def test_run_with_default_options(self, bam_file_mol_col_24):
        # Nathan chooses a test BAM file to try the bam-filter tool.
        # he goes to a newly created directory, copies the file there,
        # and he runs the program on it:
        bam = bam_file_mol_col_24["in"]
        text = bam_file_mol_col_24["in-text"]
        self.check_bam_filter_with_bam_and_expected_results(bam, text)
        # and indeed they are! But what happens if he runs a filter?
        # He is eager to test this...

    def test_run_with_minimum_dna_seq_len(self, bam_file_mol_col_24):
        # He wants to filter out now short DNA sequences. So he goes
        # again to the newly created directory, copies the files there,
        # and he runs the program on it but now with the proper filter:
        bam = bam_file_mol_col_24["in"]
        text = bam_file_mol_col_24["dna1500"]
        self.check_bam_filter_with_bam_and_expected_results(
            bam, text, "-l", "1500")
        # and indeed they are! But what happens if he adds a filter?
        # He is eager to test this...

    def test_run_with_min_reps_per_molecule(
            self, bam_file_mol_col_24, bam_file_mol_col_19):
        # He wants to filter out now molecules with a low number of subreads.
        # So he goes again to the newly created directory, copies the files
        # there, and he runs the program on it but now with the proper filter:
        bam = bam_file_mol_col_24["in"]
        text = bam_file_mol_col_24["subreads100"]
        self.check_bam_filter_with_bam_and_expected_results(
            bam, text, "-r", "100")
        # and indeed they are! What if he tries it with a new file with the
        # molecule id in column 19?
        bam = bam_file_mol_col_19["in"]
        text = bam_file_mol_col_19["subreads400"]
        self.check_bam_filter_with_bam_and_expected_results(
            bam, text, "-r", "400")
        # He is eager to use this in production...
        # But what happens if he adds a filter?

    def test_run_with_quality_threshold(self, bam_file_mol_col_24):
        # He wants to filter out now subreads with a low quality.
        # So he goes again to the newly created directory, copies the files
        # there, and he runs the program on it but now with the proper filter:
        bam = bam_file_mol_col_24["in"]
        text = bam_file_mol_col_24["quality254"]
        self.check_bam_filter_with_bam_and_expected_results(
            bam, text, "-q", "254")
        # and indeed they are! But what happens if he adds a filter?
        # He is eager to test this...

    def test_run_with_mappings(self, bam_file_mol_col_24, bam_file_mol_col_19):
        # He wants to keep only wished mappings.
        # So he goes again to the newly created directory, copies the files
        # there, and he runs the program on it but now with the proper filter:
        bam = bam_file_mol_col_24["in"]
        text = bam_file_mol_col_24["mappings256"]
        self.check_bam_filter_with_bam_and_expected_results(
            bam, text, "-m", "256")
        # and indeed they are! But what happens if he adds a filter?
        # But, what if he wants more than one mapping?
        text = bam_file_mol_col_24["mappings272+16"]
        self.check_bam_filter_with_bam_and_expected_results(
            bam, text, "-m", "16", "272")
        # Does this work also with files where the molecule is in a diff col?
        bam = bam_file_mol_col_19["in"]
        text = bam_file_mol_col_19["mappings256_ratio0.2"]
        self.check_bam_filter_with_bam_and_expected_results(
            bam, text, "-m", "256", "-R", "0.2")

    def test_run_with_min_relative_mapping_ratio(self, bam_file_mol_col_24):
        # And to give a nice twist, he would like to keep only some mappings,
        # *if* the ratio of their occurence is larger than some value.
        # So he goes again to the newly created directory, copies the files
        # there, and he runs the program on it but now with the proper filter:
        bam = bam_file_mol_col_24["in"]
        text = bam_file_mol_col_24["mappings256_ratio0.35"]
        self.check_bam_filter_with_bam_and_expected_results(
            bam, text, "-m", "256", "-R", "0.35")
        # and indeed they are! But what happens if he adds a filter?
        # But, what if he wants more than one mapping?
        text = bam_file_mol_col_24["mappings0+16_ratio0.4"]
        self.check_bam_filter_with_bam_and_expected_results(
            bam, text, "-m", "0", "16", "-R", "0.4")

    def test_run_with_combined_options(self, bam_file_mol_col_24):
        """The intent here is to write a test that combines several options to
        explicitly check that they don't collide.
        But maybe this test is not part of the happy path?
        """
        # Well, after all the tests, he would like to combine several filters
        # in one step. Would it work?
        bam = bam_file_mol_col_24["in"]
        text = bam_file_mol_col_24["mappings256_subreads70_dna1000"]
        self.check_bam_filter_with_bam_and_expected_results(
            bam, text, "-m", "256", "-r", "70", "-l", "1000")
        # Wonderful! It works!


class TestCaseErrors:
    def test_missing_file_passed_as_input(self, forbidden_bam):
        # Nathan passes by accident a wrong file name to bam-filter:
        cmd = (forbidden_bam,)
        with run_bam_filter(*cmd) as cmd_result:
            clean_stdout = normalize_whitespaces(cmd_result.stdout.decode())
            clean_stderr = normalize_whitespaces(cmd_result.stderr.decode())
            output = clean_stdout+clean_stderr
            # and he finds a critical error:
            assert "critical" in output.lower(), f"Actual output:\n{output}"
            assert str(forbidden_bam) in output
            assert len(clean_stdout) == 0
            # and the return code of the program is not 0, which is a clear
            # sign that there was a problem:
            assert cmd_result.returncode != 0
