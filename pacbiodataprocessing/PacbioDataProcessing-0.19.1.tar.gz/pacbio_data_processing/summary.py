#######################################################################
#
# Copyright (C) 2022 David Palao
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

from datetime import datetime
import sys
import socket
import csv
from pathlib import Path
from collections import defaultdict
from collections.abc import Mapping
import math

import pandas

from . import __version__ as VERSION
from .constants import SM_ANALYSIS_EXE, DNA_SEQ_COLUMN, PI_SHIFTED_VARIANT
from .templates import SUMMARY_REPORT_HTML_TEMPLATE
from .bam import BamFile
from .utils import DNASeq, find_gatc_positions, shift_me_back
from .cigar import Cigar
from .plots import make_barsplot, make_rolling_history, make_multi_histogram


SET_RO_ATTRIBUTE_ERR_MSG = "attribute '{}' cannot be set directly"

DEFAULT_STYLE = """    <style>
      table {
	    font-family: arial, sans-serif;
	    border-collapse: collapse;
	    width: 50%;
      }

      img {
	    width: 50%;
      }

      td, th {
	    border: 1px solid #dddddd;
	    text-align: left;
	    padding: 8px;
      }

      tr:nth-child(even) {
	    background-color: #dddddd;
      }
      tr:hover{
	    background-color: #D6EEEE;
      }
      .bottom-large {
	    margin-bottom: 1cm;
      }
      .top-large {
	    margin-top: 1cm;
      }
      .text-center {
	    text-align: center;
      }

    </style>

"""


class SimpleAttribute:
    """The base class of all other descriptor managed attributes
    of ``SummaryReport``.
    It is a wrapper around the ``_data`` dictionary of the instance
    owning this attribute.
    """
    def __init__(self, name=None):
        self.name = name

    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return instance._data[self.name]

    def __set__(self, instance, value):
        instance._data[self.name] = value


class MethylationReport(SimpleAttribute):
    def __set__(self, instance, value):
        super().__set__(instance, value)
        # refactor idea: use Counter
        # refactor idea: use properties or methods
        mols_in_meth_report = 0
        subreads_in_meth_report = 0
        mols_in_meth_report_with_gatcs = 0
        subreads_in_meth_report_with_gatcs = 0
        mols_in_meth_report_without_gatcs = 0
        subreads_in_meth_report_without_gatcs = 0
        max_possible_methylations = 0
        fully_methylated_gatcs = 0
        fully_unmethylated_gatcs = 0
        hemi_plus_methylated_gatcs = 0
        hemi_minus_methylated_gatcs = 0
        positions_in_meth = set()
        gatc_positions_in_meth = set()
        with open(value, newline="") as csvfile:
            reader = csv.reader(csvfile, delimiter=";")
            next(reader)
            for line in reader:
                mols_in_meth_report += 1
                subreads = int(line[5])+int(line[6])
                subreads_in_meth_report += subreads
                num_gatcs = int(line[10])
                max_possible_methylations += num_gatcs
                states = line[13]
                start = int(line[2])-1
                end = int(line[3])
                # if end < start (molecule crossing origin) the gatcs are
                # not counted. FIX IT.
                positions_in_meth |= set(range(start, end))
                if num_gatcs == 0:
                    mols_in_meth_report_without_gatcs += 1
                    subreads_in_meth_report_without_gatcs += subreads
                else:
                    mols_in_meth_report_with_gatcs += 1
                    subreads_in_meth_report_with_gatcs += subreads
                    gatc_positions_in_meth |= {
                        int(_) for _ in line[11].split(",")}
                fully_methylated_gatcs += states.count("f")
                fully_unmethylated_gatcs += states.count("0")
                hemi_plus_methylated_gatcs += states.count("+")
                hemi_minus_methylated_gatcs += states.count("-")

        instance._data["mols_in_meth_report"] = mols_in_meth_report
        instance._data["subreads_in_meth_report"] = subreads_in_meth_report
        instance._data["mols_in_meth_report_with_gatcs"] = (
            mols_in_meth_report_with_gatcs)
        instance._data["subreads_in_meth_report_with_gatcs"] = (
            subreads_in_meth_report_with_gatcs)
        instance._data["mols_in_meth_report_without_gatcs"] = (
            mols_in_meth_report_without_gatcs)
        instance._data["subreads_in_meth_report_without_gatcs"] = (
            subreads_in_meth_report_without_gatcs)
        all_gatcs_in_meth = len(gatc_positions_in_meth)
        instance._data["all_gatcs_in_meth"] = all_gatcs_in_meth
        all_gatcs_not_in_meth = instance.total_gatcs_in_ref-all_gatcs_in_meth
        instance._data["all_gatcs_not_in_meth"] = all_gatcs_not_in_meth
        instance._data["max_possible_methylations"] = max_possible_methylations
        instance._data["fully_methylated_gatcs"] = fully_methylated_gatcs
        instance._data["fully_unmethylated_gatcs"] = fully_unmethylated_gatcs
        hemi_methylated_gatcs = (
            hemi_plus_methylated_gatcs+hemi_minus_methylated_gatcs)
        instance._data["hemi_methylated_gatcs"] = hemi_methylated_gatcs
        instance._data["hemi_plus_methylated_gatcs"] = (
            hemi_plus_methylated_gatcs)
        instance._data["hemi_minus_methylated_gatcs"] = (
            hemi_minus_methylated_gatcs)
        all_positions_in_meth = len(positions_in_meth)
        instance._data["all_positions_in_meth"] = all_positions_in_meth
        all_positions_not_in_meth = (
            instance.reference_base_pairs - all_positions_in_meth)
        instance._data["all_positions_not_in_meth"] = all_positions_not_in_meth
        instance.switch_on(self.name)


