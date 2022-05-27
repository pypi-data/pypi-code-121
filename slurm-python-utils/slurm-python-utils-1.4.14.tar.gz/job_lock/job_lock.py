import argparse, contextlib, datetime, itertools, os, pathlib, random, re, subprocess, sys, time, uuid
if sys.platform != "cygwin":
  import psutil

def rm_missing_ok(path):
  if sys.version_info >= (3, 8):
    return path.unlink(missing_ok=True)
  else:
    try:
      return path.unlink()
    except FileNotFoundError:
      pass

def SLURM_JOBID():
  return os.environ.get("SLURM_JOBID", None)
def CONDOR_JOBINFO():
  if "_CONDOR_SCRATCH_DIR" not in os.environ: return None
  try:
    return os.environ["CONDOR_CLUSTERID"], os.environ["CONDOR_PROCID"]
  except KeyError:
    raise OSError("Please put 'environment = CONDOR_cLUSTERID=$(ClusterId) CONDOR_PROCID=$(ProcId)' in your condor submission script")

def cpuid():
  node = uuid.getnode()
  #least significant bit of the first octet is not set --> this is a hardware address
  if not node & 2**40:
    return node

  #otherwise getnode gave us a random number!
  for filename in "/etc/machine-id", "/var/lib/dbus/machine-id":
    try:
      with open(filename) as f:
        machineid = f.read().strip()
    except FileNotFoundError:
      continue
    return uuid.UUID(machineid).int

  raise ValueError("Couldn't find a cpuid using any of the methods we know about")

def jobinfo():
  slurm = SLURM_JOBID()
  if slurm is not None:
    return "SLURM", 0, slurm
  condor = CONDOR_JOBINFO()
  if condor is not None:
    return "CONDOR", condor[0], condor[1]
  return sys.platform, cpuid(), os.getpid()

