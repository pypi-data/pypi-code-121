# (c) 2015-2022 Acellera Ltd http://www.acellera.com
# All Rights Reserved
# Distributed under HTMD Software License Agreement
# No redistribution in whole or part
#
import logging
import os
import shutil
import sys
import tempfile
import time
import yaml
from jobqueues.simqueue import SimQueue
from protocolinterface import ProtocolInterface
from protocolinterface.validators import Number
from playmolecule.job import JobStatus

logger = logging.getLogger(__name__)


class PlayQueue(SimQueue, ProtocolInterface):
    def __init__(self, session, parent_job, outdir):
        SimQueue.__init__(self)
        ProtocolInterface.__init__(self)

        self._arg(
            "ngpu", "int", "Number of GPUs", default=0, validator=Number(int, "0POS")
        )
        self._arg(
            "ncpu", "int", "Number of CPUs", default=1, validator=Number(int, "0POS")
        )
        self._arg(
            "memory",
            "int",
            "Amount of memory (MB)",
            default=1000,
            validator=Number(int, "POS"),
        )
        self._arg(
            "max_jobs",
            "int",
            "Maximum number of concurent jobs",
            default=sys.maxsize,
            validator=Number(int, "POS"),
        )

        self._parent_job = parent_job
        self._session = session
        self._outdir = outdir

    def submit(self, dirs):
        logger.info(f"Maximum number of concurrent jobs: {self.max_jobs}")

        dirs = [dirs] if isinstance(dirs, str) else dirs
        for dir_ in dirs:
            # Delay submission
            while self.inprogress() >= self.max_jobs:
                time.sleep(5)

            with open(os.path.join(dir_, "config.yaml"), "r") as f:
                config = yaml.load(f, Loader=yaml.FullLoader)

            # Submit a job
            job = self._session.start_app(config["app"])
            # TODO: Set the arguments!
            job.submit(_logger=False, child_of=self._parent_job._execid)

            logger.info(f"Submitted job {job._execid}:")
            logger.info(f"    App name: {self.app}")
            logger.info(f"    Input directory: {dir_}")
            logger.info(
                f"    Resources: {self.ngpu} GPUs, {self.ncpu} CPUs, {self.memory} MB of memory"
            )

    def inprogress(self):
        not_complete = set(JobStatus) - set((JobStatus.COMPLETED, JobStatus.ERROR))
        children = self._parent_job.get_children(
            status=not_complete, return_dict=True, _logger=False
        )
        return len(children)

    def retrieve(self):
        children = self._parent_job.get_children(
            status=(JobStatus.COMPLETED, JobStatus.ERROR),
            return_dict=False,
            _logger=False,
        )
        for job in children:
            if job.get_status(_logger=False) == JobStatus.ERROR:
                logger.info(f"Job {job._execid} failed")
                continue

            with tempfile.TemporaryDirectory() as tmpDir:
                logger.info(f"Job {job._execid} completed")
                outDir = job.retrieve(_logger=False, path=tmpDir)
                for file in os.listdir(outDir):
                    shutil.copy(os.path.join(outDir, file), self._outdir)
                logger.info(f"    Retrieved results to {self._outdir}")

    def stop(self):
        raise NotImplementedError()

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
