# (c) 2015-2019 Acellera Ltd http://www.acellera.com
# All Rights Reserved
# Distributed under HTMD Software License Agreement
# No redistribution in whole or part
#
import json
import logging
import os
import shutil
import sys
import tempfile
import time
import zipfile

from jobqueues.simqueue import SimQueue
from protocolinterface import ProtocolInterface, val
from jobqueues.config import loadConfig

logger = logging.getLogger(__name__)


def _symlinkorcopy(ff, targetdir, symlink):
    if symlink:
        relpath = os.path.relpath(ff, os.path.dirname(os.path.abspath(targetdir)))
        os.symlink(relpath, targetdir)
    else:
        shutil.copytree(ff, targetdir)


class PlayQueue(SimQueue, ProtocolInterface):
    def __init__(
        self, _configapp=None, _configfile=None, _findExecutables=True, _logger=True
    ):
        from playmolecule import Session, Job

        SimQueue.__init__(self)
        ProtocolInterface.__init__(self)

        self._arg(
            "parentjob",
            "playmolecule.job.Job",
            "Spawn all jobs as children of this job",
            default=None,
            required=False,
            validator=val.Object(Job),
        )
        self._arg(
            "session",
            "playmolecule.session.Session",
            "The current PMWS Session object",
            required=True,
            validator=val.Object(Session),
        )
        self._arg("jobname", "str", "Job name (identifier)", None, val.String())
        self._arg("group", "str", "Group name (identifier)", None, val.String())
        self._arg(
            "ngpu",
            "int",
            "Number of GPUs",
            default=0,
            validator=val.Number(int, "0POS"),
        )
        self._arg(
            "ncpu",
            "int",
            "Number of CPUs",
            default=1,
            validator=val.Number(int, "0POS"),
        )
        self._arg(
            "memory",
            "int",
            "Amount of memory (MB)",
            default=1000,
            validator=val.Number(int, "POS"),
        )
        self._arg("app", "str", "App name", required=True, validator=val.String())
        self._arg(
            "configname",
            "str",
            "Name of the file containing the individual job configurations yaml or json. Not a filepath, just the name. All submitted folders must contain this file.",
            None,
            val.String(),
        )
        self._arg(
            "retrievedir",
            "str",
            "Directory in which to retrieve the results of jobs",
            None,
            val.String(),
        )
        self._arg(
            "datadir",
            "str",
            "Directory in which to copy or symlink the output directory.",
            None,
            val.String(),
        )
        self._arg(
            "symlink",
            "bool",
            "Set to False to copy instead of symlink the directories from the retrievedir to datadir",
            True,
            val.Boolean(),
        )
        self._arg(
            "copy",
            "list",
            "A list of file names or globs for the files to copy or symlink from retrievedir to datadir.",
            ("/",),
            val.String(),
            nargs="*",
        )

        loadConfig(self, "playmolecule", _configfile, _configapp, _logger)

    def submit(self, folders):
        from jobqueues.util import ensurelist
        import uuid

        if self.group is None:
            self.group = uuid.uuid4()

        for f in ensurelist(folders):
            if self.jobname is None:
                name = os.path.basename(os.path.abspath(f))
            else:
                name = self.jobname

            job = self.session.startApp(self.app)
            job.readArguments(os.path.join(f, self.configname))
            job.name = name
            job.group = self.group
            job.submit(
                childOf=self.parentjob._execid if self.parentjob is not None else None
            )

    def _getJobs(self, returnDict, status):
        if self.parentjob is not None:
            jobs = self.parentjob.getChildren(returnDict=True, status=status)
        else:
            if self.group is None:
                raise RuntimeError(
                    "If no parent job is specified you need to specify a job group."
                )
            jobs = self.session.getJobsByGroup(
                self.group, status=status, returnDict=True
            )
        if returnDict:
            return jobs
        else:
            return jobs[0], jobs[1]

    def inprogress(self):
        from playmolecule import JobStatus

        prog_status = (
            JobStatus.RUNNING,
            JobStatus.WAITING_DATA,
            JobStatus.QUEUED,
            JobStatus.SLEEPING,
        )

        jobs = self._getJobs(returnDict=True, status=prog_status)
        return len(jobs)

    def retrieve(self):
        import shutil
        from glob import glob
        from playmolecule import JobStatus
        from jobqueues.util import ensurelist

        retrievedir = self.retrievedir if self.retrievedir is not None else self.datadir

        jobs = self._getJobs(
            returnDict=False, status=(JobStatus.COMPLETED, JobStatus.ERROR)
        )

        for job in jobs:
            targetdir = os.path.join(self.datadir, job.name)

            retdir = job.retrieve(path=retrievedir, skip=True)

            if job.getStatus() != JobStatus.ERROR:
                for fglob in ensurelist(self.copy):
                    currglob = os.path.join(retdir, fglob)
                    if "*" in currglob:
                        for ff in glob(currglob):
                            _symlinkorcopy(ff, targetdir, self.symlink)
                    else:
                        _symlinkorcopy(currglob, targetdir, self.symlink)

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
