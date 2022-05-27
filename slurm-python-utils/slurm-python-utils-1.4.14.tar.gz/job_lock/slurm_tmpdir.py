from .job_lock import JobLockAndWait, SLURM_JOBID
import contextlib, os, pathlib, shutil, subprocess

def _rsync(source, dest, *, silent, copylinks):
  args = ["-az", "--partial"]
  if copylinks: args.append("-L")
  if not silent: args += ["-v", "--progress"]
  subprocess.check_call(["rsync", *args, os.fspath(source), os.fspath(dest)])

def slurm_rsync_input(filename, *, tempfilename=None, copylinks=True, silentjoblock=None, silentrsync=None):
  filename = pathlib.Path(filename)
  if not filename.is_absolute(): raise ValueError(f"filename {filename} has to be an absolute path")

  if tempfilename is None: tempfilename = filename.relative_to("/")
  tempfilename = pathlib.Path(tempfilename)
  if tempfilename.is_absolute(): raise ValueError(f"tempfilename {tempfilename} has to be a relative path")

  if SLURM_JOBID() is not None:
    tmpdir = pathlib.Path(os.environ["TMPDIR"])
    tempfilename = tmpdir/tempfilename
    if silentrsync is None:
      silentrsync = tempfilename.exists()
    tempfilename.parent.mkdir(exist_ok=True, parents=True)
    lockfilename = tempfilename.with_suffix(".lock")
    if lockfilename == tempfilename:
      lockfilename = tempfilename.with_suffix(".lock_2")
    assert lockfilename != tempfilename
    try:
      with JobLockAndWait(lockfilename, 10, task=f"rsyncing {filename}", silent=silentjoblock):
        _rsync(filename, tempfilename, silent=silentrsync, copylinks=copylinks)
    except subprocess.CalledProcessError:
      return filename
    return tempfilename
  else:
    return filename

@contextlib.contextmanager
def slurm_rsync_output(filename, *, tempfilename=None, copylinks=True, silentrsync=None, ok_if_not_created=False):
  filename = pathlib.Path(filename)
  if not filename.is_absolute(): raise ValueError(f"filename {filename} has to be an absolute path")

  if tempfilename is None: tempfilename = filename.relative_to("/")
  tempfilename = pathlib.Path(tempfilename)
  if tempfilename.is_absolute(): raise ValueError(f"tempfilename {tempfilename} has to be a relative path")

  if SLURM_JOBID() is not None:
    tmpdir = pathlib.Path(os.environ["TMPDIR"])
    tmpoutput = tmpdir/tempfilename
    if silentrsync is None:
      silentrsync = False
    tmpoutput.parent.mkdir(exist_ok=True, parents=True)
    yield tmpoutput
    if not tmpoutput.exists():
      if ok_if_not_created:
        return
      else:
        raise FileNotFoundError(f"{tmpoutput} was not created in the with block")
    _rsync(tmpoutput, filename, silent=silentrsync, copylinks=copylinks)
  else:
    yield filename

def slurm_clean_up_temp_dir():
  if SLURM_JOBID() is None: return
  tmpdir = pathlib.Path(os.environ["TMPDIR"])
  for filename in tmpdir.iterdir():
    if filename.is_dir() and not filename.is_symlink():
      shutil.rmtree(filename)
    else:
      filename.unlink()
