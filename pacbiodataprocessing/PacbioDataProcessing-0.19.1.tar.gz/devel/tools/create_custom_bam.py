#######################################################################
#
# Copyright (C) 2021 David Palao
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

"""This script creates a custom BAM file from 11mols.bam with

* one molecule with subreads such that len(base pairs)<50
* one molecule with subreads having q!=254
* one molecule with <90% subreads having FLAG in {0, 16}
* one molecule with some subreads which FLAG is not in {0, 16}
* one molecule with less <20 subreads

"""

import sys
from collections import Counter

from pacbio_data_processing.bam import BamFile


STARTING_BAM = "../../tests/functional/data/11mols.bam"
OUTPUT_BAM = "12mols.bam"


def get_subreads_from_mol(bam, mol_id, num_subreads):
    count = 0
    for line in bam:
        if line.molecule_id == mol_id:
            if count < num_subreads:
                yield line
                count += 1
            else:
                break


def combine_lines(src, lines_to_add):
    src_mols = set(src.all_molecules)
    other_mols = set(lines_to_add.keys())
    already = set()
    for line in src:
        mol_id = line.molecule_id
        if mol_id not in already:
            print("[11mols] writing mol =", mol_id)
            yield from lines_to_add[mol_id]
            already.add(mol_id)
        yield line
    for mol_id in sorted(other_mols-already):
        print("[other] writing mol =", mol_id)
        yield from lines_to_add[mol_id]


