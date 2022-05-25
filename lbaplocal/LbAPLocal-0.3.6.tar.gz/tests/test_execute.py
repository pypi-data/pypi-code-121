###############################################################################
# (c) Copyright 2020 CERN for the benefit of the LHCb Collaboration           #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################
import os
from os.path import isfile, join

import pytest
from click.testing import CliRunner

import LbAPLocal.testing
from LbAPLocal.cli import main


@pytest.mark.slow
@pytest.mark.vcr
@pytest.mark.parametrize(
    "name,n_events",
    [
        ("2016_MagDown_PromptMC_D02KK", 2444),
        ("2016_MagUp_PromptMC_D02KK", 2393),
        ("2016_MagDown_PromptMC_D02KK_noautoconf", 2444),
        ("2016_MagUp_PromptMC_D02KK_noautoconf", 2393),
    ],
)
def test_run_test(
    with_proxy, data_pkg_repo, with_data, name, n_events, monkeypatch, record_mode
):
    if record_mode == "none":
        monkeypatch.setattr(LbAPLocal.testing, "get_sso_token", lambda x, y: "")

    runner = CliRunner()
    result = runner.invoke(main, ["test", "executabletests", name, "--no-validate"])
    assert result.exit_code == 0, result.stdout

    assert "Application Manager Finalized successfully" in result.stdout
    assert "Application Manager Terminated successfully" in result.stdout
    assert f"{n_events} events processed" in result.stdout
    assert "Summary of log messages" in result.stdout
    assert "General explanations" in result.stdout
    assert "Histograms are not being saved" in result.stdout

    assert "Output can be found in" in result.stdout
    output_dir = result.stdout.split("Output can be found in")[-1].strip()

    output_fn = join(output_dir, "00012345_00006789_1.D02KK.ROOT")
    assert isfile(output_fn)
    assert 100 * 1024 <= os.stat(output_fn).st_size <= 1024**2

    stdout_fn = join(output_dir, "stdout.log")
    assert isfile(stdout_fn)
    with open(stdout_fn, "rt") as fp:
        stdout = fp.read()
    assert "Application Manager Finalized successfully" in stdout
    assert "Application Manager Terminated successfully" in stdout
    assert f"{n_events} events processed" in stdout

    stderr_fn = join(output_dir, "stderr.log")
    assert isfile(stderr_fn)


# TODO: Re-add this
# @pytest.mark.slow
# @pytest.mark.vcr
# def test_reproduce(with_proxy, with_data, mocker):
#     from LbAPLocal.testing import prepare_reproduce

#     prepare_reproduce("3558905", "cbtesting", "2016_MagUp_PromptMC_D02KK", "0")

#     execlp_mock = mocker.patch("os.execlp", side_effect=None)

#     runner = CliRunner()
#     result = runner.invoke(
#         main, ["reproduce", "3558905", "cbtesting", "2016_MagUp_PromptMC_D02KK", "0"]
#     )
#     assert result.exit_code == 0, result.stdout
#     assert "Cloning " in result.stdout
#     assert "Downloading pool_xml_catalog.xml" in result.stdout
#     assert "Downloading prodConf_DaVinci_00012345_00006789_1.py" in result.stdout
#     assert "Starting lb-run with: lb-run" in result.stdout

#     assert execlp_mock.call_count == 1
#     cmd, *execlp_args = execlp_mock.call_args[0]
#     assert cmd == execlp_args[0]
#     assert "--use=ProdConf" in execlp_args
#     assert "DaVinci/v39r1p6" in execlp_args

#     assert isfile(execlp_args[execlp_args.index("--rcfile") + 1])
#     with subprocess.Popen(
#         execlp_args + ["-i"],
#         stdout=subprocess.PIPE,
#         stdin=subprocess.PIPE,
#         stderr=subprocess.PIPE,
#     ) as p:
#         stdout_data, stderr_data = p.communicate(input=b"which gaudirun.py")
#     stdout_data = list(filter(None, stdout_data.decode().strip().split("\n")))
#     assert "Welcome to analysis productions debug mode:" in stdout_data
#     assert (
#         stdout_data[-1]
#         == "/cvmfs/lhcb.cern.ch/lib/lhcb/GAUDI/GAUDI_v27r0/InstallArea/x86_64-slc6-gcc49-opt/scripts/gaudirun.py"
#     )
#     assert not isfile(execlp_args[execlp_args.index("--rcfile") + 1])

#     gaudirun_cmd = stdout_data[-2]
#     assert gaudirun_cmd.startswith("gaudirun.py ")
