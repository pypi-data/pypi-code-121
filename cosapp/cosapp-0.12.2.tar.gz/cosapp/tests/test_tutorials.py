import os
import unittest
from shutil import copy2, rmtree
from tempfile import mkdtemp

import pytest

nbconvert = pytest.importorskip("nbconvert")

from nbconvert.preprocessors.execute import executenb
from nbformat import read, current_nbformat

test_folder = os.path.dirname(__file__)
tutorials_folder = os.path.join(test_folder, '../../docs/tutorials')
if not os.path.exists(tutorials_folder):  # For distributed cosapp package
    tutorials_folder = os.path.join(test_folder, '../tutorials')


@pytest.fixture(scope="module")
def copy_tutorials():
    tutorials_tmp = mkdtemp()

    if os.path.exists(tutorials_folder):
        curdir = tutorials_folder
        for f in os.listdir(tutorials_folder):
            curfile = os.path.join(curdir, f)
            if os.path.isfile(curfile) and os.path.splitext(curfile)[1] in (".ipynb", ".py"):
                copy2(curfile, tutorials_tmp)

    yield tutorials_tmp
    
    # teardown
    rmtree(tutorials_tmp)


@pytest.mark.notebook
@pytest.mark.parametrize("filename",
    [file for file in os.listdir(tutorials_folder) if os.path.splitext(file)[1] == '.ipynb'])
def test_all(copy_tutorials, filename):
    fullpath = os.path.join(copy_tutorials, filename)
    assert os.path.exists(fullpath), f"Tutorial {filename} was not copied."

    with open(fullpath) as fnb:
        nb = read(fnb, current_nbformat)

    # The execution of the notebook should not raise
    # nbconvert.preprocessors.execute.CellExecutionError
    executenb(nb, cwd=copy_tutorials, timeout=60)
