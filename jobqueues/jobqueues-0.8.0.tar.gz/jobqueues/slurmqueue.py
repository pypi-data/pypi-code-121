# (c) 2015-2018 Acellera Ltd http://www.acellera.com
# All Rights Reserved
# Distributed under HTMD Software License Agreement
# No redistribution in whole or part
#
import os
import shutil
import random
import string
from jobqueues.config import loadConfig
import yaml
from subprocess import check_output, CalledProcessError
from protocolinterface import ProtocolInterface, val
from jobqueues.simqueue import SimQueue, QueueJobStatus, _inProgressStatus
from jobqueues.util import ensurelist
import getpass
import unittest
import logging

logger = logging.getLogger(__name__)


JOB_STATE_CODES = {
    "BOOT_FAIL": QueueJobStatus.FAILED,
    "CANCELLED": QueueJobStatus.CANCELLED,
    "COMPLETED": QueueJobStatus.COMPLETED,
    "DEADLINE": QueueJobStatus.FAILED,
    "FAILED": QueueJobStatus.FAILED,
    "NODE_FAIL": QueueJobStatus.FAILED,
    "OUT_OF_MEMORY": QueueJobStatus.OUT_OF_MEMORY,
    "PENDING": QueueJobStatus.PENDING,
    "PREEMPTED": QueueJobStatus.PENDING,
    "RUNNING": QueueJobStatus.RUNNING,
    "REQUEUED": QueueJobStatus.PENDING,
    "RESIZING": QueueJobStatus.PENDING,
    "REVOKED": QueueJobStatus.FAILED,
    "SUSPENDED": QueueJobStatus.PENDING,
    "TIMEOUT": QueueJobStatus.TIMEOUT,
}


