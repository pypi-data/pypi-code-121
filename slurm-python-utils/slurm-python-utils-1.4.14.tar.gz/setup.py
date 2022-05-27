import pathlib, setuptools

here = pathlib.Path(__file__).parent
with open(here/'README.md', encoding='utf-8') as f:
  long_description = f.read()

setuptools.setup(
  name = "slurm-python-utils",
  packages = setuptools.find_packages(include=["job_lock"]),
  author = "Heshy Roskes",
  author_email = "heshyr@gmail.com",
  url = "https://github.com/hroskes/slurm-python-utils",
  install_requires = [
    "methodtools",
    "psutil;sys_platform!='cygwin'",
  ],
  entry_points = {
    "console_scripts": [
      "clean_up_old_job_locks=job_lock.job_lock:clean_up_old_job_locks_argparse",
    ],
  },
  long_description = long_description,
  long_description_content_type = 'text/markdown',
)
