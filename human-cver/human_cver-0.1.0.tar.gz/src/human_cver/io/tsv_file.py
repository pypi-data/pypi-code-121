"""
Copyright (c) Microsoft Corporation.
Licensed under the MIT license.

Definition of TSV class
"""
# copy from https://github.com/microsoft/MeshTransformer/tree/main/metro/utils/tsv_file.py

import logging
import os
import os.path as op


def generate_lineidx(filein, idxout):
    idxout_tmp = idxout + ".tmp"
    with open(filein, "r") as tsvin, open(idxout_tmp, "w") as tsvout:
        fsize = os.fstat(tsvin.fileno()).st_size
        fpos = 0
        while fpos != fsize:
            tsvout.write(str(fpos) + "\n")
            tsvin.readline()
            fpos = tsvin.tell()
    os.rename(idxout_tmp, idxout)


class TSVFileReader(object):
    def __init__(self, tsv_file):
        self.tsv_file = tsv_file
        self.lineidx = op.splitext(tsv_file)[0] + ".lineidx"
        self._fp = None
        self._lineidx = None
        # the process always keeps the process which opens the file.
        # If the pid is not equal to the currrent pid, we will re-open the file.
        self.pid = None
        # generate lineidx if not exist
        if not op.isfile(self.lineidx):
            generate_lineidx(self.tsv_file, self.lineidx)

    def __del__(self):
        if self._fp:
            self._fp.close()

    def __str__(self):
        return "TSVFile(tsv_file='{}')".format(self.tsv_file)

    def __repr__(self):
        return str(self)

    def num_rows(self):
        self._ensure_lineidx_loaded()
        return len(self._lineidx)

    def seek(self, idx):
        self._ensure_tsv_opened()
        self._ensure_lineidx_loaded()
        try:
            pos = self._lineidx[idx]
        except:
            logging.info("{}-{}".format(self.tsv_file, idx))
            raise
        self._fp.seek(pos)
        return [s.strip() for s in self._fp.readline().split("\t")]

    def __getitem__(self, index):
        return self.seek(index)

    def __len__(self):
        return self.num_rows()

    def _ensure_lineidx_loaded(self):
        if self._lineidx is None:
            logging.info("loading lineidx: {}".format(self.lineidx))
            with open(self.lineidx, "r") as fp:
                self._lineidx = [int(i.strip()) for i in fp.readlines()]

    def _ensure_tsv_opened(self):
        if self._fp is None:
            self._fp = open(self.tsv_file, "r")
            self.pid = os.getpid()

        if self.pid != os.getpid():
            logging.info(
                "re-open {} because the process id changed".format(self.tsv_file)
            )
            self._fp = open(self.tsv_file, "r")
            self.pid = os.getpid()


class TSVFileWriter(object):
    def __init__(self, tsv_file):
        self.tsv_file = tsv_file
        self._fp = None

    def writeline(self, text):
        self._ensure_tsv_opened()
        if isinstance(text, str):
            self._fp.write(text + "\n")
        elif isinstance(text, list):
            text = "\t".join(text)
            self._fp.write(text + "\n")

    def __del__(self):
        self.close()
    
    def _ensure_tsv_opened(self):
        if self._fp is None:
            self._fp = open(self.tsv_file, "w")
    
    def close(self):
        if self._fp:
            self._fp.close()
