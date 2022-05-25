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
import json
import os
import re
import shlex
from glob import glob
from os.path import join

import click
from LbAPCommon import parse_yaml, render_yaml, validate_yaml
from LbAPCommon.checks import run_job_checks
from LbAPCommon.checks_utils import checks_to_JSON, hist_to_root
from pkg_resources import DistributionNotFound, get_distribution

from .checks import checks_exist, perform_checks
from .log_parsing import show_log_advice
from .testing import enter_debugging, prepare_reproduce, prepare_test
from .utils import (
    available_productions,
    check_production,
    inside_ap_datapkg,
    logging_subprocess_run,
    production_name_type,
    validate_environment,
)


class NaturalOrderGroup(click.Group):
    """Group for showing subcommands in the correct order"""

    def list_commands(self, ctx):
        return self.commands.keys()


def print_version(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    for package in ["LbAPLocal", "LbAPCommon", "LbEnv", "LbDiracWrappers"]:
        try:
            version = get_distribution(package).version
        except DistributionNotFound:
            click.secho(f"{package} is not installed", fg="red")
        else:
            click.echo(f"{package} version: {version}")
    ctx.exit()


@click.group(cls=NaturalOrderGroup)
@click.option(
    "--version", is_flag=True, callback=print_version, expose_value=False, is_eager=True
)
def main():
    """Command line tool for the LHCb AnalysisProductions"""
    pass


@main.command()
@click.argument("production_name", type=production_name_type, default="", nargs=1)
def list(production_name):
    """List the available production folders by running lb-ap list \n
    List the available productions for a specific production by running lb-ap list <YOUR_PRODUCTION>"""
    inside_ap_datapkg()

    if production_name:
        # Check if production exists
        check_production(production_name)
        click.echo(f"The available jobs for {production_name} are: ")

        # Get rendered yaml and find all the production names
        with open(os.path.join(production_name, "info.yaml"), "rt") as fp:
            raw_yaml = fp.read()
        job_data, check_data = parse_yaml(render_yaml(raw_yaml))
        for job_name in job_data:
            click.echo(f"* {job_name}")
    else:
        click.echo("The available productions are: ")
        for folder in available_productions():
            click.echo(f"* {folder}")


@main.command()
@click.argument("production_name", type=production_name_type, nargs=1)
@click.argument("job_name", type=str, default="", nargs=1)
def list_checks(production_name, job_name):
    """List the checks for a specific production by running lb-ap list-checks <YOUR_PRODUCTION> \n
    List only the checks required by a specific job by running lb-ap list-checks <YOUR_PRODUCTION> <YOUR_JOB>"""
    inside_ap_datapkg()

    # Check if production exists
    check_production(production_name)

    # Get rendered yaml and find all the production names
    with open(os.path.join(production_name, "info.yaml"), "rt") as fp:
        raw_yaml = fp.read()
    try:
        jobs_data, checks_data = parse_yaml(render_yaml(raw_yaml))
    except Exception:
        click.secho("Parsed YAML has errors!", fg="red")
        click.secho(f'See "lb-ap validate {production_name}" for details', fg="red")
        raise click.ClickException("Failed to parse YAML")

    if len(checks_data) == 0:
        click.echo(f"No checks are defined for {production_name}")
        return

    if job_name:
        try:
            job_data = jobs_data[job_name]
        except KeyError:
            raise click.ClickException(
                f"Job {job_name} is not found for production {production_name}!"
            )

        job_checks = job_data.get("checks")
        if len(job_checks) == 0 or job_checks is None:
            click.echo(
                f"None of the checks defined for {production_name} are required by {job_name}"
            )
        else:
            click.echo(
                f"The checks defined for {production_name} that are required by {job_name} are: "
            )
            for cname in job_checks:
                ctype = checks_data.get(cname).get("type")
                click.echo(f"* {cname} (type: {ctype})")
    else:
        click.echo(f"The checks defined for {production_name} are: ")
        for cname, cvalue in checks_data.items():
            ctype = cvalue.get("type")
            click.echo(f"* {cname} (type: {ctype})")


@main.command()
@click.argument("production_name", type=production_name_type, nargs=1)
def render(production_name):
    """Render the info.yaml for a given production"""
    inside_ap_datapkg()

    # Check if production exists
    check_production(production_name)

    # Get rendered yaml and print
    click.secho(f"Rendering info.yaml for {production_name}", fg="green")
    with open(os.path.join(production_name, "info.yaml"), "rt") as fp:
        raw_yaml = fp.read()
    render = render_yaml(raw_yaml)
    click.echo(render)
    try:
        job_data, check_data = parse_yaml(render)
        warnings = validate_yaml(job_data, check_data, ".", production_name)
    except Exception:
        click.secho("Rendered YAML has errors!", fg="red")
        click.secho(f'See "lb-ap validate {production_name}" for details', fg="red")
        raise click.ClickException("Failed to parse and validate YAML")
    else:
        for warning in warnings:
            click.secho(f"WARNING: {warning}", fg="yellow")
        click.secho("YAML parsed and validated successfully", fg="green")


@main.command()
@click.argument("production_name", type=production_name_type, nargs=1)
def validate(production_name):
    """Validate the configuration for a given production"""
    inside_ap_datapkg()

    # Check if production exists
    check_production(production_name)

    # Get rendered yaml and print
    click.secho(f"Rendering info.yaml for {production_name}", fg="green")
    with open(os.path.join(production_name, "info.yaml"), "rt") as fp:
        raw_yaml = fp.read()
    render = render_yaml(raw_yaml)

    try:
        job_data, check_data = parse_yaml(render)
    except Exception as e:
        click.secho("Error parsing YAML!", fg="red")
        raise click.ClickException(str(e))
    else:
        click.secho("YAML parsed successfully", fg="green")

    try:
        warnings = validate_yaml(job_data, check_data, ".", production_name)
    except Exception as e:
        click.secho("Error validating YAML!", fg="red")
        raise click.ClickException(str(e))
    else:
        for warning in warnings:
            click.secho(f"WARNING: {warning}", fg="yellow")
        click.secho("YAML validated successfully", fg="green")


@main.command()
@click.argument("production_name", type=production_name_type, nargs=1)
@click.argument("job_name", type=str, nargs=1)
@click.option("--validate/--no-validate", default=True)
@click.option(
    "-i",
    "--dependent-input",
    default=None,
    nargs=1,
    help="Run the test on a specific input file by passing either an LFN or a path to a local file",
)
def test(production_name, job_name, dependent_input, validate):
    """Execute a job locally"""
    if validate:
        validate_environment()
    inside_ap_datapkg()

    out_dir, prodrun_config_path = prepare_test(
        production_name, job_name, dependent_input
    )

    cmd = ["lb-prod-run", prodrun_config_path, "--verbose"]
    click.secho(f"Starting application with: {shlex.join(cmd)}", fg="green")
    result = logging_subprocess_run(cmd, cwd=out_dir)

    (out_dir / "stdout.log").write_bytes(result.stdout)
    (out_dir / "stderr.log").write_bytes(result.stderr)

    click.secho("Summary of log messages:", fg="green")
    show_log_advice(
        b"\n".join([result.stdout, result.stderr]).decode(errors="backslashreplace")
    )

    if result.returncode != 0:
        raise click.ClickException("Execution failed, see above for details")

    # Obtain the right output file name
    with open(os.path.join(production_name, "info.yaml"), "rt") as fp:
        raw_yaml = fp.read()
    prod_data, checks_data = parse_yaml(render_yaml(raw_yaml))
    yaml_warnings = validate_yaml(prod_data, checks_data, ".", production_name)
    try:
        job_data = prod_data[job_name]
    except KeyError:
        raise click.ClickException(
            f"Job {job_name} is not found for production {production_name}!"
        )
    output_file = job_data["output"][0]

    # Validating Gaudi options
    test_ntuple_path = out_dir / f"00012345_00006789_1.{output_file}"
    for file_path in glob(str(out_dir / "*")):
        if re.match(
            str(test_ntuple_path),
            file_path,
            re.IGNORECASE,
        ):
            test_ntuple_path = file_path
            break
    else:
        raise click.ClickException(
            "ERROR: The expected output file does not exist!\n"
            f"Expected: {test_ntuple_path}"
        )

    errors, warnings = [], []
    # TODO: This hasn't been updated to work with lb-prod-run
    click.secho("Options parsing is currently unavailable", fg="yellow")
    # if ".root" in test_ntuple_path.lower():
    #     errors, warnings = do_options_parsing(
    #         # TODO
    #         env_cmd,
    #         out_dir,
    #         join(out_dir, "output.pkl"),
    #         test_ntuple_path,
    #         job_name,
    #         prod_data,
    #     )
    warnings.extend(yaml_warnings)
    for warning in warnings:
        click.secho(f"WARNING: {warning}", fg="yellow")

    if errors:
        raise click.ClickException(
            "Found the following errors when parsing the options:"
            + "\n  * "
            + "\n  * ".join(errors)
        )
    if not any([warnings, errors]):
        click.secho(
            "No problems found while validating the options and output file!",
            fg="green",
        )

    # Run checks
    if checks_exist(checks_data):
        checks_output_dir = join(out_dir, "checks")
        perform_checks(production_name, job_name, [test_ntuple_path], checks_output_dir)

    # The functionality of job-dependent job testing relies on out_dir being written
    # in the line below as the final word so please be careful if changing the below line
    click.secho(f"Success! Output can be found in {out_dir}", fg="green")


@main.command()
@click.argument("production_name", type=production_name_type, nargs=1)
@click.argument("job_name", type=str, nargs=1)
@click.argument("test_ntuple_path", type=click.Path(exists=True), nargs=1)
@click.argument("checks_output_dir", type=click.Path(), default="", nargs=1)
@click.option("--validate/--no-validate", default=True)
def check(production_name, job_name, test_ntuple_path, checks_output_dir, validate):
    """Run checks for a production"""
    if validate:
        validate_environment()
    inside_ap_datapkg()

    # Obtain the right output file name
    with open(os.path.join(production_name, "info.yaml"), "rt") as fp:
        raw_yaml = fp.read()
    try:
        prod_data, checks_data = parse_yaml(render_yaml(raw_yaml))
        warnings = validate_yaml(prod_data, checks_data, ".", production_name)
    except Exception:
        click.secho("Rendered YAML has errors!", fg="red")
        click.secho(f'See "lb-ap validate {production_name}" for details', fg="red")
        raise click.ClickException("Failed to parse and validate YAML")
    else:
        for warning in warnings:
            click.secho(f"WARNING: {warning}", fg="yellow")
        click.secho("YAML parsed and validated successfully", fg="green")

    # If checks_output_dir not specified, set it to a "checks" dir in the same directory as the input file
    if not checks_output_dir:
        checks_output_dir = join(os.path.dirname(test_ntuple_path), "checks")

    # Run checks
    if checks_exist(checks_data):
        perform_checks(production_name, job_name, [test_ntuple_path], checks_output_dir)


@main.command()
@click.argument("checks_data_file", type=str, nargs=1)
@click.argument("input_ntuple", type=str, nargs=1)
@click.argument("output_dir", type=str, nargs=1)
@click.argument("job_index", type=int, nargs=1)
def ci_checks(
    checks_data_file: str, input_ntuple: str, output_dir: str, job_index: int
):
    """Helper function for running checks in the CI. This is not recommended for users."""
    click.secho("Starting checks!", fg="green")
    with open(checks_data_file, "r") as inf:
        test_info = json.load(inf)
    check_results = run_job_checks(
        test_info["jobs"][job_index]["checks"],
        test_info["jobs"][job_index]["checks_data"],
        [input_ntuple],
    )
    hist_to_root(
        test_info["jobs"][job_index]["name"], check_results, f"{output_dir}/checks.root"
    )

    check_results = {test_info["jobs"][job_index]["name"]: check_results}
    checks_to_JSON(
        test_info["jobs"][job_index]["checks_data"],
        check_results,
        json_output_path=f"{output_dir}/checks.json",
    )


@main.command()
@click.argument("production_name", type=production_name_type, nargs=1)
@click.argument("job_name", type=str, nargs=1)
@click.option("--validate/--no-validate", default=True)
@click.option(
    "-i",
    "--dependent-input",
    default=None,
    nargs=1,
    help="Run the test on a specific input file by passing either an LFN or a path to a local file",
)
def debug(production_name, job_name, dependent_input, validate):
    """Start an interactive session inside the job's environment"""
    if validate:
        validate_environment()
    inside_ap_datapkg()

    enter_debugging(*prepare_test(production_name, job_name, dependent_input))


@main.command()
@click.argument("pipeline_id", type=int, nargs=1)
@click.argument("production_name", type=production_name_type, nargs=1)
@click.argument("job_name", type=str, nargs=1)
@click.argument("test_id", type=str, nargs=1, default="latest")
@click.option("--validate/--no-validate", default=True)
def reproduce(pipeline_id, production_name, job_name, test_id, validate):
    """Reproduce an existing online test locally"""
    if validate:
        validate_environment()
    enter_debugging(*prepare_reproduce(pipeline_id, production_name, job_name, test_id))


@main.command()
@click.argument("log_fn", type=click.Path(exists=True))
@click.option(
    "--suppress",
    type=int,
    default=5,
    show_default=True,
    help="Minimum number of instances required to show ERROR and WARNING messages",
)
def parse_log(log_fn, suppress):
    """Read a Gaudi log file and extract information"""
    with open(log_fn, "rt") as fp:
        log_text = fp.read()

    click.echo(f"Summary of log messages in: {log_fn}")
    show_log_advice(log_text, suppress)
