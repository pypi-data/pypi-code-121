#!/bin/env python

#######################################################################
#
# Copyright (C) 2021 David Palao
#
# This file is part of PacBio data processing.
#
#  PacBio data processing is free software: you can redistribute it and/or modify
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
#  along with PacBio data processing.  If not, see <http://www.gnu.org/licenses/>.
#
#######################################################################

import sys
from difflib import SequenceMatcher
import re
import statistics
from collections import Counter

from pacbio_data_processing.bam_utils import gen_body

CIGAR_SYMBOLS = "=IDSXH"

def parse_cigar(cigar):
    """The symbols mean:
    = -- equal
    X -- mismatch
    I -- insertion
    S -- soft clip (??)
    H -- hard clip (??)

    """
    return re.findall(rf"\d+[{CIGAR_SYMBOLS}]", cigar)
    return m.groups()

        
def compare_seq(query, ref, cigar):
    s = SequenceMatcher(None, query, ref)


class Cigar:
    def __init__(self, incigar):
        self._incigar = str(incigar)
        
def analyze_cigars(cigars, sequences_per_molecule, len_th=100):
    results = {}
    lines_per_mol = Counter()
    shortest_cigars = Counter()
    cigars_per_line = Counter()
    shortest_cigars_seq_len_cut = Counter()
    
    for mol_id, cigar_list in cigars.items():
        lines_per_mol[len(cigar_list)] += 1
        shortest_cigars[min(len(cigar) for cigar in cigar_list)] += 1
        sequences_list = sequences_per_molecule[mol_id]
        cigar_list_len_cut = []
        for cigar, seq in zip(cigar_list, sequences_list):
            if len(seq) >= len_th:
                cigar_list_len_cut.append(cigar)
        try:
            shortest_cigars_seq_len_cut[min(len(cigar) for cigar in cigar_list_len_cut)] += 1
        except ValueError:
            pass
        for cigar in cigar_list:
            cigars_per_line[len(cigar)] += 1
    results["number of molecules"] = len(cigars)
    results["number of lines/cigars"] = sum(nc*nl for nc, nl in lines_per_mol.items())
    for cilen in sorted(cigars_per_line.keys()):
        num = cigars_per_line[cilen]
        results[f"number of cigars of len {cilen}"] = num
    for cilen, count in sorted(shortest_cigars.items()):
        results[f"number of molecules which shortest cigar has len of {cilen}"] = count
    for cilen, count in sorted(shortest_cigars_seq_len_cut.items()):
        results[f"number of molecules which shortest cigar has len of {cilen}, and len(DNA)>={len_th}"] = count
    return results


if __name__ == "__main__":
    print(" ".join(sys.argv))
    print("."*50)
    bam = sys.argv[1]
    ref = sys.argv[2]

    with open(ref) as reff:
        reff.readline()
        full_reference = reff.read().replace("\n", "")

    ratios = []
    matching_per_molecule = {}
    cigars = {}
    sequences = {}
    
    for bam_line in gen_body(bam):
        pos = int(bam_line[3].decode())-1
        mol_id = bam_line[16].decode()
        query = bam_line[9].decode()
        rq = bam_line[14].decode().split(":")[-1]
        cigar = bam_line[5].decode()
        cigar_split = parse_cigar(cigar)
        cigar_list = cigars.setdefault(mol_id, [])
        cigar_list.append(cigar_split)

        sequences_per_molecule = sequences.setdefault(mol_id, [])
        sequences_per_molecule.append(query)
        
        ref = full_reference[pos:pos+len(query)]

        s = SequenceMatcher(None, query, ref)
        ratio = s.ratio()
        ratios.append(ratio)

        mmol = matching_per_molecule.setdefault(mol_id, [])
        mmol.append(ratio)
        
        print(f"[mol ID] {mol_id}")
        print(cigar, "->", cigar_split, f"(similarity ratio: {ratio}); rq={rq}")
        for op in s.get_opcodes():
            print(" ", op)
        print(query)
        print(ref)
        print()

    nbam_lines = len(ratios)
    full_matches = sum(1 for _ in ratios if _==1.0)
    above_66 = sum(1 for _ in ratios if _>=.66)
    below_50 = sum(1 for _ in ratios if _<=.5)
    
    rel_full_matches = 100*full_matches/nbam_lines
    rel_above_66 = 100*above_66/nbam_lines
    rel_below_50 = 100*below_50/nbam_lines

    num_mols = len(matching_per_molecule)
    num_mols_with_full_matching = 0
    num_mols_above_80 = 0
    num_mols_above_90 = 0
    num_mols_above_95 = 0
    for mol_id, ratios in matching_per_molecule.items():
        if 1.0 in ratios:
            num_mols_with_full_matching += 1
        max_match = max(ratios)
        if max_match >= 0.8:
            num_mols_above_80 += 1
        if max_match >= 0.9:
            num_mols_above_90 += 1
        if max_match >= 0.95:
            num_mols_above_95 += 1

    stats = analyze_cigars(cigars, sequences)
    
    print("Total number of molecules:", num_mols)
    print("Total lines:", nbam_lines)
    print("---")
    print("full match:", full_matches, f"({rel_full_matches} %)")
    print("above 66% matching:", above_66, f"({rel_above_66} %)")
    print("below 50% matching:", below_50, f"({rel_below_50} %)")
    print("ratio of molecules with full matching:", 100*num_mols_with_full_matching/num_mols, "%")
    print("ratio of molecules 80% matching:", 100*num_mols_above_80/num_mols, "%")
    print("ratio of molecules 90% matching:", 100*num_mols_above_90/num_mols, "%")
    print("ratio of molecules 95% matching:", 100*num_mols_above_95/num_mols, "%")

    print("---")
    print("Cigar summary:\n")
    for msg, value in stats.items():
        print(f" {msg}: {value}")
