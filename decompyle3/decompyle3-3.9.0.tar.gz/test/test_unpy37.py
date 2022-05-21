#!/usr/bin/env python
# emacs-mode: -*-python-*-
"""
test_unpy37.py -- unpy37 Python libraries

Usage-Examples:

  test_unpy37.py --all		# decompile all tests (suite + libs)
  test_unpy37.py --all --verify	# decomyile all tests and verify results
  test_unpy37.py --run		# decompile only the testsuite
  test_unpy37.py --verify	# decompile and verify python lib 3.7

Adding own test-trees:

Step 1) Edit this file and add a new entry to 'test_options', eg.
          test_options['mylib'] = ('/usr/lib/mylib', PYOC, 'mylib')
Step 2: Run the test:
	  test_unpy37.py --mylib	  # decompile 'mylib'
	  test_unpy37.py --mylib --verify # decompile verify 'mylib'
"""

import os, time, shutil, sys
from fnmatch import fnmatch
from unpyc37 import decompile


def help():
    print(__doc__)


# ----- configure this for your needs

TEST_VERSIONS = ("3.7.13",)

target_base = "/tmp/py-dis/"
lib_prefix = os.path.join(os.environ["HOME"], ".pyenv/versions")

PYC = ("*.pyc",)
PYO = ("*.pyo",)
PYOC = ("*.pyc", "*.pyo")

# -----

test_options = {
    # name: (src_basedir, pattern, output_base_suffix)
    # "test": ("./test", PYOC, "test"),
    # "max=": 200,
}

for vers in TEST_VERSIONS:
    short_vers = vers[:3]
    test_options[vers] = (
        os.path.join(lib_prefix, vers, "lib", "python" + short_vers),
        PYC,
        "python-lib" + short_vers,
    )


def do_tests(
    src_dir, patterns, target_dir, start_with=None, do_verify=False, max_files=200
):
    def visitor(files, dirname, names):
        files.extend(
            [
                os.path.normpath(os.path.join(dirname, n))
                for n in names
                for pat in patterns
                if fnmatch(n, pat)
            ]
        )

    files = []
    cwd = os.getcwd()
    os.chdir(src_dir)
    for root, dirname, names in os.walk(os.curdir):
        files.extend(
            [
                os.path.normpath(os.path.join(root, n))
                for n in names
                for pat in patterns
                if fnmatch(n, pat)
            ]
        )
        pass
    os.chdir(cwd)
    files.sort()

    if start_with:
        try:
            start_with = files.index(start_with)
            files = files[start_with:]
            print(">>> starting with file", files[0])
        except ValueError:
            pass

    if len(files) > max_files:
        files = [file for file in files if not "site-packages" in file]
        files = [file for file in files if not "test" in file]
        if len(files) > max_files:
            # print("Number of files %d - truncating to last 200" % len(files))
            print(
                "Number of files %d - truncating to first %s" % (len(files), max_files)
            )
            files = files[:max_files]

    os.chdir(src_dir)
    os.makedirs(target_dir, exist_ok=True)
    failed = 0
    tot_files = 0
    for file in files:
        tot_files += 1
        python_prog_str = None
        try:
            python_prog_str = decompile(file)

        except:
            failed += 1

        sys.stdout.write(f"{file} -- {failed} failed, {tot_files} total\n")
        if python_prog_str:
            outfile = f"{target_dir}/{os.path.basename(file[:-1])}"
            try:
                open(outfile, mode="w", encoding="utf-8").write(str(python_prog_str))
                if do_verify:
                    os.system(f"python -m py_compile {outfile}")
                    pass
            except SyntaxError:
                print("file: %s" % sys.exc_info()[1])
                failed += 1
            except:
                print(sys.exc_info()[1])
                sys.stdout.write("\n")
                failed += 1
                pass

    sys.stdout.write("\n")
    print(time.ctime())
    return failed


if __name__ == "__main__":
    import getopt

    codes = []
    do_coverage = do_verify = False
    test_dirs = []
    start_with = None

    test_options_keys = list(test_options.keys())
    test_options_keys.sort()
    opts, args = getopt.getopt(
        sys.argv[1:],
        "",
        ["start-with=", "verify", "v", "max=", "run", "all", "help", "h"]
        + test_options_keys,
    )
    vers = ""

    for opt, val in opts:
        if opt == "--verify":
            do_verify = "strong"
        elif opt == "--start-with":
            start_with = val
        elif opt[2:] in test_options_keys:
            triple = test_options[opt[2:]]
            vers = triple[-1]
            test_dirs.append(triple)
        elif opt == "--max":
            test_options["max="] = int(val)
        elif opt == "--run":
            test_dirs.append(("bytecode_3.7_run", PYOC, "test",))
        elif opt == "--all":
            vers = "all"
            for val in test_options_keys:
                test_dirs.append(test_options[val])

    failed = 0
    for src_dir, pattern, target_dir in test_dirs:
        if os.path.exists(src_dir):
            target_dir = os.path.join(target_base, target_dir)
            if os.path.exists(target_dir):
                shutil.rmtree(target_dir, ignore_errors=1)
            failed = do_tests(
                src_dir,
                pattern,
                target_dir,
                start_with,
                do_verify,
                # test_options["max="],
            )
            print(f"### {failed} tests failed")
        else:
            print("### Path %s doesn't exist; skipping" % src_dir)
            pass
        pass
    sys.exit(failed)
