import os
import tempfile
from pathlib import Path

from pyabc.external.base import ExternalHandler as eh

import fitmulticell as fmc


def test_morpheus():
    file = os.path.normpath(os.getcwd() + os.sep)
    # file = os.getcwd()
    file_ = str(file + '/doc/example/models' + '/Demo_CellMotility.xml')
    pars = {'motion_strength': 1.0, 'noise_level': 0.1}
    new_eh = eh('morpheus')
    loc = tempfile.mkdtemp()
    cmd = new_eh.create_executable(loc)
    cmd = cmd + f" -file={file_} -outdir={loc}"
    # call the model
    assert new_eh.run(args=pars, cmd=cmd, loc=loc)


def test_simulation():
    file = os.path.normpath(os.getcwd() + os.sep)
    # file = os.getcwd()
    file_ = str(file + '/doc/example/models' + '/Demo_CellMotility.xml')
    par_map = {
        'motion_strength': './Global/Constant[@symbol="motion_strength"]',
        'noise_level': './Global/Constant[@symbol="noise_level"]',
    }
    assert fmc.model.MorpheusModel(
        file_,
        par_map=par_map,
        executable="morpheus",
        show_stdout=False,
        show_stderr=True,
        raise_on_error=False,
    )


def test_simulation_output():
    file = os.path.normpath(os.getcwd() + os.sep)
    # file = os.getcwd()
    file_ = str(file + '/doc/example/models' + '/Demo_CellMotility.xml')
    tmp_dir = tempfile.TemporaryDirectory()
    par_map = {
        'motion_strength': './Global/Constant[@symbol="motion_strength"]',
        'noise_level': './Global/Constant[@symbol="noise_level"]',
    }
    pars = {'motion_strength': 1.0, 'noise_level': 0.1}
    model = fmc.model.MorpheusModel(
        file_,
        par_map=par_map,
        executable="morpheus",
        show_stdout=False,
        show_stderr=True,
        raise_on_error=False,
        dir=tmp_dir.name,
        clean_simulation=False,
    )
    model.sample(pars)
    os.chdir(tmp_dir.name)
    assert len(list(Path(".").rglob("*.csv"))) != 0
    tmp_dir.cleanup()
