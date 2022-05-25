###############################################################################
# (c) Copyright 2020-2021 CERN for the benefit of the LHCb Collaboration      #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################
import importlib
import io
import json
import os
import shlex
import shutil
import subprocess
import tempfile
import zipfile
from os.path import join

import click
import requests
from LbAPCommon import get_sso_token, parse_yaml, render_yaml, validate_yaml
from LbAPCommon.hacks import project_uses_cmt
from LbAPCommon.options_parsing import validate_options

from .utils import (
    check_production,
    check_status_code,
    create_output_dir,
    pool_xml_catalog,
    recursively_create_input,
    resolve_input_overrides,
)

LBAPI_HOST = os.environ.get("LBAPI_HOST", "https://lbap.app.cern.ch")
LBAPI_CLIENT_ID = os.environ.get("LBAPI_CLIENT_ID", "lhcb-analysis-productions")


def prepare_test(production_name, job_name, dependent_input=None):
    """Run a local test job for a specific production job"""
    token = get_sso_token(LBAPI_HOST, LBAPI_CLIENT_ID)

    # Check if production exists
    check_production(production_name)

    # Check if job actually exists in production
    with open(os.path.join(production_name, "info.yaml"), "rt") as fp:
        raw_yaml = fp.read()
    prod_data, checks_data = parse_yaml(render_yaml(raw_yaml))
    validate_yaml(prod_data, checks_data, ".", production_name)
    try:
        job_data = prod_data[job_name]
    except KeyError:
        raise click.ClickException(
            f"Job {job_name} is not found for production {production_name}!"
        )

    application_name, application_version = job_data["application"].rsplit("/", 1)
    require_cmt = project_uses_cmt(application_name, application_version)

    prodrun_conf = {
        "spec_version": 1,
        "application": {
            "name": application_name,
            "version": application_version,
            "data_pkgs": ["AnalysisProductions v999999999999", "ProdConf"],
        },
        "options": {"format": "WGProd", "files": job_data["options"]},
        "input": {"xml_summary_file": "summaryDaVinci_00012345_00006789_1.xml"},
        "output": {"prefix": "00012345_00006789_1"},
    }

    override_input, output_filetype = resolve_input_overrides(prod_data, job_name)
    if "job_name" in job_data["input"] and dependent_input is None:
        dependent_input = recursively_create_input(
            production_name,
            job_data["input"]["job_name"],
            job_data["input"].get("filetype"),
            prod_data,
        )

    # only create output directories if this is the job that's about to be run
    # i.e. there are no dependent jobs that need to be run first
    dynamic_dir, out_dir = create_output_dir(production_name, require_cmt)

    if job_data["automatically_configure"]:
        params = {}
        if output_filetype:
            params["override-output-filetype"] = output_filetype
        response = requests.post(
            f"{LBAPI_HOST}/pipelines/autoconf-options/",
            headers={"Authorization": f"Bearer {token}"},
            json={**job_data, **({"input": override_input} if override_input else {})},
            params=params,
        )
        check_status_code(response)

        config_path = dynamic_dir / production_name / f"{job_name}_autoconf.py"
        config_path.parent.mkdir(parents=True)
        config_path.write_text(response.text)
        prodrun_conf["options"]["files"].insert(
            0, join("$ANALYSIS_PRODUCTIONS_DYNAMIC", production_name, config_path.name)
        )

    prodrun_config_path = out_dir / "prodConf_DaVinci_00012345_00006789_1.json"

    prodrun_conf["output"]["types"] = job_data["output"]

    # force to use the file chosen by the user
    if "bk_query" in job_data["input"] or "transform_ids" in job_data["input"]:
        if dependent_input is not None:
            prodrun_conf["input"]["files"] = [dependent_input]
            if "LFN:" in dependent_input:
                (out_dir / "pool_xml_catalog.xml").write_text(
                    pool_xml_catalog([dependent_input])
                )
                prodrun_conf["input"]["xml_file_catalog"] = "pool_xml_catalog.xml"
        else:
            response = requests.post(
                f"{LBAPI_HOST}/pipelines/lfns/",
                headers={"Authorization": f"Bearer {token}"},
                json=job_data["input"],
            )
            lfns = check_status_code(response).json()

            prodrun_conf["input"]["files"] = [f"LFN:{lfn}" for lfn in lfns]
            (out_dir / "pool_xml_catalog.xml").write_text(pool_xml_catalog(lfns))
            prodrun_conf["input"]["xml_file_catalog"] = "pool_xml_catalog.xml"

    elif "job_name" in job_data["input"]:
        prodrun_conf["input"]["files"] = [dependent_input]

    prodrun_config_path.write_text(json.dumps(prodrun_conf))
    return out_dir, prodrun_config_path.name


