import contextlib, datetime, multiprocessing, os, pathlib, subprocess, tempfile, time, unittest
from job_lock import clean_up_old_job_locks, clear_slurm_running_jobs_cache, JobLock, JobLockAndWait, jobinfo, MultiJobLock, slurm_clean_up_temp_dir, slurm_rsync_input, slurm_rsync_output

class TestJobLock(unittest.TestCase, contextlib.ExitStack):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    try:
      self.enter_context(contextlib.nullcontext())
    except AttributeError:
      contextlib.ExitStack.__init__(self)
    self.maxDiff = None
  def setUp(self):
    self.tmpdir = pathlib.Path(self.enter_context(tempfile.TemporaryDirectory()))
    self.bkpenviron = os.environ.copy()
    self.slurm_tmpdir = self.tmpdir/"slurm_tmpdir"
    self.slurm_tmpdir.mkdir()
    os.environ["TMPDIR"] = os.fspath(self.slurm_tmpdir)
    clear_slurm_running_jobs_cache()
  def tearDown(self):
    del self.tmpdir
    self.close()
    os.environ.clear()
    os.environ.update(self.bkpenviron)

  def testJobLock(self):
    with JobLock(self.tmpdir/"lock1.lock") as lock1:
      self.assertTrue(lock1)
      self.assertEqual(lock1.iterative_lock_filename, self.tmpdir/"lock1.lock_2")
      with JobLock(self.tmpdir/"lock2.lock") as lock2:
        self.assertTrue(lock2)
      with JobLock(self.tmpdir/"lock1.lock") as lock3:
        self.assertFalse(lock3)
        self.assertEqual(lock3.debuginfo, {"outputsexist": None, "inputsexist": None, "prevsteplockfilesexist": None, "oldjobinfo": jobinfo(), "removed_failed_job": False, "iterative_lock_debuginfo": {"inputsexist": None, "iterative_lock_debuginfo": None, "oldjobinfo": None, "outputsexist": None, "prevsteplockfilesexist": None, "removed_failed_job": False}})

  def testMultiJobLock(self):
    fn1 = self.tmpdir/"lock1.lock"
    fn2 = self.tmpdir/"lock2.lock"

    with MultiJobLock(fn1, fn2) as locks:
      self.assertTrue(locks)
      self.assertTrue(fn1.exists())
      self.assertTrue(fn2.exists())

    with JobLock(fn1):
      with MultiJobLock(fn1, fn2) as locks:
        self.assertFalse(locks)
        self.assertTrue(fn1.exists())
        self.assertFalse(fn2.exists())

    with JobLock(fn2):
      with MultiJobLock(fn1, fn2) as locks:
        self.assertFalse(locks)
        self.assertFalse(fn1.exists())
        self.assertTrue(fn2.exists())

  def testInputFiles(self):
    fn1 = self.tmpdir/"lock1.lock"
    input1 = self.tmpdir/"inputfile1.txt"
    input2 = self.tmpdir/"inputfile2.txt"

    with JobLock(fn1, inputfiles=[input1, input2]) as lock:
      self.assertFalse(lock)
      self.assertEqual(lock.debuginfo, {"inputsexist": {input1: False, input2: False}, "outputsexist": None, "prevsteplockfilesexist": None, "oldjobinfo": None, "removed_failed_job": False, "iterative_lock_debuginfo": None})
    input1.touch()
    with JobLock(fn1, inputfiles=[input1, input2]) as lock:
      self.assertFalse(lock)
      self.assertEqual(lock.debuginfo, {"inputsexist": {input1: True, input2: False}, "outputsexist": None, "prevsteplockfilesexist": None, "oldjobinfo": None, "removed_failed_job": False, "iterative_lock_debuginfo": None})
    with JobLock(fn1, inputfiles=[input1]) as lock:
      self.assertTrue(lock)
      self.assertEqual(lock.debuginfo, {"inputsexist": {input1: True}, "outputsexist": None, "prevsteplockfilesexist": None, "oldjobinfo": None, "removed_failed_job": False, "iterative_lock_debuginfo": None})

    input2.touch()
    with JobLock(fn1, inputfiles=[input1, input2]) as lock:
      self.assertTrue(lock)
      self.assertEqual(lock.debuginfo, {"inputsexist": {input1: True, input2: True}, "outputsexist": None, "prevsteplockfilesexist": None, "oldjobinfo": None, "removed_failed_job": False, "iterative_lock_debuginfo": None})

  def testOutputFiles(self):
    fn1 = self.tmpdir/"lock1.lock"
    fn2 = self.tmpdir/"lock1.lock_2"
    output1 = self.tmpdir/"outputfile1.txt"
    output2 = self.tmpdir/"outputfile2.txt"

    with open(fn2, "w") as f:
      f.write("SLURM 0 1234568")

    with JobLock(fn1, outputfiles=[output1, output2]) as lock:
      self.assertTrue(lock)
      self.assertEqual(lock.debuginfo, {"outputsexist": {output1: False, output2: False}, "inputsexist": None, "prevsteplockfilesexist": None, "oldjobinfo": None, "removed_failed_job": False, "iterative_lock_debuginfo": None})
    output1.touch()
    with JobLock(fn1, outputfiles=[output1, output2]) as lock:
      self.assertTrue(lock)
      self.assertEqual(lock.debuginfo, {"outputsexist": {output1: True, output2: False}, "inputsexist": None, "prevsteplockfilesexist": None, "oldjobinfo": None, "removed_failed_job": False, "iterative_lock_debuginfo": None})
    with JobLock(fn1, outputfiles=[output1]) as lock:
      self.assertFalse(lock)
      self.assertEqual(lock.debuginfo, {"outputsexist": {output1: True}, "inputsexist": None, "prevsteplockfilesexist": None, "oldjobinfo": None, "removed_failed_job": False, "iterative_lock_debuginfo": None})

    output2.touch()
    with JobLock(fn1, outputfiles=[output1, output2]) as lock:
      self.assertFalse(lock)
      self.assertEqual(lock.debuginfo, {"outputsexist": {output1: True, output2: True}, "inputsexist": None, "prevsteplockfilesexist": None, "oldjobinfo": None, "removed_failed_job": False, "iterative_lock_debuginfo": None})
    self.assertTrue(fn2.exists()) #should not have cleaned up the iterative locks

    dummysqueue = """
      #!/bin/bash
      echo '
           1234567   RUNNING
      '
    """.lstrip()
    with open(self.tmpdir/"squeue", "w") as f:
      f.write(dummysqueue)
    (self.tmpdir/"squeue").chmod(0o0777)
    os.environ["PATH"] = f"{self.tmpdir}:"+os.environ["PATH"]

    with open(fn1, "w") as f:
      f.write("SLURM 0 1234567")
    with JobLock(fn1, outputfiles=[output1, output2]) as lock:
      self.assertFalse(lock)
      self.assertEqual(lock.debuginfo, {"outputsexist": None, "inputsexist": None, "prevsteplockfilesexist": None, "oldjobinfo": ("SLURM", 0, 1234567), "removed_failed_job": False, "iterative_lock_debuginfo": {"inputsexist": None, "iterative_lock_debuginfo": None, "oldjobinfo": None, "outputsexist": None, "prevsteplockfilesexist": None, "removed_failed_job": True}})
    self.assertTrue(output1.exists())
    self.assertTrue(output2.exists())
    self.assertFalse(fn2.exists()) #should have cleaned up the iterative locks

    with open(fn1, "w") as f:
      f.write("SLURM 0 1234568")
    with open(fn2, "w") as f:
      f.write("SLURM 0 1234568")
    with JobLock(fn1, outputfiles=[output1, output2], dosqueue=False) as lock:
      self.assertFalse(lock)
      self.assertEqual(lock.debuginfo, {"outputsexist": None, "inputsexist": None, "prevsteplockfilesexist": None, "oldjobinfo": None, "removed_failed_job": False, "iterative_lock_debuginfo": {"inputsexist": None, "iterative_lock_debuginfo": None, "oldjobinfo": None, "outputsexist": None, "prevsteplockfilesexist": None, "removed_failed_job": False}})
    self.assertTrue(fn1.exists())
    self.assertTrue(fn2.exists())
    with JobLock(fn1, outputfiles=[output1, output2]) as lock:
      self.assertTrue(lock)
      self.assertEqual(lock.debuginfo, {"outputsexist": None, "inputsexist": None, "prevsteplockfilesexist": None, "oldjobinfo": ("SLURM", 0, 1234568), "removed_failed_job": True, "iterative_lock_debuginfo": {"inputsexist": None, "iterative_lock_debuginfo": None, "oldjobinfo": None, "outputsexist": None, "prevsteplockfilesexist": None, "removed_failed_job": True}})
    self.assertFalse(output1.exists())
    self.assertFalse(output2.exists())

  def testPrevStepLockFiles(self):
    fn1 = self.tmpdir/"lock1.lock"
    fn2 = self.tmpdir/"lock2.lock"

    with JobLock(fn2, prevsteplockfiles=[fn1]) as lock:
      self.assertTrue(lock)
      self.assertEqual(lock.debuginfo, {"outputsexist": None, "inputsexist": None, "prevsteplockfilesexist": {fn1: False}, "oldjobinfo": None, "removed_failed_job": False, "iterative_lock_debuginfo": None})

    with JobLock(fn1) as lock:
      self.assertTrue(lock)
      with JobLock(fn2, prevsteplockfiles=[fn1]) as lock2:
        self.assertFalse(lock2)
        self.assertEqual(lock2.debuginfo, {"outputsexist": None, "inputsexist": None, "prevsteplockfilesexist": {fn1: True}, "oldjobinfo": None, "removed_failed_job": False, "iterative_lock_debuginfo": None})

    dummysqueue = """
      #!/bin/bash
      echo '
           1234567   RUNNING
      '
    """.lstrip()
    with open(self.tmpdir/"squeue", "w") as f:
      f.write(dummysqueue)
    (self.tmpdir/"squeue").chmod(0o0777)
    os.environ["PATH"] = f"{self.tmpdir}:"+os.environ["PATH"]

    with open(fn1, "w") as f:
      f.write("SLURM 0 1234567")

    with JobLock(fn2, prevsteplockfiles=[fn1]) as lock:
      self.assertFalse(lock)
      self.assertEqual(lock.debuginfo, {"outputsexist": None, "inputsexist": None, "prevsteplockfilesexist": {fn1: True}, "oldjobinfo": None, "removed_failed_job": False, "iterative_lock_debuginfo": None})

    with open(fn1, "w") as f:
      f.write("SLURM 0 1234568")

    with JobLock(fn2, prevsteplockfiles=[fn1]) as lock:
      self.assertTrue(lock)
      self.assertEqual(lock.debuginfo, {"outputsexist": None, "inputsexist": None, "prevsteplockfilesexist": {fn1: False}, "oldjobinfo": None, "removed_failed_job": False, "iterative_lock_debuginfo": None})

  def testRunningJobs(self):
    jobtype, cpuid, jobid = jobinfo()
    with open(self.tmpdir/"lock1.lock", "w") as f:
      f.write(f"{jobtype} {cpuid} {jobid}")
    with open(self.tmpdir/"lock2.lock", "w") as f:
      f.write(f"{'not'+jobtype} {cpuid} {jobid}")
    with open(self.tmpdir/"lock3.lock", "w") as f:
      f.write(f"{jobtype} {cpuid+1} {jobid}")

    with JobLock(self.tmpdir/"lock1.lock") as lock1:
      self.assertFalse(lock1)
    with JobLock(self.tmpdir/"lock2.lock") as lock2:
      self.assertFalse(lock2)
    with JobLock(self.tmpdir/"lock3.lock") as lock3:
      self.assertFalse(lock3)

    with subprocess.Popen(["cat"], stdin=subprocess.PIPE, stdout=subprocess.PIPE) as popen:
      pid = popen.pid
      with open(self.tmpdir/"lock4.lock", "w") as f:
        f.write(f"{jobtype} {cpuid} {pid}")
      with JobLock(self.tmpdir/"lock4.lock") as lock4:
        self.assertFalse(lock4)

    with JobLock(self.tmpdir/"lock4.lock") as lock4:
      self.assertTrue(lock4)

  def testsqueue(self):
    dummysqueue = """
      #!/bin/bash
      echo '
           1234567   RUNNING
           1234568   PENDING
      '
    """.lstrip()
    with open(self.tmpdir/"squeue", "w") as f:
      f.write(dummysqueue)
    (self.tmpdir/"squeue").chmod(0o0777)
    os.environ["PATH"] = f"{self.tmpdir}:"+os.environ["PATH"]

    with open(self.tmpdir/"lock1.lock", "w") as f:
      f.write("SLURM 0 1234567")
    with open(self.tmpdir/"lock2.lock", "w") as f:
      f.write("1234567")
    with open(self.tmpdir/"lock3.lock", "w") as f:
      f.write("SLURM 0 12345678")
    with open(self.tmpdir/"lock4.lock", "w") as f:
      f.write("12345678")
    with open(self.tmpdir/"lock5.lock", "w") as f:
      f.write("SLURM 0 1234568")
    with open(self.tmpdir/"lock6.lock", "w") as f:
      f.write("1234568")

    with JobLock(self.tmpdir/"lock1.lock") as lock1:
      self.assertFalse(lock1)
    with JobLock(self.tmpdir/"lock2.lock") as lock2:
      self.assertFalse(lock2)
    with JobLock(self.tmpdir/"lock3.lock") as lock3:
      self.assertTrue(lock3)
    with JobLock(self.tmpdir/"lock4.lock") as lock4:
      self.assertTrue(lock4)
    with JobLock(self.tmpdir/"lock5.lock") as lock5:
      self.assertTrue(lock5)
    with JobLock(self.tmpdir/"lock6.lock") as lock6:
      self.assertTrue(lock6)

  def testcondor(self):
    dummycondor_q = """
      #!/bin/bash
      echo '
        -- Schedd: my schedd
         ID      OWNER            SUBMITTED     RUN_TIME ST PRI SIZE CMD
         1234567.1
         1234568.1
      '
    """.lstrip()
    with open(self.tmpdir/"condor_q", "w") as f:
      f.write(dummycondor_q)
    (self.tmpdir/"condor_q").chmod(0o0777)
    os.environ["PATH"] = f"{self.tmpdir}:"+os.environ["PATH"]

    with open(self.tmpdir/"lock1.lock", "w") as f:
      f.write("SLURM 1234567 1")
    with open(self.tmpdir/"lock2.lock", "w") as f:
      f.write("CONDOR 1234567 1")
    with open(self.tmpdir/"lock3.lock", "w") as f:
      f.write("CONDOR 12345678 1")
    with open(self.tmpdir/"lock4.lock", "w") as f:
      f.write("CONDOR 1234568 1")
    with open(self.tmpdir/"lock5.lock", "w") as f:
      f.write("CONDOR 1234567 2")

    with JobLock(self.tmpdir/"lock1.lock") as lock1:
      self.assertFalse(lock1)
    with JobLock(self.tmpdir/"lock2.lock") as lock2:
      self.assertFalse(lock2)
    with JobLock(self.tmpdir/"lock3.lock") as lock3:
      self.assertTrue(lock3)
    with JobLock(self.tmpdir/"lock4.lock") as lock4:
      self.assertFalse(lock4)
    with JobLock(self.tmpdir/"lock5.lock") as lock5:
      self.assertTrue(lock5)

  def testCacheSqueue(self):
    with open(self.tmpdir/"lock.lock", "w") as f:
      f.write("SLURM 0 1234567")
    with JobLock(self.tmpdir/"lock.lock") as lock:
      self.assertFalse(lock)

    dummysqueue = """
      #!/bin/bash
      echo '
           1234567   RUNNING
      '
      sed -i s/1234567/1234568/g $0
    """.lstrip()
    with open(self.tmpdir/"squeue", "w") as f:
      f.write(dummysqueue)
    (self.tmpdir/"squeue").chmod(0o0777)
    os.environ["PATH"] = f"{self.tmpdir}:"+os.environ["PATH"]

    with JobLock(self.tmpdir/"lock.lock") as lock:
      self.assertFalse(lock)
    with JobLock(self.tmpdir/"lock.lock") as lock:
      self.assertFalse(lock)
    with JobLock(self.tmpdir/"lock.lock", cachesqueue=False) as lock:
      self.assertTrue(lock)

  def testJobLockAndWait(self):
    with JobLockAndWait(self.tmpdir/"lock1.lock", 0.001, silent=True) as lock1:
      self.assertEqual(lock1.niterations, 1)

    with open(self.tmpdir/"lock2.lock", "w") as f:
      f.write("SLURM 0 1234567")
    with self.assertRaises(RuntimeError):
      with JobLockAndWait(self.tmpdir/"lock2.lock", 0.001, maxiterations=10, silent=True) as lock2:
        pass

    dummysqueue = """
      #!/bin/bash
      echo '
           1234567   RUNNING
      '
      sed -i s/1234567/1234568/g $0
    """.lstrip()
    with open(self.tmpdir/"squeue", "w") as f:
      f.write(dummysqueue)
    (self.tmpdir/"squeue").chmod(0o0777)
    os.environ["PATH"] = f"{self.tmpdir}:"+os.environ["PATH"]

    with JobLockAndWait(self.tmpdir/"lock2.lock", 0.001, maxiterations=10, silent=True, cachesqueue=False) as lock2:
      self.assertEqual(lock2.niterations, 2)

    inputfile = self.tmpdir/"input.txt"
    outputfile = self.tmpdir/"output.txt"

    with JobLockAndWait(self.tmpdir/"lock3.lock", 0.001, maxiterations=10, silent=True, outputfiles=[outputfile]) as lock3:
      self.assertTrue(lock3)
      self.assertEqual(lock3.niterations, 1)

    outputfile.touch()

    with JobLockAndWait(self.tmpdir/"lock3.lock", 0.001, maxiterations=10, silent=True, outputfiles=[outputfile]) as lock3:
      self.assertFalse(lock3)

    with JobLockAndWait(self.tmpdir/"lock3.lock", 0.001, maxiterations=10, silent=True, outputfiles=[outputfile], inputfiles=[inputfile]) as lock3:
      self.assertFalse(lock3)

    outputfile.unlink()

    with self.assertRaises(FileNotFoundError):
      with JobLockAndWait(self.tmpdir/"lock3.lock", 0.001, maxiterations=10, silent=True, outputfiles=[outputfile], inputfiles=[inputfile]) as lock3:
        pass

    def touchlater(filename, delay):
      def inner():
        time.sleep(delay)
        filename.touch()
      p = multiprocessing.Process(target=inner)
      p.start()

    iterationtime = 0.01
    touchlater(inputfile, iterationtime * 1.5)
    with JobLockAndWait(self.tmpdir/"lock3.lock", iterationtime, maxiterations=10, silent=True, inputfiles=[inputfile], waitforinputs=True) as lock3:
      self.assertTrue(lock3)
      self.assertGreaterEqual(lock3.niterations, 3)
      self.assertLessEqual(lock3.niterations, 4)

  def testCorruptFileTimeout(self):
    with open(self.tmpdir/"lock1.lock_2", "w"): pass
    with open(self.tmpdir/"lock1.lock_5", "w"): pass
    with open(self.tmpdir/"lock1.lock_30", "w"): pass
    time.sleep(1)
    with open(self.tmpdir/"lock1.lock_10", "w"): pass
    with open(self.tmpdir/"lock1.lock", "w"): pass
    with JobLock(self.tmpdir/"lock1.lock", corruptfiletimeout=datetime.timedelta(seconds=1)) as lock:
      self.assertFalse(lock)
      self.assertIsInstance(lock.debuginfo["oldjobinfo"], ValueError)
    self.assertFalse((self.tmpdir/"lock1.lock_2").exists())
    self.assertTrue((self.tmpdir/"lock1.lock_5").exists())
    self.assertTrue((self.tmpdir/"lock1.lock_10").exists())
    self.assertTrue((self.tmpdir/"lock1.lock_30").exists())
    time.sleep(1)
    with JobLock(self.tmpdir/"lock1.lock") as lock:
      self.assertFalse(lock)
    with JobLock(self.tmpdir/"lock1.lock", corruptfiletimeout=datetime.timedelta(seconds=10)) as lock:
      self.assertFalse(lock)
    with JobLock(self.tmpdir/"lock1.lock", corruptfiletimeout=datetime.timedelta(seconds=1)) as lock:
      self.assertTrue(lock)
    self.assertFalse((self.tmpdir/"lock1.lock_5").exists())
    self.assertFalse((self.tmpdir/"lock1.lock_10").exists())
    self.assertFalse((self.tmpdir/"lock1.lock_30").exists())

  def testCleanUp(self):
    with open(self.tmpdir/"lock1.lock_2", "w"): pass
    with open(self.tmpdir/"lock1.lock_5", "w"): pass
    with open(self.tmpdir/"lock1.lock_30", "w"): pass
    time.sleep(1)
    with open(self.tmpdir/"lock1.lock_10", "w"): pass
    clean_up_old_job_locks(self.tmpdir, howold=datetime.timedelta(seconds=1), dryrun=True, silent=True)
    self.assertTrue((self.tmpdir/"lock1.lock_2").exists())
    self.assertTrue((self.tmpdir/"lock1.lock_5").exists())
    self.assertTrue((self.tmpdir/"lock1.lock_10").exists())
    self.assertTrue((self.tmpdir/"lock1.lock_30").exists())
    time.sleep(1)
    clean_up_old_job_locks(self.tmpdir, howold=datetime.timedelta(seconds=1), dryrun=True, silent=True)
    subprocess.run(["clean_up_old_job_locks", self.tmpdir, "--hours-old", str(1/3600), "--silent", "--dry-run"], check=True)
    self.assertTrue((self.tmpdir/"lock1.lock_2").exists())
    self.assertTrue((self.tmpdir/"lock1.lock_5").exists())
    self.assertTrue((self.tmpdir/"lock1.lock_10").exists())
    self.assertTrue((self.tmpdir/"lock1.lock_30").exists())
    subprocess.run(["clean_up_old_job_locks", self.tmpdir, "--hours-old", str(1/3600), "--silent"], check=True)
    clean_up_old_job_locks(self.tmpdir, howold=datetime.timedelta(seconds=1), silent=True)
    self.assertFalse((self.tmpdir/"lock1.lock_2").exists())
    self.assertFalse((self.tmpdir/"lock1.lock_5").exists())
    self.assertFalse((self.tmpdir/"lock1.lock_10").exists())
    self.assertFalse((self.tmpdir/"lock1.lock_30").exists())

  def testMkdir(self):
    with self.assertRaises(FileNotFoundError):
      with JobLock(self.tmpdir/"nested"/"subfolders"/"lock1.lock") as lock:
        pass
    with JobLock(self.tmpdir/"nested"/"subfolders"/"lock1.lock", mkdir=True) as lock:
      self.assertTrue(lock)
    with JobLock(self.tmpdir/"nested"/"subfolders"/"lock1.lock") as lock:
      self.assertTrue(lock)

  def testSlurmRsyncInput(self):
    inputfile = self.tmpdir/"input.txt"
    with open(inputfile, "w") as f: f.write("hello")

    rsyncedinput = slurm_rsync_input(inputfile, silentrsync=True)
    self.assertEqual(inputfile, rsyncedinput)

    os.environ["SLURM_JOBID"] = "1234567"
    rsyncedinput = slurm_rsync_input(inputfile, silentrsync=True)
    self.assertNotEqual(inputfile, rsyncedinput)
    with open(inputfile) as f1, open(rsyncedinput) as f2:
      self.assertEqual(f1.read(), f2.read())

    inputfile2 = self.tmpdir/"subfolder"/"input.txt"
    inputfile2.parent.mkdir()
    with open(inputfile2, "w") as f: f.write("hello 2")
    rsyncedinput2 = slurm_rsync_input(inputfile2, silentrsync=True)
    with open(rsyncedinput) as f1, open(rsyncedinput2) as f2:
      self.assertEqual(f1.read(), "hello")
      self.assertEqual(f2.read(), "hello 2")

  def testSlurmRsyncOutput(self):
    outputfile = self.tmpdir/"output.txt"
    with slurm_rsync_output(outputfile, silentrsync=True) as outputtorsync:
      self.assertEqual(outputfile, outputtorsync)

    os.environ["SLURM_JOBID"] = "1234567"
    with slurm_rsync_output(outputfile, silentrsync=True) as outputtorsync:
      self.assertNotEqual(outputfile, outputtorsync)
      with open(outputtorsync, "w") as f: f.write("hello")
    with open(outputfile) as f1, open(outputtorsync) as f2:
      self.assertEqual(f1.read(), f2.read())

    outputfile2 = self.tmpdir/"subfolder"/"output.txt"
    outputfile2.parent.mkdir()
    with slurm_rsync_output(outputfile, silentrsync=True) as outputtorsync, slurm_rsync_output(outputfile2, silentrsync=True) as outputtorsync2:
      with open(outputtorsync, "w") as f1, open(outputtorsync2, "w") as f2:
        f1.write("hello")
        f2.write("hello 2")
    with open(outputfile) as f1, open(outputfile2) as f2:
      self.assertEqual(f1.read(), "hello")
      self.assertEqual(f2.read(), "hello 2")

  def testSlurmCleanUpTempDir(self):
    filename = self.slurm_tmpdir/"test.txt"
    filename.touch()
    slurm_clean_up_temp_dir()
    self.assertTrue(filename.exists())

    os.environ["SLURM_JOBID"] = "1234567"
    slurm_clean_up_temp_dir()
    self.assertFalse(filename.exists())

  def testOkIfNotCreated(self):
    outputfile = self.tmpdir/"output.txt"
    os.environ["SLURM_JOBID"] = "1234567"
    with self.assertRaises(FileNotFoundError):
      with slurm_rsync_output(outputfile, silentrsync=True):
        pass

    with slurm_rsync_output(outputfile, silentrsync=True, ok_if_not_created=True):
      pass

