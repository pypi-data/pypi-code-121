# (c) 2015-2018 Acellera Ltd http://www.acellera.com
# All Rights Reserved
# Distributed under HTMD Software License Agreement
# No redistribution in whole or part
#
import os
import shutil
import random
import string
from subprocess import check_output, CalledProcessError
from protocolinterface import ProtocolInterface, val
from jobqueues.simqueue import SimQueue
from jobqueues.config import loadConfig
import logging

logger = logging.getLogger(__name__)


class PBSQueue(SimQueue, ProtocolInterface):
    """

    .. warning:: This queue system has not been tested and can possibly fail.

    Queue system for PBS

    Parameters
    ----------
    jobname : str, default=None
        Job name (identifier)
    queue : str, default=None
        The queue to run on
    ngpu : int, default=0
        Number of GPUs to use for a single job
    ncpu : int, default=1
        Number of CPUs to use for a single job
    memory : int, default=1000
        Amount of memory per job (MB)
    walltime : int, default=3600
        Job timeout (s)
    environment : str, default='ACEMD_HOME,HTMD_LICENSE_FILE'
        Envvars to propagate to the job.
    datadir : str, default=None
        The path in which to store completed trajectories.
    trajext : str, default='xtc'
        Extension of trajectory files. This is needed to copy them to datadir.
    cluster : str, default=None
        Select nodes from a single specified cluster
    scratch_local : int, default=None
        Local scratch in MB


    Examples
    --------
    >>> from jobqueues.pbsqueue import PBSQueue
    >>> s = PBSQueue()
    >>> s.queue = 'multiscale'
    >>> s.submit('/my/runnable/folder/')  # Folder containing a run.sh bash script
    """

    def __init__(
        self, _configapp=None, _configfile=None, _findExecutables=True, _logger=True
    ):
        super().__init__()
        self._arg("jobname", "str", "Job name (identifier)", None, val.String())
        self._arg("queue", "str", "The queue to run on", None, val.String())
        self._arg(
            "ngpu",
            "int",
            "Number of GPUs to use for a single job",
            0,
            val.Number(int, "0POS"),
        )
        self._arg(
            "ncpu",
            "int",
            "Number of CPUs to use for a single job",
            1,
            val.Number(int, "0POS"),
        )
        self._arg(
            "memory",
            "int",
            "Amount of memory per job (MB)",
            1000,
            val.Number(int, "0POS"),
        )
        self._arg("walltime", "int", "Job timeout (s)", 3600, val.Number(int, "POS"))
        self._arg(
            "environment",
            "str",
            "Envvars to propagate to the job.",
            "ACEMD_HOME,HTMD_LICENSE_FILE",
            val.String(),
        )
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
            "cluster",
            "str",
            "Select nodes from a single specified cluster",
            None,
            val.String(),
        )
        self._arg(
            "scratch_local", "int", "Local scratch in MB", None, val.Number(int, "0POS")
        )

        loadConfig(self, "pbs", _configfile, _configapp, _logger)

        # Find executables
        if _findExecutables:
            self._qsubmit = PBSQueue._find_binary("qsub")
            self._qinfo = PBSQueue._find_binary("qstat") + " -a"
            self._qcancel = PBSQueue._find_binary("qdel")
            self._qstatus = PBSQueue._find_binary("qstat") + " -Q"

        self._sentinel = "jobqueues.done"
        # For synchronous
        self._joblist = []
        self._dirs = []

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
        workdir = os.path.abspath(workdir)
        if not self.queue and self.ngpu > 0:
            self.queue = "gpgpu"
        with open(fname, "w") as f:
            f.write("#!/bin/bash\n")
            f.write("#\n")
            if self.jobname:
                f.write(f"#PBS -N={self.jobname}\n")
            f.write(
                f"#PBS -lselect=1:ncpus={self.ncpu}:ngpus={self.ngpu}:mem={self.memory}MB"
            )
            if self.scratch_local is not None:
                f.write(f":scratch_local={self.scratch_local}MB")
            if self.cluster is not None:
                f.write(f":cl_{self.cluster}=True")
            f.write("\n")
            if self.queue:
                f.write(f"#PBS -q  {self.queue}\n")
            hours = int(self.walltime / 3600)
            minutes = int((self.walltime % 3600) / 60)
            seconds = self.walltime % 3600 % 60
            f.write(f"#PBS -lwalltime={hours}:{minutes}:{seconds}\n")
            if self.environment is not None:
                a = []
                for i in self.environment.split(","):
                    if (i in os.environ) and len(os.environ[i]):
                        a.append(i)
                f.write("#PBS -v %s\n" % (",".join(a)))
            # Trap kill signals to create sentinel file
            f.write(
                '\ntrap "touch {}" EXIT SIGTERM\n'.format(
                    os.path.normpath(os.path.join(workdir, self._sentinel))
                )
            )
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

    def _autoQueueName(self):
        ret = check_output(self._qinfo)
        return ",".join(
            list(
                set(
                    [
                        i.split()[0].strip("*")
                        for i in ret.decode("ascii").split("\n")[1:-1]
                    ]
                )
            )
        )

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
        dist : list
            A list of executable directories.
        """
        dirs = self._submitinit(dirs)

        if self.queue is None:
            self.queue = self._autoQueueName()

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
                ret = check_output([self._qsubmit, jobscript])
                try:
                    jid = ret.decode("ascii").split("\n")[0]
                    self._joblist.append(jid)
                    logger.info("Job id %s" % jid)
                except:
                    pass
                logger.debug(ret)
            except CalledProcessError as e:
                logger.error(e.output)
                raise
            except:
                raise

    def inprogress(self, debug=False):
        """Returns the sum of the number of running and queued workunits of the specific group in the engine.

        Returns
        -------
        total : int
            Total running and queued workunits
        """
        import time
        import getpass

        if self.queue is None:
            self.queue = self._autoQueueName()
        if self.jobname is None:
            raise ValueError("The jobname needs to be defined.")
        user = getpass.getuser()
        cmd = [self._qstatus, "-J", self.jobname, "-u", user, "-q", self.queue]
        logger.debug(cmd)

        # This command randomly fails so I need to allow it to repeat or it crashes adaptive
        tries = 0
        while tries < 3:
            try:
                ret = check_output(cmd)
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
        return l

    def stop(self):
        """Cancels all currently running and queued jobs"""
        import getpass

        if self.partition is None:
            raise ValueError("The partition needs to be defined.")
        for j in self._joblist:
            cmd = [self._qcancel, j]
            logger.debug(cmd)
            ret = check_output(cmd)
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


if __name__ == "__main__":
    pass