class JobLock(object):
  defaultcorruptfiletimeout = datetime.timedelta(hours=24)

  def __init__(self, filename, *, outputfiles=[], checkoutputfiles=True, inputfiles=[], checkinputfiles=True, prevsteplockfiles=[], corruptfiletimeout=None, mkdir=False, dosqueue=True, cachesqueue=True):
    self.filename = pathlib.Path(filename)
    self.outputfiles = [pathlib.Path(_) for _ in outputfiles]
    self.inputfiles = [pathlib.Path(_) for _ in inputfiles]
    self.prevsteplockfiles = [pathlib.Path(_) for _ in prevsteplockfiles]
    self.checkoutputfiles = outputfiles and checkoutputfiles
    self.checkinputfiles = inputfiles and checkinputfiles
    self.checkprevsteplockfiles = prevsteplockfiles
    self.removed_failed_job = False
    if corruptfiletimeout is None:
      corruptfiletimeout = self.defaultcorruptfiletimeout
    self.corruptfiletimeout = corruptfiletimeout
    self.mkdir = mkdir
    self.dosqueue = dosqueue
    self.cachesqueue = cachesqueue
    self.sublockkwargs = {
      "checkoutputfiles": checkoutputfiles,
      "checkinputfiles": checkinputfiles,
      "mkdir": mkdir,
      "dosqueue": dosqueue,
      "cachesqueue": cachesqueue,
      "corruptfiletimeout": corruptfiletimeout,
    }
    self.__reset()

  def __reset(self):
    self.fd = self.f = None
    self.bool = False
    self.__inputsexist = self.__outputsexist = self.__prevsteplockfilesexist = self.__oldjobinfo = self.__iterative_lock = None

  @property
  def wouldbevalid(self):
    if self: return True
    with self:
      return bool(self)

  def runningjobinfo(self, exceptions=False, compatibility=True):
    try:
      with open(self.filename) as f:
        contents = f.read()
        try:
          jobtype, cpuid, jobid = contents.split()
        except ValueError:
          if not compatibility: raise
          #compatibility with older version of job_lock
          jobtype = "SLURM"
          cpuid = 0
          jobid = int(contents)
        cpuid = int(cpuid)
        jobid = int(jobid)
        return jobtype, cpuid, jobid
    except (IOError, OSError, ValueError):
      if exceptions: raise
      return None, None, None

  @property
  def outputsexist(self):
    return self.__outputsexist

  @property
  def inputsexist(self):
    return self.__inputsexist

  @property
  def prevsteplockfilesexist(self):
    return self.__prevsteplockfilesexist

  @property
  def oldjobinfo(self):
    return self.__oldjobinfo

  @property
  def iterative_lock(self):
    return self.__iterative_lock
  @property
  def iterative_lock_debuginfo(self):
    if self.iterative_lock is None: return None
    return self.iterative_lock.debuginfo

  def __open(self):
    self.fd = os.open(self.filename, os.O_CREAT | os.O_EXCL | os.O_WRONLY)

  @property
  def iterative_lock_filename(self):
    match = re.match("[.]lock(?:_([0-9]+))?$", self.filename.suffix)
    if match:
      n = match.group(1)
      if n is None: n = 1
      n = int(n)
      if n > 1:
        #sleep by a random amount less than 1/100 of a second to lower the probability of two jobs competing indefinitely
        time.sleep(random.random()/100)
      return self.filename.with_suffix(f".lock_{n+1}")
    else:
      return self.filename.with_suffix(self.filename.suffix+".lock")

  def clean_up_iterative_locks(self):
    iterative_lock_filename = self.iterative_lock_filename

    def n_from_filename(filename):
      match = re.match("[.]lock(?:_([0-9]+))?$", filename.suffix)
      if not match: return -float("inf")
      n = match.group(1)
      if n is None: n = 1
      return int(n)

    my_n = n_from_filename(iterative_lock_filename)-1
    if my_n > 1: return #they'll be cleaned up when the non-iterative version cleans them up

    filenames = iterative_lock_filename.parent.glob(iterative_lock_filename.with_suffix(".lock").name+"*")
    filenames = [_ for _ in filenames if n_from_filename(_) > my_n]
    if not filenames: return
    filenames.sort(key=n_from_filename, reverse=True)

    with JobLock(self.filename.with_suffix(".cleanup.lock"), **self.sublockkwargs) as lock:
      if not lock: return
      for filename in filenames:
        with JobLock(filename, **self.sublockkwargs) as lock:
          if not lock:
            break

  def __enter__(self):
    self.removed_failed_job = False
    if self.checkoutputfiles and not self.filename.exists():
      self.__outputsexist = {_: _.exists() for _ in self.outputfiles}
      if all(self.outputsexist.values()):
        self.clean_up_iterative_locks()
        return self
    if self.checkinputfiles:
      self.__inputsexist = {_: _.exists() for _ in self.inputfiles}
      if not all(self.inputsexist.values()):
        return self
    if self.checkprevsteplockfiles:
      self.__prevsteplockfilesexist = {_: not JobLock(_, **self.sublockkwargs).wouldbevalid for _ in self.prevsteplockfiles}
      if any(self.prevsteplockfilesexist.values()):
        return self
    if self.mkdir:
      self.filename.parent.mkdir(parents=True, exist_ok=True)
    try:
      self.__open()
    except FileExistsError:
      #check if the job died without removing the lock
      #however this needs another job lock, because it has
      #a race condition: two jobs could be looking if the previous
      #job failed at the same time, and one of them could remove
      #the lock created by the other one
      with JobLock(self.iterative_lock_filename, **self.sublockkwargs) as iterative_lock:
        self.__iterative_lock = iterative_lock
        if not iterative_lock: return self
        try:
          self.__oldjobinfo = self.runningjobinfo(exceptions=True)
        except (IOError, OSError) as e:
          self.__oldjobinfo = e
          try:
            self.__open()
          except FileExistsError:
            return self
        except ValueError as e:
          self.__oldjobinfo = e
          if self.corruptfiletimeout is not None:
            modified = datetime.datetime.fromtimestamp(self.filename.stat().st_mtime)
            now = datetime.datetime.now()
            if now - modified >= self.corruptfiletimeout:
              for outputfile in self.outputfiles:
                rm_missing_ok(outputfile)
              rm_missing_ok(self.filename)
              self.removed_failed_job = True
              try:
                self.__open()
              except FileExistsError:
                return self
            else:
              return self
          else:
            return self
        else:
          if jobfinished(*self.oldjobinfo, dosqueue=self.dosqueue, cachesqueue=self.cachesqueue):
            for outputfile in self.outputfiles:
              rm_missing_ok(outputfile)
            rm_missing_ok(self.filename)
            self.removed_failed_job = True
            try:
              self.__open()
            except FileExistsError:
              return self
          else:
            return self

    self.f = os.fdopen(self.fd, 'w')

    message = " ".join(str(_) for _ in jobinfo())
    try:
      self.f.write(message+"\n")
    except (IOError, OSError):
      pass
    try:
      self.f.close()
    except (IOError, OSError):
      pass
    self.bool = True
    return self

  def __exit__(self, exc_type, exc, traceback):
    if self:
      #clean up output files if job failed
      if exc is not None:
        for outputfile in self.outputfiles:
          rm_missing_ok(outputfile)
      #clean up iterative locks whose jobs died
      self.clean_up_iterative_locks()
      #remove this lock file
      rm_missing_ok(self.filename)
    self.__reset()

  def __bool__(self):
    return self.bool

  @property
  def debuginfo(self):
    return {
      "outputsexist": self.outputsexist,
      "inputsexist": self.inputsexist,
      "prevsteplockfilesexist": self.prevsteplockfilesexist,
      "oldjobinfo": self.oldjobinfo,
      "removed_failed_job": self.removed_failed_job,
      "iterative_lock_debuginfo": self.iterative_lock_debuginfo,
    }

