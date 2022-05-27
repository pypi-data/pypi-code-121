#######################################################################
#
# Copyright (C) 2020-2022 David Palao
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

import subprocess as sp
from contextlib import contextmanager
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, wait
import time
import re
import shutil
from html.parser import HTMLParser
from typing import Union
from collections.abc import Callable

import psutil

from pacbio_data_processing.constants import (
    SM_ANALYSIS_EXE, BAM_FILTER_EXE, SAMTOOLS_GET_BODY, SM_ANALYSIS_GUI_EXE
)


def find_procs_by_name(name: str) -> list[psutil.Process]:
    """It returns a list with the processes (psutil.Process instances)
    for which 'name' is either the name of the process or of the script.
    """
    procs = []
    for p in psutil.process_iter(["name", "cmdline"]):
        try:
            script = p.info["cmdline"][1]
        except (TypeError, IndexError):
            script = ""
        if name == p.info['name'] or name == Path(script).name:
            procs.append(p)
    return procs


def count_procs_by_name(name: str) -> int:
    """Return the number of processes with 'name' or as a script with
    name 'name' in the first argument."""
    return len(find_procs_by_name(name))


def count_nprocs(
        proc_name: str, seconds: float = 1, tdelta: float = 0.05) -> dict:
    """Determines the max number of concurrent processes with name
    'proc_name' that were found during an interval of measurements*tdelta,
    probing every tdelta seconds.
    It stops measuring 5 measures after a value != 0 has been detected. The
    reason for this arbitrary mechanism is to increase the likelihood of
    measuring a correct value.

    The returned value is a dictionary with the following keys:

    * ``nprocs``: max. number of simultaneous procs. with ``proc_name``
    * ``pids``: all ``PIDs`` corresponding to those procs.

    Warning! The PIDs are not correctly counted!
    """
    counts = set()
    pids = set()
    exit = 5
    measurements = int(seconds/tdelta)
    for it in range(measurements):
        procs = find_procs_by_name(proc_name)
        counts.add(len(procs))
        for p in procs:
            pids.add(p.pid)
        time.sleep(tdelta)
        if exit == 0:
            break
        if len(counts) > 0:
            c = max(counts)
            if c > 0:
                exit -= 1
    return {"pids": pids, "nprocs": max(counts)}


# Refactor hint:
# the *_later functions could be refactored using a decorator

def killall_later(name, delay):
    """It kills all instances of programs with 'name' as name
    or script name after 'delay' seconds.
    """
    time.sleep(delay)
    for p in find_procs_by_name(name):
        p.terminate()


def remove_later(delay_seconds: float, *filenames: Path) -> None:
    """It removes the filenames provided after some time."""
    time.sleep(delay_seconds)
    for filename in filenames:
        filename.unlink(missing_ok=True)


def run_later(
        delay_seconds: float,
        cmd: Union[list[str], Callable],
        *args: str
) -> None:
    """Defer execution of a command, ``cmd`` by ``delay_seconds``.
    The command can be:
    1. a list of strings to be passe4d to subprocess.run (ie, a
       command in the so-calloed executable form), or
    2. a callable, to be called with ``*args``.
    """
    time.sleep(delay_seconds)
    if callable(cmd):
        cmd(*args)
    else:
        sp.run(cmd)


@contextmanager
def run_sm_analysis(*opts):
    """A function to launch "sm-analysis" within the FTs. It is a context
    manager to make it more powerful and easy to use. I'm using
    this solution instead of using "fixtures for everything" to be more
    explicit in some steps of the configuration, simulating the
    human intervention. I hope.

    Example usage:

    # To just call " -h"
    with run_sm_analysis("-h") as help_result:
        self.assertEqual(help_result[0].returncode, 0)

    """
    with ThreadPoolExecutor(max_workers=5) as executor:
        # "seconds" parameters must be increased if the
        # system has high load:
        future_to_nprocs_blasr = executor.submit(
            count_nprocs, "blasr", seconds=2.5)  # seconds=2.5)
        future_to_nprocs_ipd = executor.submit(
            count_nprocs, "ipdSummary", seconds=2.5)  # seconds=2)
        future_to_nprocs_ccs = executor.submit(
            count_nprocs, "ccs", seconds=2.5)  # seconds=3)
        line = [SM_ANALYSIS_EXE]+list(opts)
        future_to_result = executor.submit(
            sp.run, line, stdout=sp.PIPE, stderr=sp.PIPE)
        wait(
            (future_to_result, future_to_nprocs_ipd,
                future_to_nprocs_blasr, future_to_nprocs_ccs)
        )
        # result = sp.run(line, stdout=sp.PIPE, stderr=sp.PIPE)
    ipdSummary_result = future_to_nprocs_ipd.result()
    blasr_result = future_to_nprocs_blasr.result()
    ccs_result = future_to_nprocs_ccs.result()
    meta = {
        "nprocs_ipdsummary": ipdSummary_result["nprocs"],
        "pids_ipdsummary": ipdSummary_result["pids"],
        "nprocs_blasr": blasr_result["nprocs"],
        "pids_blasr": blasr_result["pids"],
        "nprocs_ccs": ccs_result["nprocs"],
        "pids_ccs": ccs_result["pids"],
    }
    yield (future_to_result.result(), meta)
    # post-work (clean up?, ...). Remove files with results?