class ROAttribute(SimpleAttribute):
    def __set__(self, instance, value):
        msg = SET_RO_ATTRIBUTE_ERR_MSG.format(self.name)
        raise AttributeError(msg)


class MolsSetAttribute(SimpleAttribute):
    def __set__(self, instance, value):
        self._set = value
        result = len(value)
        instance._data[self.name] = result
        subreads_name = self.name.replace("mols", "subreads")
        num_subreads = 0
        for mol in instance.bam:
            if int(mol.molecule_id) in self._set:
                num_subreads += 1
        instance._data[subreads_name] = num_subreads
        instance.switch_on(self.name)


class PercAttribute(ROAttribute):
    """From a given attribute in a SummaryReport instance s, the
    percentage is computed (wrt the value s.total_attr) and returned
    as str.
    """
    def __init__(self, total_attr, pref="perc_", suf="_wrt_meth", name=None):
        super().__init__(name)
        self.total_attr = total_attr
        self.pref = pref
        self.suf = suf

    def __get__(self, instance, owner):
        if instance is None:
            return self
        ref_attr = self.name.removeprefix(self.pref).removesuffix(self.suf)
        try:
            perc = 100*instance._data[ref_attr]/instance._data[self.total_attr]
        except ZeroDivisionError:
            result = "N/A"
        else:
            result = f"{perc:4.2f}"
        return result


class InputBamAttribute(SimpleAttribute):
    def __set__(self, instance, value):
        super().__set__(instance, value)
        bam = BamFile(value)
        instance._data["input_bam_size"] = bam.size_in_bytes
        instance._data["full_md5sum"] = bam.full_md5sum
        instance._data["body_md5sum"] = bam.md5sum_body
        instance._data["mols_ini"] = bam.num_molecules
        instance._data["subreads_ini"] = bam.num_subreads
        instance.bam = bam
        instance.switch_on(self.name)


class InputReferenceAttribute(SimpleAttribute):
    def __set__(self, instance, value):
        super().__set__(instance, value.fasta_name)
        instance._data["reference_name"] = value.description.strip()
        instance._data["reference_base_pairs"] = len(value)
        instance._data["reference_md5sum"] = value.md5sum
        instance._data["total_gatcs_in_ref"] = value.upper().count("GATC")
        instance.switch_on(self.name)