__knownrunningslurmjobs = set()

def clear_slurm_running_jobs_cache():
  __knownrunningslurmjobs.clear()

def jobfinished(jobtype, cpuid, jobid, *, dosqueue=True, cachesqueue=True):
  if jobtype == "SLURM":
    if cachesqueue and jobid in __knownrunningslurmjobs: return False #assume job is still running
    if not dosqueue: return None #don't know if the job finished
    try:
      output = subprocess.check_output(["squeue", "--job", str(jobid), "--format", "jobid,state", "--noheader"], stderr=subprocess.STDOUT)
      for line in output.split(b"\n"):
        line = line.strip()
        if not line: continue
        try:
          runningjobid, state = line.split()
        except ValueError:
          return None #don't know if the job finished, probably a temporary glitch in squeue
        runningjobid = int(runningjobid)
        if runningjobid == jobid:
          state = state.decode("ascii")
          if state in ("PENDING", "PD"):
            #this can happen if the job was cancelled due to node failure and was automatically resubmitted
            return True #job is not currently running
          else:
            __knownrunningslurmjobs.add(jobid)
            return False #job is still running
      return True #job is finished
    except FileNotFoundError:  #no squeue
      return None  #we don't know if the job finished
    except subprocess.CalledProcessError as e:
      if b"slurm_load_jobs error: Invalid job id specified" in e.output:
        return True #job is finished
      print(e.output)
      raise
  elif jobtype == "CONDOR":
    if not dosqueue: return None #don't know if the job finished
    try:
      output = subprocess.check_output(["condor_q", "-nobatch", "-run"], stderr=subprocess.STDOUT)
      for line in output.split(b"\n"):
        line = line.strip()
        if not line: continue
        if line.startswith(b"-- Schedd:"): continue
        if line.startswith(b"ID "): continue
        runningjobid = line.split()[0]
        try:
          runningclusterid, runningprocid = (int(_) for _ in runningjobid.split(b"."))
        except ValueError:
          return None #don't know if the job finished, probably a temporary glitch in squeue
        if runningclusterid == cpuid and runningprocid == jobid:
          return False #job is still running
      return True #job is finished
    except FileNotFoundError:  #no squeue
      return None  #we don't know if the job finished
    except subprocess.CalledProcessError as e:
      print(e.output)
      raise
  else:
    myjobtype, mycpuid, myjobid = jobinfo()
    if myjobtype != jobtype: return None #we don't know if the job finished
    if mycpuid != cpuid: return None #we don't know if the job finished
    if jobid == myjobid: return False #job is still running
    if sys.platform == "cygwin":
      psoutput = subprocess.check_output(["ps", "-s"])
      lines = psoutput.split(b"\n")
      for line in lines[1:]:
        if not line: continue
        if int(line.split(maxsplit=1)[0]) == jobid:
          return False #job is still running
      return True #job is finished
    else:
      for process in psutil.process_iter():
        if jobid == process.pid:
          return False #job is still running
      return True #job is finished