class SlurmQueue(SimQueue, ProtocolInterface):
    """Queue system for SLURM

    Parameters
    ----------
    jobname : str, default=None
        Job name (identifier)
    partition : str or list of str, default=None
        The queue (partition) or list of queues to run on. If list, the one offering earliest initiation will be used.
    priority : str, default=None
        Job priority
    ngpu : int, default=1
        Number of GPUs to use for a single job
    ncpu : int, default=1
        Number of CPUs to use for a single job
    memory : int, default=1000
        Amount of memory per job (MiB)
    gpumemory : int, default=None
        Only run on GPUs with at least this much memory. Needs special setup of SLURM. Check how to define gpu_mem on
        SLURM.
    walltime : int, default=None
        Job timeout (s)
    mailtype : str, default=None
        When to send emails. Separate options with commas like 'END,FAIL'.
    mailuser : str, default=None
        User email address.
    outputstream : str, default='slurm.%N.%j.out'
        Output stream.
    errorstream : str, default='slurm.%N.%j.err'
        Error stream.
    datadir : str, default=None
        The path in which to store completed trajectories.
    trajext : str, default='xtc'
        Extension of trajectory files. This is needed to copy them to datadir.
    nodelist : list, default=None
        A list of nodes on which to run every job at the *same time*! Careful! The jobs will be duplicated!
    exclude : list, default=None
        A list of nodes on which *not* to run the jobs. Use this to select nodes on which to allow the jobs to run on.
    envvars : str, default='ACEMD_HOME,HTMD_LICENSE_FILE'
        Envvars to propagate from submission node to the running node (comma-separated)
    prerun : list, default=None
        Shell commands to execute on the running node before the job (e.g. loading modules)

    Examples
    --------
    >>> s = SlurmQueue()
    >>> s.partition = 'multiscale'
    >>> s.submit('/my/runnable/folder/')  # Folder containing a run.sh bash script
    """

    _defaults = {
        "partition": None,
        "priority": None,
        "ngpu": 1,
        "ncpu": 1,
        "memory": 1000,
        "walltime": None,
        "envvars": "ACEMD_HOME,HTMD_LICENSE_FILE",
        "prerun": None,
    }

    def __init__(
        self, _configapp=None, _configfile=None, _findExecutables=True, _logger=True
    ):
        SimQueue.__init__(self)
        ProtocolInterface.__init__(self)
        self._arg("jobname", "str", "Job name (identifier)", None, val.String())
        self._arg(
            "partition",
            "str",
            "The queue (partition) or list of queues to run on. If list, the one offering "
            "earliest initiation will be used.",
            self._defaults["partition"],
            val.String(),
            nargs="*",
        )
        self._arg(
            "priority", "str", "Job priority", self._defaults["priority"], val.String()
        )
        self._arg(
            "ngpu",
            "int",
            "Number of GPUs to use for a single job",
            self._defaults["ngpu"],
            val.Number(int, "0POS"),
        )
        self._arg(
            "ncpu",
            "int",
            "Number of CPUs to use for a single job",
            self._defaults["ncpu"],
            val.Number(int, "POS"),
        )
        self._arg(
            "memory",
            "int",
            "Amount of memory per job (MiB)",
            self._defaults["memory"],
            val.Number(int, "POS"),
        )
        self._arg(
            "gpumemory",
            "int",
            "Only run on GPUs with at least this much memory. Needs special setup of SLURM. "
            "Check how to define gpu_mem on SLURM.",
            None,
            val.Number(int, "0POS"),
        )
        self._arg(
            "walltime",
            "int",
            "Job timeout (minutes)",
            self._defaults["walltime"],
            val.Number(int, "POS"),
        )
        self._cmdDeprecated("environment", "envvars")
        self._arg(
            "mailtype",
            "str",
            "When to send emails. Separate options with commas like 'END,FAIL'.",
            None,
            val.String(),
        )
        self._arg("mailuser", "str", "User email address.", None, val.String())
        self._arg(
            "outputstream", "str", "Output stream.", "slurm.%N.%j.out", val.String()
        )
        self._arg(
            "errorstream", "str", "Error stream.", "slurm.%N.%j.err"
        ), val.String()
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
            "nodelist",
            "list",
            "A list of nodes on which to run every job at the *same time*! Careful! The jobs"
            " will be duplicated!",
            None,
            val.String(),
            nargs="*",
        )
        self._arg(
            "exclude",
            "list",
            "A list of nodes on which *not* to run the jobs. Use this to select nodes on "
            "which to allow the jobs to run on.",
            None,
            val.String(),
            nargs="*",
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
        self._arg(
            "account",
            "str",
            "Charge resources used by the jobs to specified account.",
            None,
            val.String(),
        )
        self._arg(
            "user",
            "str",
            "The SLURM user submitting and managing jobs",
            getpass.getuser(),
            val.String(),
        )
        self._arg(
            "useworkdir",
            "bool",
            "Set to False to not use a working dir",
            True,
            val.Boolean(),
        )
        self._arg(
            "nodes",
            "int",
            "Number of nodes to request",
            None,
            val.Number(int, "0POS"),
        )
        self._arg(
            "ntasks",
            "int",
            "Total number of tasks",
            None,
            val.Number(int, "0POS"),
        )
        self._arg(
            "ntasks_per_node",
            "int",
            "Number of tasks each node will run",
            None,
            val.Number(int, "0POS"),
        )

        # Load Slurm configuration profile
        loadConfig(self, "slurm", _configfile, _configapp, _logger)

        # Find executables
        if _findExecutables:
            self._qsubmit = SlurmQueue._find_binary("sbatch")
            self._qinfo = SlurmQueue._find_binary("sinfo")
            self._qcancel = SlurmQueue._find_binary("scancel")
            self._qstatus = SlurmQueue._find_binary("squeue")
            self._qjobinfo = SlurmQueue._find_binary("sacct", permissive=True)
            self._checkQueue()

    def _checkQueue(self):
        # Check if the slurm daemon is running by executing squeue
        try:
            ret = check_output([self._qstatus]).decode("ascii")
        except CalledProcessError as e:
            raise RuntimeError(
                f"SLURM squeue command failed with error: {e} and errorcode: {e.returncode}"
            )
        except Exception as e:
            raise RuntimeError(f"SLURM squeue command failed with error: {e}")

        if self._qjobinfo is not None:
            try:
                ret = check_output([self._qjobinfo]).decode("ascii")
                if "Slurm accounting storage is disabled" in ret:
                    raise RuntimeError(
                        "Slurm accounting is disabled. Cannot get detailed job info."
                    )
            except Exception as e:
                print(f"SLURM sacct command failed with error: {e}")

    @staticmethod
    def _find_binary(binary, permissive=False):
        ret = shutil.which(binary, mode=os.X_OK)
        if not ret:
            if permissive:
                return None
            raise FileNotFoundError(
                "Could not find required executable [{}]".format(binary)
            )
        ret = os.path.abspath(ret)
        return ret

    def _createJobScript(self, fname, workdir, runsh):
        from jobqueues.config import template_env

        workdir = os.path.abspath(workdir)
        sentinel = os.path.normpath(os.path.join(workdir, self._sentinel))

        # Move completed trajectories
        odir = None
        if self.datadir is not None:
            simname = os.path.basename(os.path.normpath(workdir))
            odir = os.path.abspath(os.path.join(self.datadir, simname))

        gpustring = None
        if self.ngpu != 0:
            gpustring = f"gpu:{self.ngpu}"
            if self.gpumemory is not None:
                gpustring += f",gpu_mem:{self.gpumemory}"

        prerun = self.prerun if self.prerun is not None else []
        errorstream = self.errorstream
        outputstream = self.outputstream
        if not self.useworkdir:
            workdir = "/tmp/"
            errorstream = None
            outputstream = None
            sentinel = None
        else:
            prerun += [f"cd {workdir}"]

        template = template_env.get_template("SLURM_job.sh.j2")
        job_str = template.render(
            jobname=self.jobname,
            partition=",".join(ensurelist(self.partition)),
            ncpu=self.ncpu,
            memory=self.memory,
            priority=self.priority,
            workdir=workdir,
            gpustring=gpustring,
            outputstream=outputstream,
            errorstream=errorstream,
            envvars=self.envvars,
            time=self.walltime,
            mailtype=self.mailtype,
            mailuser=self.mailuser,
            nodelist=",".join(ensurelist(self.nodelist))
            if self.nodelist is not None
            else None,
            exclude=",".join(ensurelist(self.exclude))
            if self.exclude is not None
            else None,
            account=self.account,
            sentinel=sentinel,
            prerun=prerun,
            runsh=runsh,
            odir=odir,
            trajext=self.trajext,
            nodes=self.nodes,
            ntasks=self.ntasks,
            ntasks_per_node=self.ntasks_per_node,
        )
        with open(fname, "w") as f:
            f.write(job_str)
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

        if self.partition is None:
            raise ValueError("The partition needs to be defined.")

        # if all folders exist, submit
        for i, d in enumerate(dirs):
            logger.info("Queueing " + d)

            if self.jobname is None:
                self.jobname = self._autoJobName(d)

            runscript = commands[i] if commands is not None else self._getRunScript(d)
            self._cleanSentinel(d)

            jobscript = os.path.abspath(os.path.join(d, "job.sh"))
            self._createJobScript(jobscript, d, runscript)
            try:
                ret = check_output([self._qsubmit, jobscript])
                logger.debug(ret.decode("ascii"))
            except CalledProcessError as e:
                logger.error(e.output)
                raise
            except Exception:
                raise

    def _robust_check_output(self, cmd, maxtries=3):
        # Attempts multiple times to execute the command before failing. This is to handle connection issues to SLURM
        import time

        tries = 0
        while tries < maxtries:
            try:
                ret = check_output(cmd)
            except CalledProcessError:
                if tries == (maxtries - 1):
                    raise
                tries += 1
                time.sleep(3)
                continue
            break
        return ret

    def inprogress(self):
        """Returns the sum of the number of running and queued workunits of the specific group in the engine.

        Returns
        -------
        total : int
            Total running and queued workunits
        """
        if self.jobname is None:
            raise ValueError("The jobname needs to be defined.")

        cmd = [
            self._qstatus,
            "-n",
            self.jobname,
            "-u",
            self.user,
        ]
        if self.partition is not None:
            cmd += ["--partition", ",".join(ensurelist(self.partition))]

        logger.debug(cmd)
        ret = self._robust_check_output(cmd).decode("ascii")
        logger.debug(ret)

        # Count the number of lines returned by squeue as number of "in progress" jobs
        lines = ret.splitlines()
        inprog = max(0, len(lines) - 1)

        # Check also with sacct because squeue sometimes fails to report the right number
        if self._qjobinfo is not None:
            try:
                res = self.jobInfo()
                if res is None:
                    return inprog
                info = [
                    key for key, val in res.items() if val["state"] in _inProgressStatus
                ]
                if len(info) != inprog:
                    logger.warning(
                        f"squeue and sacct gave different number of running jobs ({inprog}/{len(info)}) with name {self.jobname}. Using the max of the two."
                    )
                inprog = max(inprog, len(info))
            except Exception as e:
                logger.warning(f"Failed to get jobInfo with error: {e}")

        return inprog

    def stop(self):
        """Cancels all currently running and queued jobs"""
        if self.jobname is None:
            raise ValueError("The jobname needs to be defined.")

        if self.partition is not None:
            for q in ensurelist(self.partition):
                cmd = [self._qcancel, "-n", self.jobname, "-u", self.user, "-p", q]
                logger.debug(cmd)
                ret = check_output(cmd)
                logger.debug(ret.decode("ascii"))
        else:
            cmd = [self._qcancel, "-n", self.jobname, "-u", self.user]
            logger.debug(cmd)
            ret = check_output(cmd)
            logger.debug(ret.decode("ascii"))

    def jobInfo(self):
        if self.jobname is None:
            raise ValueError("The jobname needs to be defined.")

        cmd = [
            self._qjobinfo,
            "--name",
            self.jobname,
            "-u",
            self.user,
            "-o",
            "JobID,JobName,State,ExitCode,Reason,Timelimit",
            "-P",
            "-X",
        ]
        if self.partition is not None:
            cmd += ["--partition", ",".join(ensurelist(self.partition))]

        logger.debug(cmd)
        ret = self._robust_check_output(cmd).decode("ascii")
        logger.debug(ret)

        # TODO: Is there a specific exit code for this?
        if "Slurm accounting storage is disabled" in ret:
            return None

        lines = ret.splitlines()
        if len(lines) < 2:
            return None

        info = {}
        for line in lines[1:]:
            jobid, _, state, exitcode, reason, timelimit = line.split("|")

            if state in JOB_STATE_CODES:
                state = JOB_STATE_CODES[state]
            else:
                raise RuntimeError(f'Unknown SLURM job state "{state}"')

            info[jobid] = {
                "state": state,
                "exitcode": exitcode,
                "reason": reason,
                "timelimit": timelimit,
            }

        return info

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


class _TestSlurmQueue(unittest.TestCase):
    def test_config(self):
        from jobqueues.home import home
        import os

        configfile = os.path.join(home(), "config_slurm.yml")
        with open(configfile, "r") as f:
            reference = yaml.load(f, Loader=yaml.FullLoader)

        for appkey in reference:
            sq = SlurmQueue(
                _configapp=appkey, _configfile=configfile, _findExecutables=False
            )
            for key in reference[appkey]:
                assert (
                    sq.__getattribute__(key) == reference[appkey][key]
                ), f'Config setup of SlurmQueue failed on app "{appkey}" and key "{key}""'

    def test_submit_command(self):
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            sl = SlurmQueue(_findExecutables=False)
            sl.partition = "jobqueues_test"
            sl.ngpu = 2
            sl.gpumemory = 2000
            sl.exclude = ["node1", "node4"]
            sl.nodelist = ["node2"]
            sl.envvars = "TEST=3"
            sl.useworkdir = False
            try:
                sl.submit([tmpdir], commands=["sleep 5"])
            except Exception as e:
                print(e)
                pass

            with open(os.path.join(tmpdir, "job.sh"), "r") as f:
                joblines = f.readlines()

            reflines = [
                "#!/bin/bash\n",
                "#\n",
                "#SBATCH --job-name=tmpwnq0uoqw_28851\n",
                "#SBATCH --partition=jobqueues_test\n",
                "#SBATCH --cpus-per-task=1\n",
                "#SBATCH --mem=1000\n",
                "#SBATCH --priority=None\n",
                "#SBATCH -D /tmp/\n",
                "#SBATCH --gres=gpu:2,gpu_mem:2000\n",
                "#SBATCH --export=TEST=3\n",
                "#SBATCH --nodelist=node2\n",
                "#SBATCH --exclude=node1,node4\n",
                "\n",
                "\n",
                "\n",
                "sleep 5\n",
                "\n",
            ]
            skiplines = [2]

            assert len(joblines) == len(reflines)
            for i, (l1, l2) in enumerate(zip(reflines, joblines)):
                if i in skiplines:
                    continue
                assert (
                    l1 == l2
                ), f"Difference found in line {i} of job file: {l1} vs {l2}"

    def test_submit_folder(self):
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            with open(os.path.join(tmpdir, "run.sh"), "w") as f:
                f.write("sleep 5")
            os.chmod(os.path.join(tmpdir, "run.sh"), 0o700)

            sl = SlurmQueue(_findExecutables=False)
            sl.partition = "jobqueues_test"
            sl.ngpu = 2
            sl.gpumemory = 2000
            sl.exclude = ["node1", "node4"]
            sl.nodelist = ["node2"]
            sl.envvars = "TEST=3"
            try:
                sl.submit(tmpdir)
            except Exception as e:
                print(e)
                pass

            with open(os.path.join(tmpdir, "job.sh"), "r") as f:
                joblines = f.readlines()

            reflines = [
                "#!/bin/bash\n",
                "#\n",
                "#SBATCH --job-name=tmp8dj2zuya_44185\n",
                "#SBATCH --partition=jobqueues_test\n",
                "#SBATCH --cpus-per-task=1\n",
                "#SBATCH --mem=1000\n",
                "#SBATCH --priority=None\n",
                "#SBATCH -D tmpdir\n",
                "#SBATCH --gres=gpu:2,gpu_mem:2000\n",
                "#SBATCH --output=slurm.%N.%j.out\n",
                "#SBATCH --error=slurm.%N.%j.err\n",
                "#SBATCH --export=TEST=3\n",
                "#SBATCH --nodelist=node2\n",
                "#SBATCH --exclude=node1,node4\n",
                "\n",
                'trap "touch tmpdir/jobqueues.done" EXIT SIGTERM\n',
                "\n",
                "cd tmpdir\n",
                "\n",
                "tmpdir/run.sh\n",
                "\n",
            ]
            skiplines = [2]

            assert len(joblines) == len(reflines)
            for i, (l1, l2) in enumerate(zip(reflines, joblines)):
                l1 = l1.replace(tmpdir, "tmpdir")
                l2 = l2.replace(tmpdir, "tmpdir")
                if i in skiplines:
                    continue
                assert (
                    l1 == l2
                ), f"Difference found in line {i} of job file: {l1} vs {l2}"


if __name__ == "__main__":
    unittest.main(verbosity=2)