class AlignedCCSBamsAttribute(SimpleAttribute):
    # This attribute could be probably replaced by one attr containing
    # Molecule's computed is SingleMoleculeAnalysis...
    def __set__(self, instance, value):
        super().__set__(instance, value)
        positions = set()
        mols = set()
        gatc_positions = set()
        len_ref = instance.reference_base_pairs
        for variant, aligned_ccs in value.items():
            if aligned_ccs is None:
                continue
            bam = BamFile(aligned_ccs)
            for subread in bam:
                seq = subread[9].decode()
                N = len(seq)
                cigar = Cigar(subread[5].decode())
                mol_id = int(subread.molecule_id)
                pos = int(subread[3])-1
                if variant == PI_SHIFTED_VARIANT:
                    pos = shift_me_back(pos, len_ref)
                if cigar.number_pb_diffs == 0:
                    if mol_id not in mols:
                        mols.add(mol_id)
                        positions |= set(
                            [_%len_ref for _ in range(pos, pos+N)])
                        gatcs = find_gatc_positions(seq, offset=pos)
                        gatc_positions |= {_%len_ref for _ in gatcs}
        all_positions_in_bam = len(positions)
        instance._data["all_positions_in_bam"] = all_positions_in_bam
        all_positions_not_in_bam = (
            instance.reference_base_pairs-all_positions_in_bam)
        instance._data["all_positions_not_in_bam"] = all_positions_not_in_bam
        all_gatcs_identified_in_bam = len(gatc_positions)
        instance._data["all_gatcs_identified_in_bam"] = (
            all_gatcs_identified_in_bam)
        all_gatcs_not_identified_in_bam = (
            instance.total_gatcs_in_ref-len(gatc_positions))
        instance._data["all_gatcs_not_identified_in_bam"] = (
            all_gatcs_not_identified_in_bam)
        instance.switch_on(self.name)


class BarsPlotAttribute(ROAttribute):
    def __get__(self, instance, owner):
        if instance is None:
            return self
        if instance.ready_to_go(*self.dependency_names):
            filename = instance._data[self.name]
            data_dict = {}
            for main_key, subkeys in self.data_definition.items():
                data_dict[main_key] = []
                for subkey in subkeys:
                    try:
                        value = float(getattr(instance, subkey))
                    except ValueError:
                        value = math.nan
                    data_dict[main_key].append(value)
                # data_dict[main_key] = [
                #     float(getattr(instance, _)) for _ in subkeys]
            data = pandas.DataFrame(data_dict, index=self.index_labels)
            return data, self.title, filename


class HistoryPlotAttribute(ROAttribute):
    def __get__(self, instance, owner):
        if instance is None:
            return self
        if instance.ready_to_go(self.dependency_name):
            filename = instance._data[self.name]
            df = self.make_data_for_plot(instance)
            return df, self.title, filename, self.legend


class MoleculeTypeBarsPlot(BarsPlotAttribute):
    title = "Processed molecules and subreads"
    dependency_names = (
        "mols_used_in_aligned_ccs",
        "mols_dna_mismatches",
        "filtered_out_mols",
        "methylation_report"
    )
    data_definition = {
        'Used in aligned CCS': (
            "perc_mols_used_in_aligned_ccs",
            "perc_subreads_used_in_aligned_ccs"
        ),
        'Mismatch discards': (
            "perc_mols_dna_mismatches",
            "perc_subreads_dna_mismatches",
        ),
        'Filtered out': (
            "perc_filtered_out_mols",
            "perc_filtered_out_subreads",
        ),
        'In Methylation report with GATC': (
            "perc_mols_in_meth_report_with_gatcs",
            "perc_subreads_in_meth_report_with_gatcs",
        ),
        'In Methylation report without GATC': (
            "perc_mols_in_meth_report_without_gatcs",
            "perc_subreads_in_meth_report_without_gatcs",
        )
    }
    index_labels = ('Number of molecules (%)', 'Number of subreads (%)')


class PositionCoverageBarsPlot(BarsPlotAttribute):
    title = "Position coverage in BAM file and Methylation report"
    dependency_names = (
        "aligned_ccs_bam_files",
        "methylation_report"
    )
    data_definition = {
        'Positions covered by molecules in BAM file (%)': (
            "perc_all_positions_in_bam",
        ),
        'Positions NOT covered by molecules in BAM file (%)': (
            "perc_all_positions_not_in_bam",
        ),
        'Positions covered by molecules in methylation report (%)': (
            "perc_all_positions_in_meth",
        ),
        'Positions NOT covered by molecules in methylation report (%)': (
            "perc_all_positions_not_in_meth",
        )
    }
    index_labels = ("Percentage",)