@contextmanager
def run_sm_analysis_gui(*opts):
    """A function to launch "sm-analysis-gui" within the FTs. It is a
    context manager to make it more powerful and easy to use. I'm using
    this solution instead of using "fixtures for everything" to be more
    explicit in some steps of the configuration, simulating the
    human intervention. I hope.

    Example usage:

    with run_sm_analysis_gui() as program:
        ...

    """
    line = [SM_ANALYSIS_GUI_EXE]+list(opts)
    # pre-work
    result = sp.run(line, stdout=sp.PIPE, stderr=sp.PIPE)
    yield result
    # post-work (clean up?, ...)


@contextmanager
def run_bam_filter(*opts):
    """A function to launch "sm-analysis" within the FTs. It is a context
    manager to make it more powerful and easy to use. I'm using
    this solution instead of using "fixtures for everything" to be more
    explicit in some steps of the configuration, simulating the
    human intervention. I hope.

    Example usage:

    # To just call " -h"
    with run_bam_filter("-h") as help_result:
        self.assertEqual(help_result.returncode, 0)

    """
    line = [BAM_FILTER_EXE]+list(opts)
    # pre-work
    result = sp.run(line, stdout=sp.PIPE, stderr=sp.PIPE)
    yield result
    # post-work (clean up?, ...)


@contextmanager
def run_samtools_get_body(*opts):
    """A function to launch "samtools view" within the FTs. It is a context
    manager to make it more powerful and easy to use. I'm using
    this solution instead of using "fixtures for everything" to be more
    explicit in some steps of the configuration, simulating the
    human intervention. I hope.

    Example usage:

    # To get a body:
    with run_samtools_get_body("my.bam") as body:
        self.assertEqual(body.returncode, 0)

    """
    line = list(SAMTOOLS_GET_BODY+opts)
    # pre-work
    result = sp.run(line, stdout=sp.PIPE, stderr=sp.PIPE)
    yield result
    # post-work (clean up?, ...)


def normalize_whitespaces(text):
    """Normalize the whitespaces in the text: any whitespace sequence -> ' '
    """
    return re.sub(r"[\r\s]+", " ", text)


def old_normalize_whitespaces(text):
    """Normalize the whitespaces in the text: any whitespace sequence -> ' '
    """
    text = text.replace("\n", " ")
    while True:
        new_text = text.replace("\t", " ")
        new_new_text = new_text.replace("  ", " ")
        if new_new_text == text:
            break
        else:
            text = new_new_text
    return text


@contextmanager
def temporarily_rename_file(path: Path):
    """As the name says, this function (intended to be used in a
    with statement) temporarily renames a file to a unique
    different name and restores back the original name afterwards.
    """
    prefix = ".hidden"
    new_name = prefix+"."+path.name
    while path.with_name(new_name).exists():
        new_name = prefix + new_name
    shutil.move(path, new_name)
    yield
    shutil.move(new_name, path)