class JobLockAndWait(JobLock):
  defaultsilent = False

  def __init__(self, name, delay, *, printmessage=None, task="doing this", maxiterations=1000, silent=None, waitforinputs=False, **kwargs):
    super().__init__(name, **kwargs)
    self.delay = delay
    if printmessage is None:
      printmessage = "Another process is already {task}.  Waiting {delay} seconds."
    printmessage = printmessage.format(delay=delay, task=task)
    self.__printmessage = printmessage
    if silent is None:
      silent = self.defaultsilent
    self.__silent = silent
    self.__waitforinputs = waitforinputs
    self.niterations = 0
    self.maxiterations = maxiterations

  def __enter__(self):
    for self.niterations in itertools.count(1):
      if self.niterations > self.maxiterations:
        raise RuntimeError(f"JobLockAndWait still did not succeed after {self.maxiterations} iterations")
      result = super().__enter__()
      if result:
        return result
      elif self.checkoutputfiles and self.outputsexist is not None and all(self.outputsexist.values()):
        return result
      elif self.checkinputfiles and self.inputsexist is not None:
        missinginputs = [k for k, v in self.inputsexist.items() if not v]
        if missinginputs:
          message = f"Some input files are missing: {', '.join(str(_) for _ in missinginputs)}."
          if self.__waitforinputs:
            if not self.__silent: print(f"{message} Waiting {self.delay} seconds.")
          else:
            raise FileNotFoundError(message)
      else:
        if not self.__silent: print(self.__printmessage)
      time.sleep(self.delay)

def clean_up_old_job_locks(*folders, glob="*.lock_*", howold=datetime.timedelta(days=7), dryrun=False, silent=False):
  for folder in folders:
    folder = pathlib.Path(folder)
    all_locks = sorted(folder.rglob(glob))
    all_first_order_locks = sorted({filename.with_suffix(filename.suffix.split("_")[0]) for filename in all_locks})
    locks_dict = {first_order_lock: {lock for lock in all_locks if lock.with_suffix(lock.suffix.split("_")[0]) == first_order_lock} for first_order_lock in all_first_order_locks}

    remove = []
    dontremove = []
    for first_order_lock_file, lock_files in sorted(locks_dict.items()):
      try:
        modified = max(datetime.datetime.fromtimestamp(file.stat().st_mtime) for file in lock_files)
      except FileNotFoundError:
        dontremove.append(first_order_lock_file)
        continue
      now = datetime.datetime.now()
      if now - modified < howold:
        dontremove.append(first_order_lock_file)
      else:
        remove.append(first_order_lock_file)

    if dryrun:
      verb = "Would remove"
      dontverb = "Would not remove"
    else:
      verb = "Removing"
      dontverb = "Keeping"

    if silent:
      def doprint(*args, **kwargs): pass
    else:
      doprint = print

    doprint(f"{verb} the following locks (and their iterations):")
    for _ in remove:
      doprint(_)
      if not dryrun:
        with JobLock(_, corruptfiletimeout=howold): pass
    doprint(f"{dontverb} the following locks (and their iterations):")
    for _ in dontremove: doprint(_)

def clean_up_old_job_locks_argparse(args=None):
  p = argparse.ArgumentParser()
  p.add_argument("folders", type=pathlib.Path, nargs="+", metavar="folder")
  p.add_argument("--glob", default="*.lock_*")
  p.add_argument("--hours-old", type=lambda x: datetime.timedelta(hours=float(x)), default=datetime.timedelta(days=7), dest="howold")
  p.add_argument("--dry-run", dest="dryrun", action="store_true")
  p.add_argument("--silent", action="store_true")
  args = p.parse_args(args=args)
  folders = args.__dict__.pop("folders")
  return clean_up_old_job_locks(*folders, **args.__dict__)

class MultiJobLock(contextlib.ExitStack):
  """
  JobLock with multiple files.
  If any of them fail, all the ones that previously succeeded are closed
  and the whole thing is considered to fail.
  """
  def __init__(self, *filenames, **kwargs):
    super().__init__()
    self.__filenames = filenames
    self.__kwargs = kwargs

  def __enter__(self):
    super().__enter__()
    for filename in self.__filenames:
      if not self.enter_context(JobLock(filename, **self.__kwargs)):
        self.close()
        return False
    return True