class GATCCoverageBarsPlot(BarsPlotAttribute):
    title = "GATCs in BAM file and Methylation report"
    dependency_names = (
        "aligned_ccs_bam_files",
        "methylation_report"
    )
    data_definition = {
        'GATCs in BAM file (%)': ("perc_all_gatcs_identified_in_bam",),
        'GATCs NOT in BAM file (%)': ("perc_all_gatcs_not_identified_in_bam",),
        'GATCs in methylation report (%)': ("perc_all_gatcs_in_meth",),
        'GATCs NOT in methylation report (%)': ("perc_all_gatcs_not_in_meth",)
    }
    index_labels = ("Percentage",)


class MethTypeBarsPlot(BarsPlotAttribute):
    title = "Methylation types in methylation report"
    dependency_names = ("methylation_report",)
    data_definition = {
        'Fully methylated (%)': ("fully_methylated_gatcs_wrt_meth",),
        'Fully unmethylated (%)': ("fully_unmethylated_gatcs_wrt_meth",),
        'Hemi-methylated in + strand (%)': (
            "hemi_plus_methylated_gatcs_wrt_meth",),
        'Hemi-methylated in - strand (%)': (
            "hemi_minus_methylated_gatcs_wrt_meth",)
    }
    index_labels = ("Percentage",)


class MoleculeLenHistogram(HistoryPlotAttribute):
    dependency_name = "methylation_report"
    column_name = "len(molecule)"
    title = "Initial subreads and analyzed molecule length histogram"
    data_name = "length"
    labels = ("Initial subreads", "Analyzed molecules")
    legend = True
    #hue = "source"

    def make_data_for_plot(self, instance):
        series = []
        subreads = pandas.Series(
            [len(_[DNA_SEQ_COLUMN]) for _ in instance.bam], name=self.data_name
        )
        series.append(subreads)
        df = pandas.read_csv(
            getattr(instance, self.dependency_name), delimiter=";")
        mols = df[self.column_name]
        mols.name = self.data_name
        series.append(mols)
        return {k: v for k, v in zip(self.labels, series)}


class PositionCoverageHistory(HistoryPlotAttribute):
    dependency_name = "methylation_report"
    title = "Sequencing positions covered by analyzed molecules"
    start_column_name = "start of molecule"
    len_column_name = "len(molecule)"
    labels = ("Positions",)
    legend = False

    def make_data_for_plot(self, instance):
        pre_df = pandas.read_csv(
            instance._data[self.dependency_name], delimiter=';')
        starts = pre_df[self.start_column_name]
        lengths = pre_df[self.len_column_name]
        N = instance.reference_base_pairs
        coverage = {i: 0 for i in range(1, N+1)}
        for s, l in zip(starts, lengths):
            for j in range(s-1, s+l-1):
                position = 1+j%N
                coverage[position] += 1
        return coverage