class SummaryReportParser(HTMLParser):
    """Simple ad-hoc parser to collect the important data from the
    summary reports made by sm-analysis.

    >>> p = SummaryReportParser()
    >>> html = '<html><head><title>Just a little report</title></head>'
    >>> html += '<body><h2>Numbers</h2><h3>Irrational</h3>'
    >>> html += '<table><tr><td>pi:</td><td>3.14159...</td></tr>'
    >>> html += '<tr><td>e</td><td>2.71828...</td></tr></table>'
    >>> html += '<h3>Integer</h3>'
    >>> html += '<table><tr><th></th><th>negative</th><th>positive</th></tr>'
    >>> html += '<tr><td>sqrt(1)</td><td>-1</td><td>+1</td></tr>'
    >>> html += '<tr><td>sqrt(4)</td><td>-2</td><td>+2</td></tr></table>'
    >>> html += '<h1>Physics</h1>'
    >>> html += '<table><tr><td>c</td><td>1</td></tr>'
    >>> html += '<tr><td>ħ</td><td>1</td></tr></table>'
    >>> html += '</body></html>'
    >>> p.feed(html)
    >>> p.parsed_data
    {'images': [], 'title': 'Just a little report', 'Numbers >> Irrational': {'pi:': '3.14159...', 'e': '2.71828...'}, 'Numbers >> Integer': {'sqrt(1)': {'negative': '-1', 'positive': '+1'}, 'sqrt(4)': {'negative': '-2', 'positive': '+2'}}, 'Physics': {'c': '1', 'ħ': '1'}}
    """

    ALL_SECTIONS = ("h1", "h2", "h3", "h4", "h5", "h6")

    def __init__(self):
        super().__init__()
        self._pay_attention_to_tags = {"title"}
        self._must_i_read = False
        self.parsed_data = {}
        self._within_table = False
        self.add = self.add_to_parsed_dict
        self._td_idx = -1
        self._table_headers = []
        self.sections = {}
        self._read_section = False
        self._new_section = None
        self.images = []
        self.parsed_data["images"] = self.images

    def arrange_sections(self):
        """Every time a new section is found in the html file,
        the others are scanned and it is evaluated what is the
        current chain (section, subsection, subsubsection, ...).
        """
        current_sections = list(self.sections.keys())
        for tag in current_sections:
            if tag >= self._new_section:
                del self.sections[tag]

    def handle_starttag(self, tag, attrs):
        if tag in self._pay_attention_to_tags:
            self._must_i_read = True
        if tag == "table":
            self._table_headers = []
        elif tag == "th":
            self._must_i_read = True
            self.add = self.add_to_table_headers
        elif tag == "tr":
            self._td_idx = -1
        elif tag == "td":
            self._td_idx += 1
            self._must_i_read = True
            self.add = self.add_to_parsed_dict
        elif tag == "img":
            self.images.append(dict(attrs))
        elif tag in self._pay_attention_to_tags:
            self._prev_data = tag
        elif tag in self.ALL_SECTIONS:
            self._read_section = True
            self._new_section = tag
            self.arrange_sections()

    def add_to_table_headers(self, what):
        self._table_headers.append(what)

    @property
    def squeezed_section(self):
        """Makes a key (string) out of the current section-chain, with
        the format
        section >> subsection >> subsubsection ...
        """
        if len(self.sections) == 0:
            return None
        else:
            return " >> ".join(
                [self.sections[_] for _ in self.ALL_SECTIONS if _ in self.sections]
            )

    def add_to_parsed_dict(self, what):
        if self.squeezed_section:
            # we are within a section
            section_dict = self.parsed_data.setdefault(
                self.squeezed_section, {})
        else:
            # We are in the root:
            section_dict = self.parsed_data
        if self._td_idx == 0:
            if len(self._table_headers) == 0:
                self._prev_data = what
            else:
                self._current_subdict_key = what
                section_dict[self._current_subdict_key] = {}
        else:
            if len(self._table_headers) == 0:
                section_dict[self._prev_data] = what
            else:
                subkey = self._table_headers[self._td_idx]
                section_dict[self._current_subdict_key][subkey] = what

    def handle_data(self, data):
        if self._must_i_read:
            self.add(data)
        if self._read_section:
            self.sections[self._new_section] = data
        self._must_i_read = False

    def handle_endtag(self, tag):
        if tag == "table":
            self._table_headers = []
            self._td_idx = -1
        elif tag in self.ALL_SECTIONS:
            self._read_section = False
            self._new_section = None
        if self._must_i_read:
            self._must_i_read = False
            if tag == "th":
                # No data was read...
                self._table_headers.append("")


def count_marker_files(basename) -> int:
    """Given a basename (blasr, ccs, ...) it returns how many files
    are found in the CWD with a name following this pattern:
    .{basename}.pid.[0-9]*
    The aim is to allow the fake tools to self declare how many times
    they have been executed.
    """
    p = Path(".")
    return len(list(p.glob(f".{basename}.pid.[0-9]*")))
