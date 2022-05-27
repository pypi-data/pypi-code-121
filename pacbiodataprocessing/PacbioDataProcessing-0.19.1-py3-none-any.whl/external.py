#######################################################################
#
# Copyright (C) 2021, 2022 David Palao
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

import subprocess
import logging
from pathlib import Path
from typing import Optional

from .types import PathOrStr, ReturnCode
from .sentinel import Sentinel, SentinelFileFound, SentinelFileNotFound


class ExternalProgram:
    """A base class with common functionality to all external
    programs' classes that:

    1. produce an output file, and
    2. its production is to be protected by a ``Sentinel``.

    This base class provides the interface and the ``Sentinel``
    protection.
    """
    def __init__(self, path: PathOrStr) -> None:
        self.program = path
        self.program_name = self.__class__.__name__.lower()

    def _run(self, *args, **kwargs) -> tuple[ReturnCode, str]:
        """Abstract internal method used by ``__call__``."""
        raise NotImplementedError

    def _log_ok_computation(self, outfile: PathOrStr) -> None:
        """Abstract internal method used by ``__call__``."""
        raise NotImplementedError

    def _log_err_computation(
            self, infile: PathOrStr, outfile: PathOrStr, err_msg: str) -> None:
        """Internal method used by ``__call__``.
        """
        logging.error(
            f"[{self.program_name}] During the execution of '{self.program}' "
            "an error occurred"
        )
        logging.error(
            f"[{self.program_name}] The following command was issued:"
        )
        cmd_issued = " ".join([str(_) for _ in self.cmd_issued])
        logging.error(f"    '{cmd_issued}'")
        if len(err_msg.strip()) == 0:
            log_err_msg = (
                f"[{self.program_name}] ...but the program did not report "
                "any error message."
            )
        else:
            log_err_msg = (
                f"[{self.program_name}] ...the error message was: '{err_msg}'"
            )
        logging.error(log_err_msg)

    def __call__(
            self,
            infile: PathOrStr,
            outfile: PathOrStr,
            *args, **kwargs
    ) -> Optional[ReturnCode]:
        """It runs the executable, with the given paramenters.
        The return code of the associated process is returned by this
        method *if* the executable could run at all, else ``None`` is
        returned.

        One case where the executable cannot run is when the sentinel
        file is there *before* the executable process is run.
        """
        path_outfile = Path(outfile)
        try:
            sentinel = Sentinel(path_outfile)
            with sentinel:
                result, err_msg = self._run(infile, outfile, *args, **kwargs)
        except SentinelFileFound:
            result = None
            logging.warning(
                f"Sentinel file '{sentinel.path}' detected! "
                f"Delaying {self.program_name} computation."
            )
        except SentinelFileNotFound:
            logging.warning(
                f"Sentinel file '{sentinel.path}' disappeared before "
                f"{self.program_name} finished its computation!"
            )
            logging.warning(
                " ...some other person/process is probably carrying out a "
                "similar computation in the same directory and messing up."
            )
            logging.warning(
                "    The integrity of the results may be compromised!"
            )
        else:
            if result == 0:
                if path_outfile.exists():
                    self._log_ok_computation(outfile)
            else:
                self._log_err_computation(infile, outfile, err_msg)
        return result


class Blasr(ExternalProgram):
    """An object to interact with the ``blasr`` aligner.
    """
    def __call__(self,
                 in_bamfile: PathOrStr,
                 fasta: PathOrStr,
                 out_bamfile: PathOrStr,
                 nprocs: int = 1) -> Optional[ReturnCode]:
        return super().__call__(in_bamfile, out_bamfile, fasta, nprocs)

    def _run(self,
             in_bamfile: PathOrStr,
             out_bamfile: PathOrStr,
             fasta: PathOrStr,
             nprocs: int = 1) -> tuple[ReturnCode, str]:
        self.cmd_issued = (
            str(self.program), str(in_bamfile), str(fasta),
            "--nproc", f"{nprocs}",
            "--bam", "--out", str(out_bamfile)
        )
        blasr_proc = subprocess.run(self.cmd_issued, capture_output=True)
        return (blasr_proc.returncode, blasr_proc.stderr.decode())

    def _log_ok_computation(self, outfile: PathOrStr) -> None:
        logging.info(
            f"[{self.program_name}] Aligned file '{outfile}' "
            "generated"
        )

    def _log_err_computation(
            self, infile: PathOrStr, outfile: PathOrStr, err_msg: str) -> None:
        logging.error(
            f"[{self.program_name}] '{self.program}' could not align the "
            f"input file '{infile}'")
        super()._log_err_computation(infile, outfile, err_msg)


class CCS(ExternalProgram):
    """An object to interact with the ``ccs`` program.
    """
    def __call__(self,
                 in_bamfile: PathOrStr,
                 out_bamfile: PathOrStr,
                 ) -> Optional[ReturnCode]:
        return super().__call__(in_bamfile, out_bamfile)

    def _run(self,
             in_bamfile: PathOrStr,
             out_bamfile: PathOrStr,
             ) -> tuple[ReturnCode, str]:
        self.cmd_issued = (self.program, in_bamfile, out_bamfile)
        ccs_proc = subprocess.run(self.cmd_issued, capture_output=True)
        return (ccs_proc.returncode, ccs_proc.stderr.decode())

    def _log_ok_computation(self, outfile: PathOrStr) -> None:
        logging.info(f"[{self.program_name}] File '{outfile}' generated")
