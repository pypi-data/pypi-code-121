import subprocess
import sys
import os
from distutils.spawn import find_executable


def create_folder(output_path):
    """
        create emringer output folder inside va directory

    :return: model related path of strudel folder
    """

    fullname = '{}'.format(output_path)

    if not os.path.isdir(fullname):
        os.mkdir(fullname, mode=0o777)
    else:
        print('{} is exist'.format(fullname))


def run_threedfsc(mapodd, mapeven, primarymap, vxsize, output_path, threedfscdir):
    """
        3DFSC calculation

    :return:
    """

    errlist = []
    try:
        assert find_executable('conda') is not None
        conda_path = find_executable('conda')
        if 'condabin' in conda_path:
            conda_root = conda_path.replace('/condabin/conda', '')
        else:
            conda_root = conda_path.replace('/bin/conda', '')
        source_conda = '{}/etc/profile.d/conda.sh'.format(conda_root)
        create_folder(output_path)
        conda_cmd = 'source {}; conda activate 3dfsc; python {} --halfmap1 {} --halfmap2 {} --fullmap {} --apix {}'.\
            format(source_conda, threedfscdir, mapodd, mapeven, primarymap, vxsize)
        try:
            subprocess.check_call(conda_cmd, cwd=output_path, shell=True)
        except subprocess.CalledProcessError as suberr:
            err = '3DFSC calculation error: {}.'.format(suberr)
            errlist.append(err)
            sys.stderr.write(err + '\n')
    except AssertionError:
        sys.stderr.write('conda executable is not there.\n')


    return errlist


