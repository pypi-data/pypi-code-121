import gzip
from typing import List, BinaryIO, TextIO
import numpy as np
from .data_loaders import to_one_hot


def load_gzdata(filename, one_hot: bool = True):
    names: List[str]
    names, seqs = read_gzfasta(filename)
    if one_hot:
        seqs = to_one_hot(seqs)
    return names, seqs


def compress_file(filename):
    f: BinaryIO
    with open(filename, 'rb') as f:
        gzout: BinaryIO
        with open(filename + '.gz', 'wb') as gzout:
            b: bytes = gzip.compress(f.read())
            gzout.write(b)


def read_gzfasta(filepath, output_arr: bool = False, encoding: str = 'utf-8'):
    names: List[str] = []
    seqs = []
    seq: str = ''
    with gzip.open(filepath, 'rb') as fin:
        file_content: str = fin.read().decode(encoding)
        lines: List[str] = file_content.split('\n')
        line: str
        for line in lines:
            if line:
                if line[0] == '>':
                    if seq:
                        names.append(name)
                        if output_arr:
                            seqs.append(np.array(list(seq)))
                        else:
                            seqs.append(seq)
                    name: str = line[1:]
                    seq = ''
                else:
                    seq += line
            else:
                continue
        if seq:  # handle last seq in file
            names.append(name)
            if output_arr:
                seqs.append(np.array(list(seq)))
            else:
                seqs.append(seq)
    if output_arr:
        seqs = np.array(seqs)
    return names, seqs


def read_fasta(filepath, output_arr: bool = False):
    names: List[str] = []
    seqs = []
    seq: str = ''
    fin: TextIO
    with open(filepath, 'r') as fin:
        line: str
        for line in fin:
            if line[0] == '>':
                if seq:
                    names.append(name)
                    if output_arr:
                        seqs.append(np.array(list(seq)))
                    else:
                        seqs.append(seq)
                name: str = line.rstrip('\n')[1:]
                seq = ''
            else:
                seq += line.rstrip('\n')
        if seq:  # handle last seq in file
            names.append(name)
            if output_arr:
                seqs.append(np.array(list(seq)))
            else:
                seqs.append(seq)
    if output_arr:
        seqs = np.array(seqs)
    return names, seqs


def output_fasta(names, seqs, filepath):
    fout: TextIO
    with open(filepath, 'w') as fout:
        for name, seq in zip(names, seqs):
            fout.write('>{}\n'.format(name))
            fout.write(seq + '\n')
