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

SUMMARY_REPORT_HTML_TEMPLATE = """<!DOCTYPE html>
<html>
  <head>
{style}
    <title>sm-analysis · summary report</title>

  </head>

  <body>
    <h1>Summary report: Single Molecule Methylation Analysis</h1>

    <h2>Overview</h2>

    <table>
      <tr>
	<td>PacBio Data Processing version</td>
	<td>{version}</td>
      </tr>
      <tr>
	<td>Date</td>
	<td>{when}</td>
      </tr>
      <tr>
	<td>Program name</td>
	<td>{program}</td>
      </tr>
      <tr>
	<td>Program options</td>
	<td>{clos}</td>
      </tr>
      <tr>
	<td>Hostname</td>
	<td>{hostname}</td>
      </tr>
    </table>
    <h2>Result filenames</h2>

    <table>
      <tr>
	<td>Methylation report</td>
	<td><a href="{methylation_report}">{methylation_report}</a></td>
      </tr>
      <tr>
	<td>Raw detections</td>
	<td><a href="{raw_detections}">{raw_detections}</a></td>
      </tr>
      <tr>
	<td>Joint <a href="https://github.com/The-Sequence-Ontology/Specifications/blob/master/gff3.md">GFF</a>s</td>
	<td><a href="{gff_result}">{gff_result}</a></td>
      </tr>
    </table>

    <h2>Input files</h2>

    <h3 id="input bam">BAM File</h3>

    <table>
      <tr>
	<td>File name</td>
	<td>{input_bam}</td>
      </tr>
      <tr>
	<td>Size (bytes)</td>
	<td>{input_bam_size}</td>
      </tr>
      <tr>
	<td>MD5 checksum (full)</td>
	<td>{full_md5sum}</td>
      </tr>
      <tr>
	<td>MD5 checksum (body)</td>
	<td>{body_md5sum}</td>
      </tr>
    </table>

    <h3 id="reference">Reference</h3>

    <table>
      <tr>
	<td>File name</td>
	<td>{input_reference}</td>
      </tr>
      <tr>
	<td>Reference name</td>
	<td>{reference_name}</td>
      </tr>
      <tr>
	<td>Size (base pairs)</td>
	<td>{reference_base_pairs}</td>
      </tr>
      <tr>
	<td>MD5 checksum (fully capitalized string)</td>
	<td>{reference_md5sum}</td>
      </tr>
    </table>

    <p class="top-large bottom-large">The following facts were found during the analysis of the above mentioned <a href="#input bam">BAM file</a> and <a href="#reference">reference</a>:</p>

    <h2>Molecules/subreads</h2>

    <table>
      <tr>
	<th></th>
	<th>number of molecules</th>
	<th>number of subreads</th>
      </tr>
      <tr>
	<td>Initial</td>
	<td>{mols_ini}</td>
	<td>{subreads_ini}</td>
      </tr>
      <tr>
	<td>Used in aligned CCS BAM</td>
	<td>{mols_used_in_aligned_ccs} ({perc_mols_used_in_aligned_ccs} %)</td>
	<td>{subreads_used_in_aligned_ccs} ({perc_subreads_used_in_aligned_ccs} %)</td>
      </tr>
      <tr>
	<td>DNA mismatch discards</td>
	<td>{mols_dna_mismatches} ({perc_mols_dna_mismatches} %)</td>
	<td>{subreads_dna_mismatches} ({perc_subreads_dna_mismatches} %)</td>
      </tr>
      <tr>
	<td>Filtered out</td>
	<td>{filtered_out_mols} ({perc_filtered_out_mols} %)</td>
	<td>{filtered_out_subreads} ({perc_filtered_out_subreads} %)</td>
      </tr>
      <tr>
	<td>In methylation report...</td>
	<td>{mols_in_meth_report} ({perc_mols_in_meth_report} %)</td>
	<td>{subreads_in_meth_report} ({perc_subreads_in_meth_report} %)</td>
      </tr>
      <tr>
	<td class="text-center">...only with GATCs</td>
	<td>{mols_in_meth_report_with_gatcs} ({perc_mols_in_meth_report_with_gatcs} %)</td>
	<td>{subreads_in_meth_report_with_gatcs} ({perc_subreads_in_meth_report_with_gatcs} %)</td>
      </tr>
      <tr>
	<td class="text-center">...only without GATCs</td>
	<td>{mols_in_meth_report_without_gatcs} ({perc_mols_in_meth_report_without_gatcs} %)</td>
	<td>{subreads_in_meth_report_without_gatcs} ({perc_subreads_in_meth_report_without_gatcs} %)</td>
      </tr>
    </table>

    <p> <img src="{molecule_type_bars}" alt="count of molecule types"> </p>
    <p> <img src="{molecule_len_histogram}" alt="molecule length histogram"> </p>

    <h2>Sequencing Position Coverage</h2>

    <p>Note: it is understood that a position is <em>covered</em> if we have confidence that it has been correctly identified. The aligned CCS version of the input BAM is used for that.</p>

    <table>
      <tr>
	<td>Number of base pairs in reference</td>
	<td>{reference_base_pairs}</td>
      </tr>
      <tr>
	<td>Positions covered by molecules in the BAM file</td>
	<td>{all_positions_in_bam} ({perc_all_positions_in_bam} %)</td>
      </tr>
      <tr>
	<td>Positions NOT covered by molecules in the BAM file</td>
	<td>{all_positions_not_in_bam} ({perc_all_positions_not_in_bam} %)</td>
      </tr>
      <tr>
	<td>Positions covered by molecules in the methylation report</td>
	<td>{all_positions_in_meth} ({perc_all_positions_in_meth} %)</td>
      </tr>
      <tr>
	<td>Positions NOT covered by molecules in the methylation report</td>
	<td>{all_positions_not_in_meth} ({perc_all_positions_not_in_meth} %)</td>
      </tr>
    </table>

    <p> <img src="{position_coverage_bars}" alt="Position coverage in BAM file and in Methylation report"> </p>
    <p> <img src="{position_coverage_history}" alt="Sequencing position coverage history"> </p>

    <h2>GATCs</h2>

    <table>
      <tr>
	<td>Total number of GATCs in reference</td>
	<td>{total_gatcs_in_ref}</td>
      </tr>
      <tr>
	<td>Number of GATCs identified in the BAM file</td>
	<td>{all_gatcs_identified_in_bam} ({perc_all_gatcs_identified_in_bam} %)</td>
      </tr>
      <tr>
	<td>Number of GATCs NOT identified in the BAM file</td>
	<td>{all_gatcs_not_identified_in_bam} ({perc_all_gatcs_not_identified_in_bam} %)</td>
      </tr>
      <tr>
	<td>Number of GATCs in methylation report</td>
	<td>{all_gatcs_in_meth} ({perc_all_gatcs_in_meth} %)</td>
      </tr>
      <tr>
	<td>Number of GATCs NOT in methylation report</td>
	<td>{all_gatcs_not_in_meth} ({perc_all_gatcs_not_in_meth} %)</td>
      </tr>
    </table>

    <p> <img src="{gatc_coverage_bars}" alt="GATC coverage"> </p>

    <h3>Methylations</h3>

    <p>In this section there are some global statistics concerning <em>individual</em> methylations.</p>

    <table>
      <tr>
	<td>Total number of GATCs in all the analyzed molecules</td>
	<td>{max_possible_methylations}</td>
      </tr>
      <tr>
	<td>Fully methylated</td>
	<td>{fully_methylated_gatcs} ({fully_methylated_gatcs_wrt_meth} %)</td>
      </tr>
      <tr>
	<td>Fully unmethylated</td>
	<td>{fully_unmethylated_gatcs} ({fully_unmethylated_gatcs_wrt_meth} %)</td>
      </tr>
      <tr>
	<td>Hemi-methylated...</td>
	<td>{hemi_methylated_gatcs} ({hemi_methylated_gatcs_wrt_meth} %)</td>
      </tr>
      <tr>
	<td class="text-center">...only in '+' strand</td>
	<td>{hemi_plus_methylated_gatcs} ({hemi_plus_methylated_gatcs_wrt_meth} %)</td>
      </tr>
      <tr>
	<td class="text-center">...only in '-' strand</td>
	<td>{hemi_minus_methylated_gatcs} ({hemi_minus_methylated_gatcs_wrt_meth} %)</td>
      </tr>
    </table>

    <p> <img src="{meth_type_bars}" alt="count of methylation types"> </p>

  </body>
</html>
"""
