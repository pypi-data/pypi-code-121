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


def run_emringer(full_modelpath, full_mappath, output_path):
    """

        Emringer score

    :return:
    """

    errlist = []
    try:
        assert find_executable('phenix.emringer') is not None
        emringerpath = find_executable('phenix.emringer')
        create_folder(output_path)
        try:
            subprocess.check_call(emringerpath + ' ' + full_modelpath + ' ' + full_mappath, cwd=output_path, shell=True)
        except subprocess.CalledProcessError as suberr:
            err = 'EMRinger calculation error: {}.'.format(suberr)
            errlist.append(err)
            sys.stderr.write(err + '\n')
    except AssertionError:
        sys.stderr.write('emringer executable is not there.\n')

    return errlist


def emringerpkl_json(self):
    """

        Load EMRiinger output pickle file and write out to a JSON file

    :return:
    """

    pass
