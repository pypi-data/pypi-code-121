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
import glob
import os
import pathlib
import re
import subprocess
import tempfile
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from os.path import dirname, join

import click
from LbAPCommon import write_jsroot_compression_options
from LbAPCommon.hacks import setup_lbrun_environment


def validate_environment():
    click.secho("Validating environment", fg="green")
    check_proxy()
    check_cvmfs()


def inside_ap_datapkg():
    """Check if script is run from main directory"""
    if not os.path.exists("./AnalysisProductions.xenv"):
        raise click.ClickException(
            "Running command in wrong directory! Please run from the AnalysisProductions base folder."
        )


def check_proxy():
    try:
        subprocess.check_call(
            ["lb-dirac", "dirac-proxy-info", "--checkvalid"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except subprocess.CalledProcessError:
        raise click.ClickException(
            "No grid proxy found, please get one with lhcb-proxy-init"
        )


def check_cvmfs():
    for path in ["/cvmfs/lhcb.cern.ch", "/cvmfs/lhcb-condb.cern.ch"]:
        if not os.listdir(path):
            raise click.ClickException(f"Missing CVMFS repository: {path}")


def pool_xml_catalog(lfns):
    click.secho("Generating pool XML catalog", fg="green")

    # First check if we already have access
    with tempfile.TemporaryDirectory() as tmp_dir:
        proc = subprocess.run(
            ["lb-dirac", "dirac-bookkeeping-genXMLCatalog", "--LFNs", ",".join(lfns)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=tmp_dir,
        )
        if proc.returncode != 0:
            click.secho("********** stdout was:", fg="red")
            click.echo(proc.stdout)
            click.secho("********** stderr was:", fg="red")
            click.echo(proc.stderr)
            raise click.ClickException(
                f"Failed to generate pool XML catalog with: {proc.args}"
            )
        with open(join(tmp_dir, "pool_xml_catalog.xml"), "rt") as fp:
            return fp.read()


def available_productions():
    """Function that finds all production folders with an info.yaml"""

    # Glob all the info.yaml and extract production name
    folders_with_info = glob.glob("*/info.yaml", recursive=True)
    production_names = []
    for folder in folders_with_info:
        folder_name = dirname(folder)
        production_names.append(folder_name)

    return production_names


def check_production(production_name):
    if production_name not in available_productions():
        raise click.ClickException(
            f"Can't find production {production_name}. Does it have an info.yaml?"
        )


def create_output_dir(production_name, require_cmt):
    """Create the directory structure for testing locally"""
    date_string = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    testing_dir = (
        pathlib.Path.cwd() / "local-tests" / f"{production_name}-{date_string}"
    )
    click.secho(f"Running tests in {testing_dir}", fg="green")
    testing_dir.mkdir(parents=True)

    dynamic_dir = testing_dir / "dynamic"
    dynamic_dir.mkdir(parents=True)
    out_dir = testing_dir / "output"
    out_dir.mkdir(parents=True)

    main_dynamic_dir = pathlib.Path.cwd() / "dynamic"
    if main_dynamic_dir.exists():
        click.secho(
            f"Found existing dynamic dir pointing to "
            f"{main_dynamic_dir.resolve()}, unlinking",
            fg="green",
        )
        main_dynamic_dir.unlink()
    main_dynamic_dir.symlink_to(dynamic_dir)
    write_jsroot_compression_options(dynamic_dir)

    # Create the fake install directory for lb-run
    click.secho(f"Setting CMAKE_PREFIX_PATH to {testing_dir}", fg="green")
    setup_lbrun_environment(testing_dir, os.getcwd(), require_cmt)

    return dynamic_dir, out_dir


def log_popen_pipe(p, pipe_name):
    result = b""
    while p.poll() is None:
        line = getattr(p, pipe_name).readline()
        result += line
        click.echo(line.decode(errors="backslashreplace").rstrip("\n"))
    return result


def logging_subprocess_run(args, *, shell=False, cwd=None):
    with subprocess.Popen(
        args, shell=shell, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=cwd
    ) as p:
        with ThreadPoolExecutor(2) as pool:
            stdout = pool.submit(log_popen_pipe, p, "stdout")
            stderr = pool.submit(log_popen_pipe, p, "stderr")
            stdout = stdout.result()
            stderr = stderr.result()
    return subprocess.CompletedProcess(args, p.returncode, stdout, stderr)


def production_name_type(production_name):
    return production_name.strip("/")


def recursively_create_input(production_name, job_name, filetype, prod_data):
    click.secho(
        f"Running {job_name} to provide the necessary input",
        fg="green",
    )

    output_filetypes = [x.lower() for x in prod_data[job_name]["output"]]
    if filetype:
        if filetype.lower() not in output_filetypes:
            raise NotImplementedError(
                f"Looking for {filetype} but {job_name} only produces {output_filetypes}"
            )
    else:
        if len(output_filetypes) > 1:
            raise ValueError(
                "An input filetype must be specified when taking input from a multi-output job!"
            )
        else:
            filetype = output_filetypes[0]

    # Run the job the desired job depends on
    result = logging_subprocess_run(
        f"lb-ap test {production_name} {job_name}", shell=True
    ).stdout.decode()
    # Get the output directory
    output_dir = result.split("\n")[-2].split(" ")[-1]
    # if this is False clearly some other error has occurred so don't bother continuing
    if os.path.exists(output_dir):
        dependent_input = output_dir + f"/00012345_00006789_1.{filetype}"
        for file_path in glob.glob(f"{output_dir}/*"):
            if re.match(
                dependent_input,
                file_path,
                re.IGNORECASE,
            ):
                dependent_input = file_path
                break
        else:
            raise OSError(
                f"{job_name} did not produce the desired output {dependent_input}"
            )

        return dependent_input
    else:
        raise OSError(
            f"The expected output directory {output_dir} does not exist! "
            "It is likely that the test failed in some way so the line in "
            "stdout upon test success that should provide the output location "
            "was not printed."
        )


def resolve_input_overrides(prod_data, job_name):
    override_input = None
    output_filetype = None
    if dependent_job := prod_data[job_name]["input"].get("job_name"):
        job_data = prod_data[dependent_job]

        if "bk_query" in job_data["input"]:
            override_input = job_data["input"]
            output_filetype = job_data["output"][0]
        elif "transform_ids" in job_data["input"]:
            override_input = job_data["input"]
            output_filetype = job_data["output"][0]
        elif "job_name" in job_data["input"]:
            override_input, output_filetype = resolve_input_overrides(
                prod_data, job_data["input"]["job_name"]
            )
        else:
            raise NotImplementedError(
                "Input requires either a bookkeeping location, transform ids or a previous job name"
            )
    return override_input, output_filetype


def check_status_code(response):
    if not response.ok:
        click.secho(response.url)
        click.secho(response.text, fg="red")
        raise click.ClickException("Network request failed")
    return response