def main():
    src = BamFile(STARTING_BAM)
    dst = BamFile(OUTPUT_BAM, "w")
    aux = BamFile(sys.argv[1])

    c = Counter()
    for subread in src:
        c[subread.molecule_id] += 1

    lines_to_add = {k: [] for k in c.keys()}
    
    lengths_11mols = set()
    for subread in src:
        lengths_11mols.add((len(subread.attr9), subread.molecule_id))

    line2 = src._BamLine(attr0=b'm54099_200714_225457/45744686/81000_81049', attr1=b'0', attr2=b'U00096.3', attr3=b'4138087', attr4=b'254', attr5=b'6S28=1D10=5S', attr6=b'*', attr7=b'0', attr8=b'0', attr9=b'AGCGAGATCTATTGGCAAACTACCGCATGGCTAAGGGCAAGCTACGGTT', attr10=b'!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!', attr11=b'cx:i:1', attr12=b'ip:B:C,2,19,3,8,18,9,1,3,41,11,37,4,39,11,22,2,15,15,14,17,6,9,14,8,0,0,4,37,21,10,1,17,61,1,3,19,13,0,1,5,22,5,5,20,46,2,16,9,14,3,1,0,87,5,24,0,17,6,8,32,5,3,41,5,2,11,14,8,1,2,0,14,3,6,22,0,11,7,18', attr13=b'np:i:1', attr14=b'pw:B:C,23,19,11,12,8,6,23,7,16,5,4,46,8,19,55,12,4,72,23,23,7,10,14,16,27,3,14,5,5,10,22,10,54,33,5,17,22,7,22,21,11,3,3,9,23,24,6,19,23,15,4,12,10,12,41,18,4,15,23,15,14,4,20,3,3,10,4,3,3,18,13,10,7,32,8,10,13,23,3', attr15=b'qe:i:80973', attr16=b'qs:i:80894', attr17=b'rq:f:0.8', attr18=b'sn:B:f,5.24822,9.164,6.75583,11.5777', zmw=b'zm:i:45744686', attr20=b'RG:Z:c984f559', attr21=b'AS:i:-285', attr22=b'NM:i:1')
    lines_to_add[b'45744686'].append(line2)

    line3 = src._BamLine(attr0=b'm54099_200714_225457/45744686/82000_82049', attr1=b'0', attr2=b'U00096.3', attr3=b'4138087', attr4=b'254', attr5=b'28=1D10=11S', attr6=b'*', attr7=b'0', attr8=b'0', attr9=b'AGCGAAATTCGGATCTATTGGCAAACTAGGCTAAGGGCAAGCTACGGTT', attr10=b'!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!', attr11=b'cx:i:1', attr12=b'ip:B:C,2,19,3,8,18,9,1,3,41,11,37,4,39,11,22,2,15,15,14,17,6,9,14,8,0,0,4,37,21,10,1,17,61,1,3,19,13,0,1,5,22,5,5,20,46,2,16,9,14,3,1,0,87,5,24,0,17,6,8,32,5,3,41,5,2,11,14,8,1,2,0,14,3,6,22,0,11,7,18', attr13=b'np:i:1', attr14=b'pw:B:C,23,19,11,12,8,6,23,7,16,5,4,46,8,19,55,12,4,72,23,23,7,10,14,16,27,3,14,5,5,10,22,10,54,33,5,17,22,7,22,21,11,3,3,9,23,24,6,19,23,15,4,12,10,12,41,18,4,15,23,15,14,4,20,3,3,10,4,3,3,18,13,10,7,32,8,10,13,23,3', attr15=b'qe:i:80973', attr16=b'qs:i:80894', attr17=b'rq:f:0.8', attr18=b'sn:B:f,5.24822,9.164,6.75583,11.5777', zmw=b'zm:i:45744686', attr20=b'RG:Z:c984f559', attr21=b'AS:i:-285', attr22=b'NM:i:1')
    lines_to_add[b'45744686'].append(line3)
    
    line4 = src._BamLine(attr0=b'm54099_200714_225457/45744686/83894_83973', attr1=b'0', attr2=b'U00096.3', attr3=b'4138087', attr4=b'240', attr5=b'11S38=1D20=10S', attr6=b'*', attr7=b'0', attr8=b'0', attr9=b'CGCCGGGACATCTTCTTTAATATCCAGTTGAGCGAGAGTTATTGGCAAACTACCGCATGGCTAAGGGCAAGCTACGGTT', attr10=b'!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!', attr11=b'cx:i:1', attr12=b'ip:B:C,2,19,3,8,18,9,1,3,41,11,37,4,39,11,22,2,15,15,14,17,6,9,14,8,0,0,4,37,21,10,1,17,61,1,3,19,13,0,1,5,22,5,5,20,46,2,16,9,14,3,1,0,87,5,24,0,17,6,8,32,5,3,41,5,2,11,14,8,1,2,0,14,3,6,22,0,11,7,18', attr13=b'np:i:1', attr14=b'pw:B:C,23,19,11,12,8,6,23,7,16,5,4,46,8,19,55,12,4,72,23,23,7,10,14,16,27,3,14,5,5,10,22,10,54,33,5,17,22,7,22,21,11,3,3,9,23,24,6,19,23,15,4,12,10,12,41,18,4,15,23,15,14,4,20,3,3,10,4,3,3,18,13,10,7,32,8,10,13,23,3', attr15=b'qe:i:80973', attr16=b'qs:i:80894', attr17=b'rq:f:0.8', attr18=b'sn:B:f,5.24822,9.164,6.75583,11.5777', zmw=b'zm:i:45744686', attr20=b'RG:Z:c984f559', attr21=b'AS:i:-285', attr22=b'NM:i:1')
    line5 = src._BamLine(attr0=b'm54099_200714_225457/45744686/84894_84973', attr1=b'0', attr2=b'U00096.3', attr3=b'4138087', attr4=b'200', attr5=b'11S38=1D20=10S', attr6=b'*', attr7=b'0', attr8=b'0', attr9=b'CGCCGGGACATCTTCTTTAATATCCAGTTGAGCGAGAGTTATTGGCAAACTACCGCATGGCTAAGGGCAAGCTACGGTT', attr10=b'!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!', attr11=b'cx:i:1', attr12=b'ip:B:C,2,19,3,8,18,9,1,3,41,11,37,4,39,11,22,2,15,15,14,17,6,9,14,8,0,0,4,37,21,10,1,17,61,1,3,19,13,0,1,5,22,5,5,20,46,2,16,9,14,3,1,0,87,5,24,0,17,6,8,32,5,3,41,5,2,11,14,8,1,2,0,14,3,6,22,0,11,7,18', attr13=b'np:i:1', attr14=b'pw:B:C,23,19,11,12,8,6,23,7,16,5,4,46,8,19,55,12,4,72,23,23,7,10,14,16,27,3,14,5,5,10,22,10,54,33,5,17,22,7,22,21,11,3,3,9,23,24,6,19,23,15,4,12,10,12,41,18,4,15,23,15,14,4,20,3,3,10,4,3,3,18,13,10,7,32,8,10,13,23,3', attr15=b'qe:i:80973', attr16=b'qs:i:80894', attr17=b'rq:f:0.8', attr18=b'sn:B:f,5.24822,9.164,6.75583,11.5777', zmw=b'zm:i:45744686', attr20=b'RG:Z:c984f559', attr21=b'AS:i:-285', attr22=b'NM:i:1')
    lines_to_add[b'45744686'].append(line4)
    lines_to_add[b'45744686'].append(line5)

    # one molecule with <90% subreads having FLAG in {0, 16}:
    new_lines = []
    newmol = b"9900000"
    offset = 1
    for line in src:
        if line.molecule_id == b'28836053':
            newattr0 = line.attr0.split(b"/")
            poss = newattr0[-1].split(b"_")
            poss = b"_".join([(f"{offset}").encode()+_ for _ in poss])
            newattr0 = b"/".join(newattr0[:-2]+[newmol, poss])

            if (line.attr1 == b"16") and (offset > 1):
                attr1 = b"254"
            else:
                attr1 = line.attr1
            zmw = b"zm:i:"+newmol
            t = (newattr0, attr1)+line[2:19]+(zmw,)+line[20:]
            new_lines.append(src._BamLine(*t))
            offset += 1
    lines_to_add[newmol] = new_lines

    # one molecule with some subreads which FLAG is not in {0, 16}:
    for line in src:
        offset = 1
        if line.molecule_id == b"72352689":
            newattr0 = line.attr0.split(b"/")
            poss = newattr0[-1].split(b"_")
            poss = b"_".join([(f"{offset}").encode()+_ for _ in poss])
            newattr0 = b"/".join(newattr0[:-1]+[poss])

            attr1 = line.attr1
            if (offset%13) == 0:
                if attr1 == b"0":
                    attr1 = b"254"
                elif attr1 == b"16":
                    attr1 = b"272"
            t = (newattr0, attr1) + line[2:]
            lines_to_add[b"72352689"].append(src._BamLine(*t))
            offset += 1

    # one molecule with less <20 subreads:
    short_mol = b'4391567'
    lines_to_add[short_mol] = list(
        get_subreads_from_mol(aux, short_mol, 19)
    )

    for mol_id, lines in lines_to_add.items():
        print(f"{mol_id} -> {len(lines)} lines")

    new_body = combine_lines(src, lines_to_add)
    dst.write(header=src.header, body=new_body)


if __name__ == "__main__":
    sys.exit(main())