def prepare_reproduce(pipeline_id, production_name, job_name, test_id):
    token = get_sso_token(LBAPI_HOST, LBAPI_CLIENT_ID)

    click.secho(
        f"Reproducing test for test {pipeline_id} {production_name} {job_name}",
        fg="green",
    )

    prod_url = f"{LBAPI_HOST}/pipelines/{pipeline_id}/{production_name}/"
    response = requests.get(prod_url, headers={"Authorization": f"Bearer {token}"})
    prod_info = check_status_code(response).json()

    job_url = f"{prod_url}jobs/{job_name}/"
    if test_id != "latest":
        job_url += f"tests/{test_id}"
    response = requests.get(job_url, headers={"Authorization": f"Bearer {token}"})
    job_info = check_status_code(response).json()
    if test_id == "latest":
        job_url += f"tests/{job_info['test']['attempt']}"

    tmp_dir = tempfile.mkdtemp()

    click.secho(f"Cloning {prod_info['repo_url']}", fg="green")
    subprocess.check_call(["git", "clone", prod_info["repo_url"], tmp_dir])

    click.secho(f"Running test in {tmp_dir}", fg="green")
    os.chdir(tmp_dir)

    click.secho(f"Checking out {prod_info['commit']}", fg="green")
    subprocess.check_call(["git", "checkout", prod_info["commit"]])

    check_production(production_name)

    require_cmt = project_uses_cmt(
        job_info["application_name"], job_info["application_version"]
    )
    dynamic_dir, out_dir = create_output_dir(production_name, require_cmt)

    # Download the jobs output sandbox
    response = requests.get(
        f"{job_url}/zip", headers={"Authorization": f"Bearer {token}"}
    )
    zip_data = io.BytesIO(check_status_code(response).content)
    with zipfile.ZipFile(zip_data) as zf:
        zf.extractall(out_dir)
    prodrun_config_path = max(
        out_dir.glob("prodConf*.json"), key=lambda x: x.name.split("_")[-1]
    )

    # Write automatic configuration if requested
    if job_info["automatically_configure"]:
        filename = dynamic_dir / job_info["dynamic_options_path"]
        # Prevent directory traversal
        if str(filename.relative_to(dynamic_dir)).startswith("."):
            raise NotImplementedError(dynamic_dir, filename)
        filename.parent.mkdir(parents=True)
        filename.write_text(job_info["autoconf_options"])

    # Download the job input
    input_paths = [x["path"] for x in job_info["test"]["input_files"]]
    if not input_paths:
        raise NotImplementedError("Failed to find any input files")
    if all("/" in x for x in input_paths):
        # It's an LFN so write the pool_xml_catalog.xml
        (out_dir / "pool_xml_catalog.xml").write_text(pool_xml_catalog(input_paths))
    elif all("/" not in x for x in input_paths):
        if len(input_paths) != 1:
            raise NotImplementedError(input_paths)
        filename = out_dir / input_paths[0]
        # It's from another job so download from S3
        response = requests.get(
            f"{prod_url}jobs/{job_info['input']['job_name']}/tests/"
            f"{job_info['test']['attempt']}/files/{filename.name}/url",
            headers={"Authorization": f"Bearer {token}"},
        )
        url = check_status_code(response).json()["url"]

        click.secho(f"Downloading {filename.name}", fg="green")
        with requests.get(url, stream=True) as resp:
            check_status_code(resp)
            with filename.open("wb") as fp:
                shutil.copyfileobj(resp.raw, fp)

        prodrun_conf = json.loads(prodrun_config_path.read_text())
        prodrun_conf["input"]["files"] = [filename.name]
        prodrun_config_path.write_text(json.dumps(prodrun_conf))
    else:
        raise NotImplementedError(input_paths)

    return out_dir, prodrun_config_path.name


def enter_debugging(out_dir, prodrun_config_path, dependent_job=None):
    # This means the requested job depends on another job and has not been told
    # the location of that jobs output
    if dependent_job is not None:
        raise NotImplementedError(
            "Automatic input creation for job-dependent jobs is not implemented in debug mode \n"
            f"The requested job depends on {dependent_job['job_name']}, please provide the location "
            f"of the output file of a local test of {dependent_job['job_name']} by appending "
            '" -i <file_location>" to the debug command'
        )
    cmd = ["lb-prod-run", prodrun_config_path, "--interactive"]
    click.secho(f"Running: lb-prod-run {shlex.join(cmd)}")
    os.chdir(out_dir)
    os.execlp(cmd[0], *cmd)


def do_options_parsing(env_cmd, out_dir, pkl_file, root_file, job_name, prod_data):
    json_file = join(out_dir, "output.json")

    with importlib.resources.path(
        "LbAPCommon.options_parsing", "gaudi_pickle_to_json.py"
    ) as script_path:
        subprocess.run(
            env_cmd
            + [
                "python",
                script_path,
                "--pkl",
                pkl_file,
                "--output",
                json_file,
                "--debug",
            ],
            text=True,
        )
    return validate_options(json_file, root_file, job_name, prod_data)
