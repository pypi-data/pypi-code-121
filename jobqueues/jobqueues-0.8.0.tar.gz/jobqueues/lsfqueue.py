# (c) 2015-2018 Acellera Ltd http://www.acellera.com
# All Rights Reserved
# Distributed under HTMD Software License Agreement
# No redistribution in whole or part
#
import os
import shutil
import random
import string
from subprocess import check_output, CalledProcessError, DEVNULL
from protocolinterface import ProtocolInterface, val
from jobqueues.simqueue import SimQueue
from jobqueues.util import ensurelist
from jobqueues.config import loadConfig
import yaml
import logging

logger = logging.getLogger(__name__)


class LsfQueue(SimQueue, ProtocolInterface):
    """Queue system for LSF

    Parameters
    ----------
    version : [9, 10], int, default=9
        LSF major version
    jobname : str, default=None
        Job name (identifier)
    queue : list, default=None
        The queue or list of queues to run on. If list, it attempts to submit the job to the first queue listed
    app : str, default=None
        The application profile
    ngpu : int, default=1
        Number of GPUs to use for a single job
    gpu_options : dict, default=None
        Number of GPUs to use for a single job (valid dict entries: {'mode': <'shared' or 'exclusive_process'>}, {'mps':
        <'yes' or 'no'>}, {'j_exclusive': <'yes' or 'no'>})
    ncpu : int, default=1
        Number of CPUs to use for a single job
    memory : int, default=4000000
        Amount of memory per job (KB)
    walltime : int, default=None
        Job timeout (hour:min or min)
    resources : list, default=None
        Resources of the queue
    outputstream : str, default='lsf.%J.out'
        Output stream.
    errorstream : str, default='lsf.%J.err'
        Error stream.
    datadir : str, default=None
        The path in which to store completed trajectories.
    trajext : str, default='xtc'
        Extension of trajectory files. This is needed to copy them to datadir.
    envvars : str, default='ACEMD_HOME'
        Envvars to propagate from submission node to the running node (comma-separated)
    prerun : list, default=None
        Shell commands to execute on the running node before the job (e.g. loading modules)



    Examples
    --------
    >>> s = LsfQueue()
    >>> s.jobname = 'simulation1'
    >>> s.queue = 'multiscale'
    >>> s.submit('/my/runnable/folder/')  # Folder containing a run.sh bash script
    """

    _defaults = {
        "version": 9,
        "queue": None,
        "app": None,
        "gpu_queue": None,
        "cpu_queue": None,
        "ngpu": 1,
        "gpu_options": None,
        "ncpu": 1,
        "memory": 4000000,
        "walltime": None,
        "resources": None,
        "envvars": "ACEMD_HOME",
        "prerun": None,
    }

    def __init__(
        self, _configapp=None, _configfile=None, _findExecutables=True, _logger=True
    ):
        SimQueue.__init__(self)
        ProtocolInterface.__init__(self)
        self._arg(
            "version",
            "int",
            "LSF major version",
            self._defaults["version"],
            valid_values=[9, 10],
        )
        self._arg("jobname", "str", "Job name (identifier)", None, val.String())
        self._arg(
            "queue",
            "list",
            "The queue or list of queues to run on. If list, it attempts to submit the job to "
            "the first queue listed",
            self._defaults["queue"],
            val.String(),
            nargs="*",
        )
        self._arg(
            "app", "str", "The application profile", self._defaults["app"], val.String()
        )
        self._arg(
            "ngpu",
            "int",
            "Number of GPUs to use for a single job",
            self._defaults["ngpu"],
            val.Number(int, "0POS"),
        )
        self._arg(
            "gpu_options",
            "dict",
            "Number of GPUs to use for a single job",
            self._defaults["gpu_options"],
            val.Dictionary(
                key_type=str,
                valid_keys=["mode", "mps", "j_exclusive"],
                value_type={"mode": str, "mps": str, "j_exclusive": str},
                valid_values={
                    "mode": ["shared", "exclusive_process"],
                    "mps": ["yes", "no"],
                    "j_exclusive": ["yes", "no"],
                },
            ),
        )
        self._arg(
            "ncpu",
            "int",
            "Number of CPUs to use for a single job",
            self._defaults["ncpu"],
            val.Number(int, "0POS"),
        )
        self._arg(
            "memory",
            "int",
            "Amount of memory per job (KB)",
            self._defaults["memory"],
            val.Number(int, "0POS"),
        )
        self._arg(
            "walltime",
            "int",
            "Job timeout (hour:min or min)",
            self._defaults["walltime"],
            val.Number(int, "0POS"),
        )
        self._arg(
            "resources",
            "list",
            "Resources of the queue",
            self._defaults["resources"],
            val.String(),
            nargs="*",
        )
        self._cmdDeprecated("environment", "prerun")
        self._arg("outputstream", "str", "Output stream.", "lsf.%J.out", val.String())
        self._arg("errorstream", "str", "Error stream.", "lsf.%J.err", val.String())
        self._arg(
            "datadir",
            "str",
            "The path in which to store completed trajectories.",
            None,
            val.String(),
        )
        self._arg(
            "trajext",
            "str",
            "Extension of trajectory files. This is needed to copy them to datadir.",
            "xtc",
            val.String(),
        )
        self._arg(
            "envvars",
            "str",
            "Envvars to propagate from submission node to the running node (comma-separated)",
            self._defaults["envvars"],
            val.String(),
        )
        self._arg(
            "prerun",
            "list",
            "Shell commands to execute on the running node before the job (e.g. "
            "loading modules)",
            self._defaults["prerun"],
            val.String(),
            nargs="*",
        )

        # Load LSF configuration profile
        loadConfig(self, "lsf", _configfile, _configapp, _logger)

        # Find executables
        if _findExecutables:
            self._qsubmit = LsfQueue._find_binary("bsub")
            self._qinfo = LsfQueue._find_binary("bqueues")
            self._qcancel = LsfQueue._find_binary("bkill")
            self._qstatus = LsfQueue._find_binary("bjobs")

    @staticmethod
    def _find_binary(binary):
        ret = shutil.which(binary, mode=os.X_OK)
        if not ret:
            raise FileNotFoundError(
                "Could not find required executable [{}]".format(binary)
            )
        ret = os.path.abspath(ret)
        return ret

    def _createJobScript(self, fname, workdir, runsh):
        from jobqueues.util import ensurelist

        workdir = os.path.abspath(workdir)
        with open(fname, "w") as f:
            f.write("#!/bin/bash\n")
            f.write("#\n")
            f.write(f"#BSUB -J {self.jobname}\n")
            f.write('#BSUB -q "{}"\n'.format(" ".join(ensurelist(self.queue))))
            f.write(f"#BSUB -n {self.ncpu}\n")
            if self.app is not None:
                f.write(f"#BSUB -app {self.app}\n")
            if self.ngpu != 0:
                if self.version == 9:
                    if self.gpu_options is not None:
                        logger.warning(
                            "gpu_options argument was set while it is not needed for LSF version 9"
                        )
                    f.write(
                        '#BSUB -R "select[ngpus>0] rusage[ngpus_excl_p={}]"\n'.format(
                            self.ngpu
                        )
                    )
                elif self.version == 10:
                    if not self.gpu_options:
                        self.gpu_options = {"mode": "exclusive_process"}
                    gpu_requirements = list()
                    gpu_requirements.append(f"num={self.ngpu}")
                    for i in self.gpu_options:
                        gpu_requirements.append(f"{i}={self.gpu_options[i]}")
                    f.write('#BSUB -gpu "{}"\n'.format(":".join(gpu_requirements)))
                else:
                    raise AttributeError("Version not supported")
            if self.resources is not None:
                for resource in ensurelist(self.resources):
                    f.write(f'#BSUB -R "{resource}"\n')
            f.write(f"#BSUB -M {self.memory}\n")
            f.write(f"#BSUB -cwd {workdir}\n")
            f.write(f"#BSUB -outdir {workdir}\n")
            f.write(f"#BSUB -o {self.outputstream}\n")
            f.write(f"#BSUB -e {self.errorstream}\n")
            if self.envvars is not None:
                f.write(f"#BSUB --env {self.envvars}\n")
            if self.walltime is not None:
                f.write(f"#BSUB -W {self.walltime}\n")
            # Trap kill signals to create sentinel file
            f.write(
                '\ntrap "touch {}" EXIT SIGTERM\n'.format(
                    os.path.normpath(os.path.join(workdir, self._sentinel))
                )
            )
            f.write("\n")
            if self.prerun is not None:
                for call in ensurelist(self.prerun):
                    f.write(f"{call}\n")
            f.write(f"\ncd {workdir}\n")
            f.write(runsh)

            # Move completed trajectories
            if self.datadir is not None:
                simname = os.path.basename(os.path.normpath(workdir))
                datadir = os.path.abspath(os.path.join(self.datadir, simname))
                os.makedirs(datadir, exist_ok=True)
                f.write(f"\nmv *.{self.trajext} {datadir}")

        os.chmod(fname, 0o700)

    def retrieve(self):
        # Nothing to do
        pass

    def _autoJobName(self, path):
        return (
            os.path.basename(os.path.abspath(path))
            + "_"
            + "".join([random.choice(string.digits) for _ in range(5)])
        )

    def submit(self, dirs, commands=None):
        """Submits all directories

        Parameters
        ----------
        dirs : list
            A list of executable directories.
        """
        dirs = self._submitinit(dirs)

        if self.queue is None:
            raise ValueError("The queue needs to be defined.")

        # if all folders exist, submit
        for i, d in enumerate(dirs):
            logger.info("Queueing " + d)

            if self.jobname is None:
                self.jobname = self._autoJobName(d)

            runscript = (
                commands[i] if commands is not None else self._getRunScript(d)
            )
            self._cleanSentinel(d)

            jobscript = os.path.abspath(os.path.join(d, "job.sh"))
            self._createJobScript(jobscript, d, runscript)
            try:
                ret = check_output(self._qsubmit + " < " + jobscript, shell=True)
                logger.debug(ret)
            except CalledProcessError as e:
                logger.error(e.output)
                raise
            except:
                raise

    def inprogress(self):
        """Returns the sum of the number of running and queued workunits of the specific group in the engine.

        Returns
        -------
        total : int
            Total running and queued workunits
        """
        import time
        import getpass

        if self.queue is None:
            raise ValueError("The queue needs to be defined.")
        if self.jobname is None:
            raise ValueError("The jobname needs to be defined.")
        user = getpass.getuser()
        l_total = 0
        for q in ensurelist(self.queue):
            cmd = [self._qstatus, "-J", self.jobname, "-u", user, "-q", q]
            logger.debug(cmd)

            # This command randomly fails so I need to allow it to repeat or it crashes adaptive
            tries = 0
            while tries < 3:
                try:
                    ret = check_output(cmd, stderr=DEVNULL)
                except CalledProcessError:
                    if tries == 2:
                        raise
                    tries += 1
                    time.sleep(3)
                    continue
                break

            logger.debug(ret.decode("ascii"))

            # TODO: check lines and handle errors
            l = ret.decode("ascii").split("\n")
            l = len(l) - 2
            if l < 0:
                l = 0  # something odd happened
            l_total += l
        return l_total

    def stop(self):
        """Cancels all currently running and queued jobs"""
        import getpass

        if self.jobname is None:
            raise ValueError("The jobname needs to be defined.")

        user = getpass.getuser()

        if self.queue is not None:
            for q in ensurelist(self.queue):
                cmd = [self._qcancel, "-J", self.jobname, "-u", user, "-q", q]
                logger.debug(cmd)
                ret = check_output(cmd, stderr=DEVNULL)
                logger.debug(ret.decode("ascii"))
        else:
            cmd = [self._qcancel, "-J", self.jobname, "-u", user]
            logger.debug(cmd)
            ret = check_output(cmd, stderr=DEVNULL)
            logger.debug(ret.decode("ascii"))

    @property
    def ncpu(self):
        return self.__dict__["ncpu"]

    @ncpu.setter
    def ncpu(self, value):
        self.ncpu = value

    @property
    def ngpu(self):
        return self.__dict__["ngpu"]

    @ngpu.setter
    def ngpu(self, value):
        self.ngpu = value

    @property
    def memory(self):
        return self.__dict__["memory"]

    @memory.setter
    def memory(self, value):
        self.memory = value


import unittest


class _TestLsfQueue(unittest.TestCase):
    def test_config(self):
        from jobqueues.home import home
        import os

        configfile = os.path.join(home(), "config_lsf.yml")
        with open(configfile, "r") as f:
            reference = yaml.load(f, Loader=yaml.FullLoader)

        for appkey in reference:
            sq = LsfQueue(
                _configapp=appkey, _configfile=configfile, _findExecutables=False
            )
            for key in reference[appkey]:
                assert (
                    sq.__getattribute__(key) == reference[appkey][key]
                ), f'Config setup of LsfQueue failed on app "{appkey}" and key "{key}""'


if __name__ == "__main__":
    unittest.main(verbosity=2)