class SummaryReport(Mapping):
    """Final summary report generated by ``sm-analysis`` initially
    intended for humans.

    This class has been crafted to carefully control its attributes.
    Data can be fed into the class by setting some attributes. That
    process triggers the generation of other attributes, that are
    typically *read-only*.

    After instantiating the class with the path to the input BAM and
    the dna sequence of the reference (instance of ``DNASeq``), one
    must set some attributes to be able to save the summary report::

      s = SummaryReport(bam_path, dnaseq)
      s.methylation_report = path_to_meth_report
      s.raw_detections = path_to_raw_detections_file
      s.gff_result = path_to_gff_result_file
      s.mols_dna_mismatches = {20, 49, ...} # set of ints
      s.filtered_out_mols = {22, 493, ...} # set of ints
      s.mols_used_in_aligned_ccs = {3, 67, ...} # set of ints
      s.aligned_ccs_bam_files = {
          'straight': aligned_ccs_path,
          'pi-shifted': pi_shifted_aligned_ccs_path
      }

    at this point all the necessary data is there and the report
    can be created::

      s.save('summary_whatever.html')
    """

    methylation_report = MethylationReport()
    raw_detections = SimpleAttribute()
    gff_result = SimpleAttribute()
    input_bam = InputBamAttribute()
    input_bam_size = ROAttribute()
    full_md5sum = ROAttribute()
    body_md5sum = ROAttribute()
    input_reference = InputReferenceAttribute()
    reference_name = ROAttribute()
    reference_base_pairs = ROAttribute()
    reference_md5sum = ROAttribute()
    mols_ini = ROAttribute()
    subreads_ini = ROAttribute()
    mols_dna_mismatches = MolsSetAttribute()
    perc_mols_dna_mismatches = PercAttribute(total_attr="mols_ini")
    subreads_dna_mismatches = ROAttribute()
    perc_subreads_dna_mismatches = PercAttribute(total_attr="subreads_ini")
    filtered_out_mols = MolsSetAttribute()
    perc_filtered_out_mols = PercAttribute(total_attr="mols_ini")
    filtered_out_subreads = ROAttribute()
    perc_filtered_out_subreads = PercAttribute(total_attr="subreads_ini")
    mols_in_meth_report = ROAttribute()
    perc_mols_in_meth_report = PercAttribute(total_attr="mols_ini")
    subreads_in_meth_report = ROAttribute()
    perc_subreads_in_meth_report = PercAttribute(total_attr="subreads_ini")
    mols_in_meth_report_with_gatcs = ROAttribute()
    perc_mols_in_meth_report_with_gatcs = PercAttribute(total_attr="mols_ini")
    subreads_in_meth_report_with_gatcs = ROAttribute()
    perc_subreads_in_meth_report_with_gatcs = PercAttribute(
        total_attr="subreads_ini")
    mols_in_meth_report_without_gatcs = ROAttribute()
    perc_mols_in_meth_report_without_gatcs = PercAttribute(
        total_attr="mols_ini")
    subreads_in_meth_report_without_gatcs = ROAttribute()
    perc_subreads_in_meth_report_without_gatcs = PercAttribute(
        total_attr="subreads_ini")
    mols_used_in_aligned_ccs = MolsSetAttribute()
    perc_mols_used_in_aligned_ccs = PercAttribute(total_attr="mols_ini")
    subreads_used_in_aligned_ccs = ROAttribute()
    perc_subreads_used_in_aligned_ccs = PercAttribute(
        total_attr="subreads_ini")
    aligned_ccs_bam_files = AlignedCCSBamsAttribute()
    all_positions_in_bam = ROAttribute()
    perc_all_positions_in_bam = PercAttribute(
        total_attr="reference_base_pairs")
    all_positions_not_in_bam = ROAttribute()
    perc_all_positions_not_in_bam = PercAttribute(
        total_attr="reference_base_pairs")
    all_positions_in_meth = ROAttribute()
    perc_all_positions_in_meth = PercAttribute(
        total_attr="reference_base_pairs")
    all_positions_not_in_meth = ROAttribute()
    perc_all_positions_not_in_meth = PercAttribute(
        total_attr="reference_base_pairs")
    total_gatcs_in_ref = ROAttribute()
    all_gatcs_identified_in_bam = ROAttribute()
    perc_all_gatcs_identified_in_bam = PercAttribute(
        total_attr="total_gatcs_in_ref")
    all_gatcs_not_identified_in_bam = ROAttribute()
    perc_all_gatcs_not_identified_in_bam = PercAttribute(
        total_attr="total_gatcs_in_ref")
    all_gatcs_in_meth = ROAttribute()
    perc_all_gatcs_in_meth = PercAttribute(total_attr="total_gatcs_in_ref")
    all_gatcs_not_in_meth = ROAttribute()
    perc_all_gatcs_not_in_meth = PercAttribute(total_attr="total_gatcs_in_ref")
    max_possible_methylations = ROAttribute()
    fully_methylated_gatcs = ROAttribute()
    fully_methylated_gatcs_wrt_meth = PercAttribute(
        total_attr="max_possible_methylations")
    fully_unmethylated_gatcs = ROAttribute()
    fully_unmethylated_gatcs_wrt_meth = PercAttribute(
        total_attr="max_possible_methylations")
    hemi_methylated_gatcs = ROAttribute()
    hemi_methylated_gatcs_wrt_meth = PercAttribute(
        total_attr="max_possible_methylations")
    hemi_plus_methylated_gatcs = ROAttribute()
    hemi_plus_methylated_gatcs_wrt_meth = PercAttribute(
        total_attr="max_possible_methylations")
    hemi_minus_methylated_gatcs = ROAttribute()
    hemi_minus_methylated_gatcs_wrt_meth = PercAttribute(
        total_attr="max_possible_methylations")

    molecule_type_bars = MoleculeTypeBarsPlot()
    molecule_len_histogram = MoleculeLenHistogram()
    position_coverage_bars = PositionCoverageBarsPlot()
    position_coverage_history = PositionCoverageHistory()
    gatc_coverage_bars = GATCCoverageBarsPlot()
    meth_type_bars = MethTypeBarsPlot()

    def __init__(self, bam_path, dnaseq):
        self._primary_attributes = defaultdict(lambda: False)
        self.figures_dir_name = "figures"
        self._data = {
            "style": DEFAULT_STYLE,
            "version": VERSION,
            "when": datetime.now().isoformat(timespec="minutes"),
            "program": SM_ANALYSIS_EXE,
            "clos": " ".join(sys.argv[1:]),
            "hostname": socket.gethostname(),
            "molecule_type_bars": (
                f"{self.figures_dir_name}/molecule_type_bars.png"),
            "molecule_len_histogram": (
                f"{self.figures_dir_name}/molecule_length_histogram.png"),
            "position_coverage_bars": (
                f"{self.figures_dir_name}/position_coverage_bars.png"),
            "position_coverage_history": (
                f"{self.figures_dir_name}/position_coverage_history.png"),
            "gatc_coverage_bars": (
                f"{self.figures_dir_name}/gatc_coverage_bars.png"),
            "meth_type_bars": (
                f"{self.figures_dir_name}/meth_type_bars.png"),
        }
        self._molecules_with_dna_mismatch = set()
        self.input_bam = bam_path
        self.input_reference = dnaseq
        Path(self.figures_dir_name).mkdir(exist_ok=True)

    @property
    def as_html(self):
        return SUMMARY_REPORT_HTML_TEMPLATE.format(**self)

    def save(self, filename):
        make_barsplot(*self.molecule_type_bars)
        make_multi_histogram(*self.molecule_len_histogram)
        make_barsplot(*self.position_coverage_bars)
        make_barsplot(*self.gatc_coverage_bars)
        make_rolling_history(*self.position_coverage_history)
        make_barsplot(*self.meth_type_bars)
        with open(filename, "w") as f:
            f.write(self.as_html)

    def switch_on(self, attribute):
        """Method used by descriptors to inform the instance of
        ``SummaryReport``that some computed attributes needed by
        the plots are already computed and usable.
        """
        self._primary_attributes[attribute] = True

    def ready_to_go(self, *attrs):
        """Method used to check if some attributes are already usable
        or not (in other words if they have been already set or not).
        """
        return all([self._primary_attributes[_] for _ in attrs])

    def __getitem__(self, item):
        """The items are fetched from either ``self._data``, or directly
        as attributes of ``self``. The priority is ``self._data``. For
        example::

          s = SummaryReport(...)
          s['temperature']

        will try to return ``s._data['temperature']``, and only if
        missing, ``s.temperature``.
        """
        try:
            value = self._data[item]
        except KeyError:
            try:
                value = getattr(self, item)
            except AttributeError as e:
                raise(KeyError(str(e)))
        return value

    def __iter__(self):
        return (self[key] for key in self.keys())

    def __len__(self):
        return len(self.keys())

    def keys(self):
        forbidden = {_ for _ in dir(self) if _.startswith("_")}
        forbidden |= {
            "as_html", "save", "switch_on", "ready_to_go",
            "keys", "values", "items"
        }
        methods = {_ for _ in dir(self) if "__call__" in dir(_)}
        descriptors = {_ for _ in dir(self) if _ not in forbidden}
        from_data = set(self._data.keys())
        return (descriptors|from_data)-methods
